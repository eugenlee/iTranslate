# pip install assemblyai requests gTTS pygame python-dotenv

import assemblyai as aai
import requests
import os
import io
import pygame
from gtts import gTTS
from dotenv import load_dotenv
from assemblyai.streaming.v3 import (
    StreamingClient,
    StreamingClientOptions,
    StreamingParameters,
    StreamingEvents,
    StreamingError,
    SpeechModel,
    TurnEvent,
    BeginEvent,
    TerminationEvent,
)

load_dotenv()

# Supported source languages for u3-rt-pro: en, es, de, fr, pt, it
SOURCE_LANG = 'en'
TARGET_LANG = 'ja'  # can be any DeepL-supported language

PROMPTS = {
    'en': 'Transcribe English.',
    'es': 'Transcribe Spanish.',
    'de': 'Transcribe German.',
    'fr': 'Transcribe French.',
    'pt': 'Transcribe Portuguese.',
    'it': 'Transcribe Italian.',
}

pygame.mixer.init()

is_playing = False


def translate(text: str, target: str) -> str:
    r = requests.post(
        'https://api-free.deepl.com/v2/translate',
        headers={'Authorization': f'DeepL-Auth-Key {os.environ["DEEPL_API_KEY"]}'},
        json={'text': [text], 'target_lang': target.upper()},
    )
    return r.json()['translations'][0]['text']


def play_tts(text: str, lang: str = 'ja'):
    global is_playing
    is_playing = True
    tts = gTTS(text=text, lang=lang)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    pygame.mixer.music.load(audio_fp, 'mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    is_playing = False


def on_begin(client: StreamingClient, event: BeginEvent):
    print(f'[session] {event.id}')
    print('Recording... (Ctrl+C to stop)')


def on_turn(client: StreamingClient, event: TurnEvent):
    if not event.transcript or is_playing:
        return
    if event.end_of_turn:
        print(f'\n[final] {event.transcript}')
        translated = translate(event.transcript, TARGET_LANG)
        print(f'[translated] {translated}')
        play_tts(translated, lang=TARGET_LANG)
    else:
        print(f'\r{event.transcript}', end='', flush=True)


def on_terminated(client: StreamingClient, event: TerminationEvent):
    print(f'\n[closed] {event.audio_duration_seconds:.1f}s transcribed')


def on_error(client: StreamingClient, error: StreamingError):
    print(f'[error] {error}')


client = StreamingClient(
    StreamingClientOptions(
        api_key=os.environ['ASSEMBLYAI_API_KEY'],
        api_host='streaming.assemblyai.com',
    )
)

client.on(StreamingEvents.Begin, on_begin)
client.on(StreamingEvents.Turn, on_turn)
client.on(StreamingEvents.Termination, on_terminated)
client.on(StreamingEvents.Error, on_error)

client.connect(
    StreamingParameters(
        sample_rate=16_000,
        speech_model=SpeechModel.u3_rt_pro,
        prompt=PROMPTS[SOURCE_LANG],
        format_turns=True,
        min_turn_silence=400,
        max_turn_silence=1500,
    )
)

try:
    client.stream(aai.extras.MicrophoneStream(sample_rate=16_000))
finally:
    client.disconnect(terminate=True)
