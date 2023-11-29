#!/usr/bin/env python3

import openai
import redis
import os
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

api_key = os.getenv("API_KEY")


# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

print(os.getenv("OPENAI_API_KEY"))

# Function to get data from Redis
def get_data_from_redis(list_name):
    return redis_client.lrange(list_name, 0, -1)

# Function to create a question from the data
def create_question(data):
    # Example logic to create a question
    return f"What can be inferred from this data: {data}?"

# Function to ask a question using OpenAI API
def ask_openai(question):
    MODEL = "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Knock knock."},
            {"role": "assistant", "content": "Who's there?"},
            {"role": "user", "content": "Orange."},
        ],
        temperature=0,
    )

    return response

def main():
    list_name = "transcription"
    data = get_data_from_redis(list_name)
    if data:
        # Decode each byte string in the list to a regular string
        decoded_data = [item.decode('utf-8') for item in data]
        response = ask_openai("What is 4 * 4?")
        print("Response from OpenAI:", response)
        print(decoded_data)
    else:
        print("No data found in Redis.")

if __name__ == "__main__":
    main()
