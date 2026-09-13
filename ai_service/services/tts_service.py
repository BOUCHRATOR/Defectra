from gtts import gTTS
import os


class TTSService:

    def __init__(self):

        self.output_dir = "audio"

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )


    def synthesize(
        self,
        text,
        filename="response.mp3"
    ):

        output_path = os.path.join(
            self.output_dir,
            filename
        )

        tts = gTTS(
            text=text,
            lang="fr"
        )

        tts.save(
            output_path
        )

        return output_path