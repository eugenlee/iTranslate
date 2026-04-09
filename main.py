# pip install assemblyai requests gTTS pygame

import assemblyai as aai
import requests
import os
import io
import pygame
from gtts import gTTS

aai.settings.api_key = os.environ['ASSEMBLYAI_API_KEY']

TARGET_LANG = 'ja'  # translate everything to Japanese

pygame.mixer.init()


def translate(text: str, target: str) -> str:
    r = requests.post(
        'https://api-free.deepl.com/v2/translate',
        data={
            'auth_key': os.environ['DEEPL_API_KEY'],
            'text': text,
            'target_lang': target.upper(),
        },
    )
    return r.json()['translations'][0]['text']


def play_tts(text: str, lang: str = 'ja'):
    tts = gTTS(text=text, lang=lang)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    pygame.mixer.music.load(audio_fp, 'mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(f'\n[final] {transcript.text}')
        translated = translate(transcript.text, TARGET_LANG)
        print(f'[translated] {translated}')
        play_tts(translated, lang=TARGET_LANG)
    else:
        print(f'\r{transcript.text}', end='', flush=True)


transcriber = aai.RealtimeTranscriber(
    sample_rate=16_000,
    on_data=on_data,
    on_error=lambda e: print(f'[error] {e}'),
    on_close=lambda: print('\n[closed]'),
    speech_model='u3-rt-pro',
    prompt='Transcribe English.',
    min_turn_silence=400,
    max_turn_silence=1500,
)

transcriber.connect()
transcriber.stream(aai.extras.MicrophoneStream(16_000))
transcriber.close()
