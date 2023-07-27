from typing import Tuple
from anthropic import Anthropic, HUMAN_PROMPT
from .searcher.types import SearchTool, SearchResult
from .utils import get_search_starting_prompt, extract_search_query, deduplicate_search_results
import logging

logger = logging.getLogger(__name__)

class ClientWithRetrieval(Anthropic):

    def __init__(self, search_tool: SearchTool, verbose: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_tool = search_tool
        self.verbose = verbose

    # Helper methods

    def _get_partial_completion(self,
                                prompt: str,
                                model: str,
                                stop_sequences: list[str] = [HUMAN_PROMPT],
                                max_tokens_to_sample: int = 1000,
                                temperature: float = 1.0) -> Tuple[str, str, str]:
        if self.verbose:
            logger.info(f'Issuing the following prompt to Claude:\n\n' + '-'*50 + f'\n\n{prompt}\n\n'+'-'*50+'\n\n')

        partial_completion = self.completions.create(prompt = prompt,
                                                     stop_sequences=stop_sequences + ['</search_query>'],
                                                     model=model,
                                                     max_tokens_to_sample = max_tokens_to_sample,
                                                     temperature = temperature)

        return partial_completion.completion, partial_completion.stop_reason, partial_completion.stop
        

    def _search_query_stop(self, partial_completion: str, n_search_results_to_use: int) -> Tuple[list[SearchResult], str]:
        search_query = extract_search_query(partial_completion + '</search_query>')
        if search_query is None:
            raise Exception(f'Completion with retrieval failed as partial completion returned mismatched <search_query> tags.')
        if self.verbose:
            logger.info('\n'+'-'*20 + f'\nPausing stream because Claude has issued a query in <search_query> tags: <search_query>{search_query}</search_query>\n' + '-'*20)
        logger.info(f'Running search query against SearchTool: {search_query}')
        search_results = self.search_tool.raw_search(search_query, n_search_results_to_use)
        extracted_search_results = self.search_tool.process_raw_search_results(search_results)
        formatted_search_results = self.search_tool.format_full(extracted_search_results)
        if self.verbose:
            logger.info('\n' + '-'*20 + f'\nThe SearchTool has returned the following search results:\n\n{formatted_search_results}\n\n' + '-'*20 + '\n')

        return search_results, formatted_search_results

    def _retrieve(self,
                       prompt: str,
                       model: str,
                       n_search_results_to_use: int = 3,
                       stop_sequences: list[str] = [HUMAN_PROMPT],
                       max_tokens_to_sample: int = 1000,
                       max_searches_to_try: int = 5,
                       temperature: float = 1.0) -> tuple[list[SearchResult], str]:
        
        prompt = get_search_starting_prompt(raw_prompt = prompt, search_tool = self.search_tool)
        starting_prompt = prompt
        token_budget = max_tokens_to_sample
        tries = 0
        all_raw_search_results: list[SearchResult] = []
        while True:
            if tries >= max_searches_to_try:
                logger.warning(f'max_searches_to_try ({max_searches_to_try}) exceeded.')
                break
            partial_completion, stop_reason, stop_seq = self._get_partial_completion(prompt, model=model,
                                                                                     stop_sequences=stop_sequences,
                                                                                     max_tokens_to_sample=token_budget,
                                                                                     temperature=temperature)
            tries += 1
            partial_completion_tokens = self.count_tokens(partial_completion)
            token_budget -= partial_completion_tokens
            prompt += partial_completion
            if stop_reason == 'stop_sequence' and stop_seq == '</search_query>':
                logger.info(f'Attempting search number {tries}.')
                raw_search_results, formatted_search_results = self._search_query_stop(partial_completion, n_search_results_to_use)
                prompt += '</search_query>' + formatted_search_results
                all_raw_search_results += raw_search_results
            else:
                break
        final_model_response = prompt[len(starting_prompt):]
        return all_raw_search_results, final_model_response
    
    # Main methods

    def completion_with_retrieval(self,
                                        prompt: str,
                                        model: str,
                                        n_search_results_to_use: int = 3,
                                        stop_sequences: list[str] = [HUMAN_PROMPT],
                                        max_tokens_to_sample: int = 1000,
                                        max_searches_to_try: int = 5,
                                        temperature: float = 1.0) -> str:
        
        _, final_model_response = self._retrieve(prompt, model=model,
                                                 n_search_results_to_use=n_search_results_to_use, stop_sequences=stop_sequences,
                                                 max_tokens_to_sample=max_tokens_to_sample,
                                                 max_searches_to_try=max_searches_to_try,
                                                 temperature=temperature)
        return final_model_response
    
    def retrieve(self,
                       prompt: str,
                       model: str,
                       n_search_results_to_use: int = 3,
                       stop_sequences: list[str] = [HUMAN_PROMPT],
                       max_tokens_to_sample: int = 1000,
                       max_searches_to_try: int = 5,
                       temperature: float = 1.0) -> str:
        
        raw_search_results, _ = self._retrieve(prompt, model=model,
                                               n_search_results_to_use=n_search_results_to_use,
                                               stop_sequences=stop_sequences, max_tokens_to_sample=max_tokens_to_sample,
                                               max_searches_to_try=max_searches_to_try,
                                               temperature=temperature)
        deduplicated_search_results = deduplicate_search_results(raw_search_results)
        extracted_search_results = self.search_tool.process_raw_search_results(deduplicated_search_results)
        formatted_search_results = self.search_tool.format_full(extracted_search_results)
        return formatted_search_results
