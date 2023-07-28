import anthropic

# project
import claude_retriever
from claude_retriever.searcher.searchtools.websearch import BraveSearchTool
from config import ANTHROPIC_API_KEY, BRAVE_API_KEY, ANTHROPIC_SEARCH_MODEL
from prompt import prompt
from sample_doc import document



def generate_user_output(document, task):

    brave_search_tool = BraveSearchTool(brave_api_key=BRAVE_API_KEY, summarize_with_claude=True, anthropic_api_key=ANTHROPIC_API_KEY)

    client = claude_retriever.ClientWithRetrieval(api_key=ANTHROPIC_API_KEY, search_tool = brave_search_tool)

    retrieval_prompt = f'''{anthropic.HUMAN_PROMPT} Here is a document shared by a user for which you will write a response about:

    <document>{document}</document>

    Using key words from the document, please find the top 5 news articles relating to the policy area discussed in the document. Follow these rules:
    - Only use news articles from the last month 
    - Prioritise national news websites, such as BBC, The Times, The Guardian, The Telegraph
    - Do not use questions in the searches, only keywords
    {anthropic.AI_PROMPT}'''


    # - Include a mix of recent government announcements and non-government announcements where possible.

    relevant_search_results  = client.retrieve(
        prompt=retrieval_prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT, "END_OF_SEARCH"],
        model=ANTHROPIC_SEARCH_MODEL,
        n_search_results_to_use=2, # Use only the top search result, so Claude can adapt queries quickly
        max_searches_to_try=3, # Reducing this number will make the search process faster, but less likely to get the best results
        max_tokens_to_sample=1000)

    # print('search results:')
    # print(relevant_search_results)

    qa_prompt = f'''{anthropic.HUMAN_PROMPT} 

    <task>{task}<task>

    Here is the document for which you will write your response about:

    <document>{document}</document>

    Here are a set of recent news article search results that will be helpful. 
    <new_results>{relevant_search_results}</news_results>
    Only use the news_results search results to inform the 'Latest news' section. Do not include articles published over 1 year ago or that are not related to the policy area in the document. 
    Always include website links of news articles where they are referenced.:
    If there are no relevant articles from the last month, say so.

    Once again, here is the main task:
    <task>{task}<task>

    And here is the user's document:
    <document>{document}</document>


    Only return the response to the task given the document provided. There will be no follow up. Your response to the task:
    {anthropic.AI_PROMPT}''' # It is best to put the query before and after the search results.

    response = client.completions.create(
        prompt=qa_prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT],
        model=ANTHROPIC_SEARCH_MODEL,
        max_tokens_to_sample=1000,
    )


    return print(response.completion)


generate_user_output(document, task=prompt)



