import random
import asyncio
import edge_tts
import os
from playsound import playsound
from pydub import AudioSegment, effects
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")

# Convert text to audio file
async def TextToAudioFile(text, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        os.remove(file_path)

    # TTS conversion
    communicate = edge_tts.Communicate(
        text,
        AssistantVoice,
        pitch='+9Hz',
        rate='+13%'
    )
    await communicate.save(file_path)

    # Apply Jarvis-style effect (normalize + light echo)
    try:
        sound = AudioSegment.from_file(file_path, format="mp3")
        sound = effects.normalize(sound)   # smooth volume

        # Create delayed version for echo
        delay_ms = 100
        silent = AudioSegment.silent(duration=delay_ms)
        delayed = silent + (sound - 6)

        # Mix original + delayed
        echo = sound.overlay(delayed)
        echo.export(file_path, format="mp3")
    except Exception as e:
        print(f"Effect error: {e}")

# Play TTS
def TTS(Text, func=lambda r=None: True):
    file_path = r"Data\speech.mp3"
    try:
        asyncio.run(TextToAudioFile(Text, file_path))

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TTS file not created: {file_path}")

        playsound(file_path)  # simple playback

        func(True)
        return True

    except Exception as e:
        print(f"error in TTS: {e}")
        func(False)
        return False

# Handle long text
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))