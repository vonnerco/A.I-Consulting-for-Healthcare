import whisper
from elevenlabs import generate, play

class VoiceProcessor:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
    
    def speech_to_text(self, audio_file: str) -> str:
        result = self.whisper_model.transcribe(audio_file)
        return result["text"]
    
    def text_to_speech(self, text: str, voice: str = "default"):
        audio = generate(text=text, voice=voice)
        return audio
