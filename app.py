from config import apikey
import streamlit as st
import requests

st.title('Red Box : Team 114')

uploaded_file = st.file_uploader('Please upload a document')
if uploaded_file is not None:
    file_details = {'name':uploaded_file.name,
                    'type':uploaded_file.type,
                    'size':uploaded_file.size}
    st.write(file_details)
    
    # Send file to Claude API
    api_url = 'https://api.anthropic.com/v1/claude'
    api_key = 'YOUR_API_KEY'
    headers = {'Authorization': f'Bearer {api_key}'}
    files = {'file': uploaded_file.getvalue()}
    res = requests.post(api_url, headers=headers, files=files)

    # Display Claude response
    if res.status_code == 200:
        st.write(res.json())
    else:
        st.error('Error getting Claude response')
