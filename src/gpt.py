import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("openai_api_key")
openai.api_base = os.getenv("openai_api_base")
openai.api_type = os.getenv("openai_api_type")
openai.api_version = os.getenv("openai_api_version")


def request_openai_gpt4(messages):
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-4-32k",
            temperature=0.5,
            max_tokens=24634,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            messages=[*messages],
        )

        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
        return "An excpetion occured."
