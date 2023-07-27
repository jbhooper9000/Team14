from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
# import dotenv
import os
from config import ANTHROPIC_API_KEY

# project
from prompt import prompt
import streamlit as st
from PyPDF2 import PdfFileReader

st.title('Red Box : Team 14')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    pdf_reader = PdfFileReader(uploaded_file)
    page_count = pdf_reader.getNumPages()
    text = ""
    for i in range(page_count):
        page = pdf_reader.getPage(i)
        text += page.extractText()

    document = text
    prompt_text = prompt
    anthropic = Anthropic(
        api_key=ANTHROPIC_API_KEY
    )

    prompt = f"{HUMAN_PROMPT}" + prompt_text + document + f"{AI_PROMPT}"

    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=300,
        prompt=prompt,
    )


    st.write(completion.completion)