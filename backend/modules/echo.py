import speech_recognition as sr
import pyttsx3


class Echo:

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty("rate", 150)
        self.tts_engine.setProperty("volume", 1.0)

    def start(self):
        print("[ECHO] Loading...")
        print("✅ Voice Module Ready")
        print()
        print("🎤 Echo Online")

    def listen(self):
        try:
            with sr.Microphone() as source:
                print("[ECHO] Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source)

            command = self.recognizer.recognize_google(audio)
            print(f"🎙️ Heard: {command}")
            return command
        except sr.UnknownValueError:
            print("[ECHO] Sorry, I could not understand the speech.")
            return None
        except sr.RequestError as error:
            print(f"[ECHO] Speech recognition service error: {error}")
            return None
        except OSError as error:
            print(f"[ECHO] Microphone error: {error}")
            print("[ECHO] Please ensure a microphone is connected and accessible.")
            return None

    def speak(self, message):
        print(f"[ECHO] Speaking: {message}")
        self.tts_engine.say(message)
        self.tts_engine.runAndWait()