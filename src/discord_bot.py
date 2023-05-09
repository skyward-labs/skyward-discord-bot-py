import os
import discord
import re
from gpt import request_openai_gpt4
from collections import deque
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)

converstion_limit: int = 8
channels = {}


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith("!gpt"):
        async with message.channel.typing():
            user_message = message.content.replace(f"!gpt", "").strip()

            messages = append_message_to_channel(message.channel.id, {"role": "user", "content": user_message})

            answer = request_openai_gpt4(messages)

            append_message_to_channel(message.channel.id, {"role": "assistant", "content": answer})

        for part in generate_answer_parts(answer):
            await message.channel.send(part)


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


def append_message_to_channel(channel_id, message):
    if (channel_id not in channels):
        channels[channel_id] = deque(maxlen=converstion_limit)
        channels[channel_id].append({"role": "system", "content": "You are a software engineer."})

    channels[channel_id].append(message)
    return channels[channel_id]


def run_bot():
    client.run(os.getenv("discord_token"))
