# This script loads txt documents from a `data` folder in your working directory and indexes all .txt files inside this folder
# It accepts a prompt as the first argument and prints a response

import os
import sys

from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.llms import openai
from langchain.chat_models import ChatOpenAI

API_KEY = os.environ['OPENAI_API_KEY']

query = sys.argv[1]

#loader = TextLoader('data.txt')
loader = DirectoryLoader(".",glob="*.txt")
index = VectorstoreIndexCreator().from_loaders([loader])
result = index.query(query,llm=ChatOpenAI())
print(result)
