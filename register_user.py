"""Register one authorized speaker for the safe demo."""
from modules.audio_processor import AudioProcessor
from modules.voice_recognizer import VoiceRecognizer
from modules.database import DatabaseManager


def main():
    name = input("اكتب اسم المستخدم: ").strip()
    if not name:
        print("❌ الاسم مطلوب")
        return

    audio = AudioProcessor().record_audio(duration=6)
    if audio is None:
        return

    recognizer = VoiceRecognizer()
    embedding = recognizer.register_voice(name, audio)
    if embedding is None:
        return

    with DatabaseManager() as db:
        if db.register_user(name, embedding) is None:
            return

    print(f"✅ تم تسجيل صوت {name} بنجاح")


if __name__ == "__main__":
    main()
