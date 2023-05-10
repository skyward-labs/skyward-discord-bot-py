from collections import deque

converstion_limit: int = 8
channels = {}


def append_message_to_channel(channel_id, message):
    if channel_id not in channels:
        channels[channel_id] = deque(maxlen=converstion_limit)
        channels[channel_id].append(
            {"role": "system", "content": "You are a software engineer."}
        )

    channels[channel_id].append(message)
    return channels[channel_id]
