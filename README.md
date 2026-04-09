# iTranslate

Real-time speech translation. Listens to your microphone, transcribes what you say, translates it, and reads the translation aloud.

**Pipeline:** Microphone → AssemblyAI (speech-to-text) → DeepL (translation) → gTTS (text-to-speech)

> **Note:** gTTS is used here for demo purposes only. For production use cases, a dedicated TTS API service is recommended — such as [ElevenLabs](https://elevenlabs.io/) or [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech) — for better voice quality, lower latency, and reliability.

## Requirements

- Python 3.8+
- [AssemblyAI API key](https://www.assemblyai.com/)
- [DeepL API key](https://www.deepl.com/pro-api) (free tier works)

## Setup

```bash
pip install assemblyai requests gTTS pygame python-dotenv
```

Create a `.env` file in the project root:

```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
DEEPL_API_KEY=your_deepl_api_key_here
```

## Usage

```bash
python main.py
```

Speak into your microphone. After each sentence, the translation will be printed and played aloud. Press `Ctrl+C` to stop.

## Configuration

At the top of `main.py`:

```python
SOURCE_LANG = 'en'  # language you're speaking
TARGET_LANG = 'ja'  # language to translate into
```

**Supported source languages** (AssemblyAI `u3-rt-pro` model): `en`, `es`, `de`, `fr`, `pt`, `it`

**Supported target languages**: any language supported by DeepL — see [DeepL docs](https://developers.deepl.com/docs/resources/supported-languages) for the full list.
