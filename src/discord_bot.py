import discord
import azure.cognitiveservices.speech as speechsdk

from os import getenv
from gpt4 import request_openai_gpt4
from gpt35 import request_openai_gpt35
from discord.ext import commands
from utils.append_message_to_channel import append_message_to_channel
from utils.generate_answer_parts import generate_answer_parts
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
prefix = getenv("discord_prefix", default="!gpt")

speech_config = speechsdk.SpeechConfig(
    subscription=getenv("speech_key"), region=getenv("speech_region")
)
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

speech_config.speech_recognition_language = "en-US"
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config, audio_config=audio_config
)

speech_config.speech_synthesis_voice_name = "en-US-JennyMultilingualNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_output_config
)


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

    while True:
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if speech_recognition_result.text == "Stop.":
                break

            messages = append_message_to_channel(
                ctx.message.channel.id,
                {"role": "user", "content": speech_recognition_result.text},
            )

            answer = request_openai_gpt35(messages)

            append_message_to_channel(
                ctx.message.channel.id, {"role": "assistant", "content": answer}
            )

            speech_synthesizer.speak_text_async(answer).get()


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


def run_bot():
    client.run(getenv("discord_token"))
