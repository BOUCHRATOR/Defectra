from services.tts_service import TTSService


service = TTSService()


text = """
La fissure détectée est un défaut grave.

Vous devriez consulter un mécanicien professionnel dès que possible.
"""


audio_path = service.synthesize(
    text,
    "test_response.mp3"
)


print("Audio generated:")
print(audio_path)