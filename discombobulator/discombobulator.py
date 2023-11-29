import openai
import redis
import os
import json

# Function to load environment variables from a file
def load_env():
    with open('env', 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            if key == 'OPENAI_KEY':
                os.environ['OPENAI_API_KEY'] = value



load_env()

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
    response = openai.Completion.create(
        engine="davinci",
        prompt=question,
        max_tokens=50
    )
    return response.choices[0].text.strip()

def main():
    list_name = "transcription"
    data = get_data_from_redis(list_name)
    if data:
        # Decode each byte string in the list to a regular string
        decoded_data = [item.decode('utf-8') for item in data]
        print(decoded_data)
    else:
        print("No data found in Redis.")

if __name__ == "__main__":
    main()
