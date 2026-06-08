import io
import os

from gtts import gTTS
from openai import AsyncOpenAI

try:
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize OpenAI client for TTS: {e}")
    openai_client = None


async def generate_speech_stream(text: str, voice: str = "alloy"):
    try:
        tts = gTTS(text=text, lang="en", slow=False)

        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        while True:
            chunk = fp.read(1024 * 4)
            if not chunk:
                break
            yield chunk

    except Exception as e:
        print(f"❌ Error in TTS Generation: {e}")
        raise e


# async def generate_speech_stream(text: str, voice: str = "alloy"):

#     if not openai_client:
#         raise RuntimeError("OpenAI client is not initialized. Check your API Key.")

#     try:
#         response = await openai_client.audio.speech.create(
#             model="tts-1", voice=voice, input=text, response_format="mp3"
#         )

#         async for chunk in response.iter_bytex(chunk_size=1024):
#             yield chunk

#     except Exception as e:
#         print(f"❌ Error in TTS Generation: {e}")
#         raise e
