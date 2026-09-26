"""Safe voice assistant demo. It never sends commands to a drone."""
from modules.audio_processor import AudioProcessor
from modules.voice_recognizer import VoiceRecognizer
from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.command_parser import CommandParser
from modules.database import DatabaseManager

WAKE_WORDS = ("يا صلاح", "صلاح", "hello salah", "hey salah")


def response_for(command, user_name):
    action = command["action"]
    if action == "HELLO":
        return f"أهلاً يا {user_name}"
    if action == "STATUS":
        return "النظام يعمل. هذه نسخة تجريبية ولا يوجد تحكم في الدرون."
    if action == "HELP":
        return "الأوامر المتاحة: الحالة، مرحبا، مساعدة، معلومات، توقف"
    if action == "INFO":
        return "أنا صلاح، مساعد صوتي تجريبي بدون أوامر طيران."
    if action == "STOP":
        return "تم التوقف عن الاستماع للأمر الحالي."
    return "لم أفهم الأمر"


def main():
    audio = AudioProcessor()
    stt = SpeechToText(model_size="tiny", language="ar")
    tts = TextToSpeech(language="ar")
    parser = CommandParser()
    recognizer = VoiceRecognizer(similarity_threshold=0.70)

    with DatabaseManager() as db:
        users = db.get_all_users()
        if not users:
            print("❌ لا يوجد مستخدم مسجل. شغّل: python register_user.py")
            return
        recognizer.load_voices({u["name"]: u["voice_embedding"] for u in users})

        print("✅ صلاح جاهز. قل: يا صلاح. اضغط Ctrl+C للخروج.")
        try:
            while True:
                wake_audio = audio.record_audio(duration=3)
                if wake_audio is None:
                    continue
                wake_text = stt.transcribe(wake_audio)
                if not wake_text or not any(word in wake_text.lower() for word in WAKE_WORDS):
                    continue

                tts.speak("أنا سامعك")
                command_audio = audio.record_audio(duration=5)
                if command_audio is None:
                    continue

                user, score = recognizer.identify_speaker(command_audio)
                if user is None:
                    tts.speak("عذراً، الصوت غير مصرح له")
                    continue

                text = stt.transcribe(command_audio)
                command = parser.parse(text)
                if command is None:
                    tts.speak("لم أفهم الأمر")
                    continue

                reply = response_for(command, user)
                db.log_command(db.get_user_by_name(user)["id"], command["action"], True, reply)
                tts.speak(reply)
                print(f"✅ {user}: {text} -> {command['action']}")
        except KeyboardInterrupt:
            print("\nتم إيقاف البرنامج")


if __name__ == "__main__":
    main()
