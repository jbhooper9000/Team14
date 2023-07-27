from typing import Optional
from claude_retriever.searcher.types import SearchResult, SearchTool
from anthropic import Anthropic
import wikipedia
from dataclasses import dataclass

import logging
logger = logging.getLogger(__name__)

# Wikipedia Searcher

WIKIPEDIA_DESCRIPTION = 'The search engine will exclusively search over Wikipedia for pages with keywords similar to your query. It returns for each page its title and full page content. Use this tool if you want to get up-to-date and comprehensive information on a topic to help answer queries.'

@dataclass
class WikipediaSearchResult(SearchResult):
    title: str
    
class WikipediaSearchTool(SearchTool):

    def __init__(self,
                 tool_description: str = WIKIPEDIA_DESCRIPTION,
                 truncate_to_n_tokens: Optional[int] = 5000):
        self.tool_description = tool_description
        self.truncate_to_n_tokens = truncate_to_n_tokens
        if truncate_to_n_tokens is not None:
            self.tokenizer = Anthropic().get_tokenizer()

    def raw_search(self, query: str, n_search_results_to_use: int) -> list[WikipediaSearchResult]:
        search_results = self._search(query, n_search_results_to_use)
        return search_results
    
    def process_raw_search_results(self, results: list[WikipediaSearchResult]) -> list[str]:
        processed_search_results = [f'Page Title: {result.title.strip()}\nPage Content:\n{self.truncate_page_content(result.content)}' for result in results]
        return processed_search_results

    def truncate_page_content(self, page_content: str) -> str:
        if self.truncate_to_n_tokens is None:
            return page_content.strip()
        else:
            return self.tokenizer.decode(self.tokenizer.encode(page_content).ids[:self.truncate_to_n_tokens]).strip()
        
    def _search(self, query: str, n_search_results_to_use: int) -> list[WikipediaSearchResult]:
        results: list[str] = wikipedia.search(query)
        search_results: list[WikipediaSearchResult] = []
        for result in results:
            if len(search_results) >= n_search_results_to_use:
                break
            try:
                page = wikipedia.page(result)
            except:
                # The Wikipedia API is a little flaky, so we just skip over pages that fail to load
                continue
            content = page.content
            title = page.title
            search_results.append(WikipediaSearchResult(content=content, title=title))
        return search_results
