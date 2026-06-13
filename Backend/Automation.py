from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import shutil
from googlesearch import search
import pywhatkit as kit
import datetime
import time

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Groq client
client = Groq(api_key=GroqAPIKey)

# Professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service sir, for any additional service or support you may need — don't hesitate to ask."
]

# Messages storage
messages = []

# System chatbot definition (safe fallback for USERNAME)
user_name = os.environ.get("USERNAME", "User")
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {user_name}, You're a content writer. You have to write letters, codes, applications, essays, notes, songs, poems etc."
}]

# Google Search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Content writing
def content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=SystemChatBot + messages[-5:],  # keep last 5 exchanges only
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True
            )
            Answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content
            Answer = Answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": Answer})
            return Answer
        except Exception as e:
            print(f"[red]Error with Groq API:[/red] {e}")
            return "Sorry, I couldn't generate content right now."

    Topic = Topic.replace("content", "").strip()
    ContentByAI = ContentWriterAI(Topic)

    os.makedirs("Data", exist_ok=True)
    filepath = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filepath)
    return True

# YouTube Search
def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Play YouTube video
def PlayYoutube(query):
    playonyt(query)
    return True

# Open App with Chrome fallback
def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"App '{app}' not found locally. Searching online...")
        query = app + " official site"
        try:
            first_link = next(search(query, num=1, stop=1, pause=2))
            print(f"Opening top result: {first_link}")
        except StopIteration:
            print("No search results found.")
            return False

        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            subprocess.Popen([chrome_path, first_link])
        else:
            webbrowser.open(first_link)

        return True

# Close App
def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Error closing {app}:[/red] {e}")
        return False

# ✅ WhatsApp handler
from AppOpener import open as appopen, close as appclose
import os, subprocess, asyncio

# --- WhatsApp Desktop handler ---
def OpenWhatsApp():
    try:
        appopen("whatsapp", match_closest=True, output=True, throw_error=True)
        print("✅ WhatsApp Desktop opened successfully.")
        return True
    except Exception as e:
        print(f"⚠️ AppOpener failed: {e}")
        # fallback: open WhatsApp via full path
        whatsapp_path = r"C:\Users\AMIT PAUL\AppData\Local\WhatsApp\WhatsApp.exe"
        if os.path.exists(whatsapp_path):
            subprocess.Popen([whatsapp_path])
            print("✅ WhatsApp opened via direct path.")
            return True
        else:
            print("❌ WhatsApp not found. Please install it or update the path.")
            return False

def CloseWhatsApp():
    try:
        appclose("whatsapp", match_closest=True, output=True, throw_error=True)
        print("✅ WhatsApp closed.")
        return True
    except Exception as e:
        print(f"⚠️ Could not close WhatsApp: {e}")
        return False



# System Commands
def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume unmute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    if command == "mute": mute()
    elif command == "unmute": unmute()
    elif command == "volume up": volume_up()
    elif command == "volume down": volume_down()
    return True

# Command Execution

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        cmd = command.lower().strip()

        # ✅ WhatsApp Desktop
        if cmd == "open whatsapp":
            funcs.append(asyncio.to_thread(OpenWhatsApp))

        elif cmd == "close whatsapp":
            funcs.append(asyncio.to_thread(CloseWhatsApp))

        # ✅ Generic App Opening
        elif cmd.startswith("open "):
            app_name = command.removeprefix("open ").strip()
            if app_name.lower() != "whatsapp":  # avoid duplicate handling
                funcs.append(asyncio.to_thread(OpenApp, app_name))

        # ✅ Generic App Closing
        elif cmd.startswith("close "):
            app_name = command.removeprefix("close ").strip()
            if app_name.lower() != "whatsapp":
                funcs.append(asyncio.to_thread(CloseApp, app_name))

        elif cmd.startswith("content "):
            funcs.append(asyncio.to_thread(content, command.removeprefix("content ")))

        elif cmd.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search ")))

        elif cmd.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif cmd.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"No function found for {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result
# ✅ Automation runner
async def Automation(commands, parallel=False):
    if parallel:
        await asyncio.gather(*(TranslateAndExecute([cmd]) async for cmd in commands))
    else:
        async for _ in TranslateAndExecute(commands):
            pass
    return True              
        
# Automation (parallel or sequential)
async def Automation(commands, parallel=False):
    if parallel:
        await asyncio.gather(*(TranslateAndExecute([cmd]) async for cmd in commands))
    else:
        async for _ in TranslateAndExecute(commands):
            pass
    return True

# Example run
if __name__ == "__main__":
    asyncio.run(Automation([], parallel=False))
