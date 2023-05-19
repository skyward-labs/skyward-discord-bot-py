import discord

from os import getenv
from gpt import request_openai_gpt4
from discord.ext import commands
from utils.append_message_to_channel import append_message_to_channel
from utils.generate_answer_parts import generate_answer_parts
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
prefix = getenv("discord_prefix", default="!gpt")


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.command()
async def gpt(ctx):
    if ctx.message.author == client.user:
        return

    async with ctx.message.channel.typing():
        user_message = ctx.message.content.replace(prefix, "").strip()

        messages = append_message_to_channel(
            ctx.message.channel.id, {"role": "user", "content": user_message}
        )

        answer = request_openai_gpt4(messages)

        append_message_to_channel(
            ctx.message.channel.id, {"role": "assistant", "content": answer}
        )

    for part in generate_answer_parts(answer):
        await ctx.message.channel.send(part)


@client.command()
async def join(ctx):
    author = ctx.message.author
    channel = author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


def run_bot():
    client.run(getenv("discord_token"))
