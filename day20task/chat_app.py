import os
from dotenv import load_dotenv
import streamlit as st
from openai import AzureOpenAI
 
# Load environment variables
load_dotenv()
 
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
MODEL_NAME = os.getenv("MODEL_NAME")
 
# Create Azure OpenAI client
client = AzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version="2025-01-01-preview"
)

user_input = st.text_input("Ask Anything")

if st.button("Send"):
    if user_input.strip():
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )
 
            st.success(response.choices[0].message.content)
 
        except Exception as e:
            st.error(str(e))