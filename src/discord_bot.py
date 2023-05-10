import discord

from os import getenv
from gpt import request_openai_gpt4
from utils.append_message_to_channel import append_message_to_channel
from utils.generate_answer_parts import generate_answer_parts
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
client = discord.Client(command_prefix="!", intents=intents)
prefix = getenv("discord_prefix")


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        async with message.channel.typing():
            user_message = message.content.replace(prefix, "").strip()

            messages = append_message_to_channel(
                message.channel.id, {"role": "user", "content": user_message}
            )

            answer = request_openai_gpt4(messages)

            append_message_to_channel(
                message.channel.id, {"role": "assistant", "content": answer}
            )

        for part in generate_answer_parts(answer):
            await message.channel.send(part)


def run_bot():
    client.run(getenv("discord_token"))
