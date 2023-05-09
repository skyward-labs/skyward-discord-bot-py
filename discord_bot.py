import os
import discord
import openai
import re
from collections import deque
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("openai_api_key")
openai.api_base = os.getenv("openai_api_base")
openai.api_type = os.getenv("openai_api_type")
openai.api_version = os.getenv("openai_api_version")

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)

converstion_limit: int = 8
messages = deque(maxlen=converstion_limit)
messages.append({"role": "system", "content": "You are a software engineer."})


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!gpt"):
        async with message.channel.typing():
            user_message = message.content.replace(f"!gpt", "").strip()

            messages.append({"role": "user", "content": user_message})

            answer = request_openai_gpt4(messages)

            messages.append({"role": "assistant", "content": answer})

        for part in generate_answer_parts(answer):
            await message.channel.send(part)


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
    except:
        return f"An exception has occured."


def generate_answer_parts(answer):
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
