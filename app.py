from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import streamlit as st
from PyPDF2 import PdfFileReader

# project
from prompt import prompt
from config import ANTHROPIC_API_KEY


st.title('Red Box : Team 114')

uploaded_file = st.file_uploader('Please upload a document')
if uploaded_file is not None:
    pdf_reader = PdfFileReader(uploaded_file)
    page_count = pdf_reader.getNumPages()
    document_text = ""
    for i in range(page_count):
        page = pdf_reader.getPage(i)
        document_text += page.extractText()


    prompt_text = prompt

    claude_query = f"{HUMAN_PROMPT}" + prompt_text + document_text + f"{AI_PROMPT}"

    anthropic = Anthropic(
        api_key=ANTHROPIC_API_KEY
    )

    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=300,
        prompt=claude_query,
    )


    st.write(completion.completion)
