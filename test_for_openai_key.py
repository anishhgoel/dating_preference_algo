import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# Initialize the client with your API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    # Call the completions endpoint using the new syntax
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ]
    )
    print("OpenAI API Key works! Response:", response.choices[0].message.content)
except Exception as e:
    print("Failed to connect to OpenAI API. Check your API key.")
    print(e)