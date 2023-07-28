from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import streamlit as st
from PyPDF2 import PdfFileReader

# project
from prompt import prompt
from config import ANTHROPIC_API_KEY

st.title('Red Box :toolbox: : Team 14')
st.subheader('This tool is design to help summarise documents. It may take a minute to load, but will save you hours.')


uploaded_file = st.file_uploader('Please upload a document')
with st.spinner(text='In progress...'):
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

        print(str(completion.completion))
        st.write(completion.completion)


hide_style = """
        <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_style, unsafe_allow_html=True)