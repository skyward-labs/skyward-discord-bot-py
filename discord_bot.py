import os
import discord
import openai
import re
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("openai_key")
openai.api_type = os.getenv("openai_type")
openai.api_base = os.getenv("openai_base")
openai.api_version = "2023-03-15-preview"

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        user_message = message.content.replace(f'<@!{client.user.id}>', '').strip()

        response = openai.ChatCompletion.create(
            engine="gpt-4-32k",
            messages=[
                {"role": "system", "content": "You are a software engineer."},
                {"role": "user", "content": user_message},
            ],
        )

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

        # Send the split answer parts to the Discord channel
        for part in split_answer_parts:
            await message.channel.send(part)


client.run(os.getenv("discord_token"))