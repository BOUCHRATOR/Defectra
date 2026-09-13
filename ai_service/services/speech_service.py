import whisper


class SpeechService:

    def __init__(self):

        print("Loading Whisper model...")

        self.model = whisper.load_model("base")

        print("Whisper model loaded.")

    def transcribe(self, audio_path):

        result = self.model.transcribe(
            audio_path,
            language="fr"
        )

        return result["text"]