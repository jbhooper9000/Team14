from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
# import dotenv
import os
from config import ANTHROPIC_API_KEY

# project
from prompt import prompt
document = "user document text imported from frontend"
prompt_text = "You are responsible for summarising important documents for a CEO. Time is tight, so you need to pick the most important points, and raise anything that may be problematic. Please summarise the report below by pulling out the key themes in 5 bullet points. Please also point out if it does not align with the Conservative manifesto pledges, and if any themes in the document have been in the news recently. Also flag if the document would also be relevant for another UK government department"

anthropic = Anthropic(
    api_key=ANTHROPIC_API_KEY
)


prompt = f"{HUMAN_PROMPT}" + prompt_text + document + f"{AI_PROMPT}"

completion = anthropic.completions.create(
    model="claude-2",
    max_tokens_to_sample=300,
    prompt=prompt,
)


print(completion.completion)