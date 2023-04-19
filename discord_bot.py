import os
import discord
import openai
import re
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("openai_api_key")
openai.api_base = os.getenv("openai_api_base")
openai.api_type = os.getenv("openai_api_type")
openai.api_version = os.getenv("openai_api_version")

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!gpt3"):
        response = request_openai_gpt3(message)
        split_answer_parts = generate_answer_parts(response)

        for part in split_answer_parts:
            await message.channel.send(part)

    if message.content.startswith("!gpt4"):
        response = request_openai_gpt4(message)
        split_answer_parts = generate_answer_parts(response)

        for part in split_answer_parts:
            await message.channel.send(part)


def request_openai_gpt3(message):
    user_message = message.content.replace(f"!gpt3", "").strip()

    return openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=[
            {"role": "system", "content": "You are a software engineer."},
            {"role": "user", "content": user_message},
        ],
    )


def request_openai_gpt4(message):
    user_message = message.content.replace(f"!gpt4", "").strip()

    return openai.ChatCompletion.create(
        engine="gpt-4-32k",
        messages=[
            {"role": "system", "content": "You are a software engineer."},
            {"role": "user", "content": user_message},
        ],
    )


def generate_answer_parts(response):
    # Extract the answer from the API response
    answer = response["choices"][0]["message"]["content"]

    # Separate code snippets from the answer using regex
    code_snippets = re.findall(r"```[\s\S]*?```", answer)
    non_code_parts = re.split(r"```[\s\S]*?```", answer)

    # Combine non-code parts and code snippets into a new list
    answer_parts = []
    for non_code_part, code_snippet in zip(
        non_code_parts,
        code_snippets + [""] * (len(non_code_parts) - len(code_snippets)),
    ):
        if non_code_part.strip():
            answer_parts.append(non_code_part.strip())
        if code_snippet.strip():
            answer_parts.append(code_snippet.strip())

    # Split the answer parts if they exceed the character limit
    max_length = 2000
    split_answer_parts = []
    for part in answer_parts:
        split_answer_parts.extend(
            [part[i : i + max_length] for i in range(0, len(part), max_length)]
        )

    return split_answer_parts


client.run(os.getenv("discord_token"))
