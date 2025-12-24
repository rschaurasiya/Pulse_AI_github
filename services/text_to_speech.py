from gtts import gTTS
import io

def text_to_audio(text, lang='en'):
    """
    Converts text to audio bytes using gTTS.
    """
    try:
        if not text:
            return None
            
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to a bytes buffer
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        return fp
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
