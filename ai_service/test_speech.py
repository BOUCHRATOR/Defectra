from services.speech_service import SpeechService


service = SpeechService()

audio_path = "test_audio.m4a"

text = service.transcribe(audio_path)

print("\n==============================")
print("TRANSCRIPTION")
print("==============================")
print(text)