#!/usr/bin/env python3

import openai
from openai import OpenAI
import redis
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

redis_client = redis.Redis(host='localhost', port=6379, db=0)

key = os.getenv("OPENAI_API_KEY")
openai.api_key = key

client = OpenAI(
    api_key=key,
)

def get_data_from_redis(list_name):
    return redis_client.lrange(list_name, 0, -1)

def ask_openai(transcripts):
    #input = '\n'.join(transcripts[0:5]) # SUBTLE AF BUG, flip the order, time goes forwards
    input = '\n'.join(transcripts[2::-1])


    #print("Input to OpenAI:")
    #print(input)

    prompt = f"""
I am going to present you with a list of five lines of transcriptions at the end of this prompt. There will be a blank newline before that input.
Each transcription is of a 30 second audio clip recorded live off the radio from an alternative rock station.
Each transcription is created from a rolling audio buffer of live audio and is updated every 15 seconds.
This means that each transcription shares a 15 second overlap with the previous transcription.
It's your job to sort out the overlapping text.
I want you to inspect the data and return just what you think the original spoken and sung words and lyrics are.
Input that is highly repetative and does not make sense is probably created from instrumental audio and should be ignored.
Some text will come from the DJ, and it will be recognizable because there are much fewer gramatical and nonsensical errors.
All text is important, but please put "DJ:" in front of sentences by the DJ and put each one on a new line.
Oftentimes, the clip will have started in the middle of a song and there was not an initial DJ introduction.
Please pad the "DJ:" lines with a blank line after they are complete before the song starts.
Words that come from songs will be much more chatoic and nonsensical. Do your best. Use your knowledge of music lyrics to help
you understand and recreate the actual stream of words that were spoken and sung.
If you recognize the song, use that to inform the lyrics you print.
Print out the text of what you think was spoken and sung in the transcriptions and nothing else. 
This last instuction is very important. Nothing else. No commentary.
Also, never include lyrics that you do not see in the text. Do not predict lyrics. Ever!

{input}
"""

    print('===')
    print(input)
    print('===')


    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,

                
                #If you recognize the song, put the song title and artist in parantheses on its own line. 
            }
        ],
        model="gpt-4-1106-preview",
    )

    return chat_completion

def replace_newlines_with_linefeeds(input_string):
    return input_string.replace('\n', '\n')


def main():
    list_name = "transcription"
    data = get_data_from_redis(list_name)
    if data:
        decoded_data = [item.decode('utf-8') for item in data]
        response = ask_openai(decoded_data)
        print(response.choices[0].message.content)
        print('---')
        print()
        print()
    else:
        print("No data found in Redis.")

if __name__ == "__main__":
    main()
