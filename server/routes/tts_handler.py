from gtts import gTTS
import uuid

def synthesize_speech(text, lang='en'):
    filename = f"audio_responses/{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(filename)
    return filename
