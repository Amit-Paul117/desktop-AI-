from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import mtranslate as mt

env_vars = dotenv_values(".env")
Inputlanguage = env_vars.get("InputLanguage", "en-US")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = 'LANG_CODE';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                // prevent infinite restart
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
        }
    </script>
</body>
</html>'''

HtmlCode = HtmlCode.replace("LANG_CODE", Inputlanguage)

os.makedirs("Data", exist_ok=True)
with open(r"Data\\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

current_dir = os.getcwd().replace("\\", "/")
Link = f"file:///{current_dir}/Data/Voice.html"

chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# ❌ Can't use headless mode if you need actual mic input
# chrome_options.add_argument("--headless=new")  

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirPath = rf"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    questions_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom",
                       "can you", "what's", "where's", "how's" ]
    if any(word + " " in new_query for word in questions_words):
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "?"
        else:
            new_query = new_query[:-1] + "?"
    else:
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "."
        else:
            new_query = new_query[:-1] + "."
    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    driver.get(Link)

    # ✅ Wait for start button to be clickable
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "start"))).click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text.strip():
                driver.find_element(By.ID, "end").click()
                SetAssistantStatus("Translating...")
                return QueryModifier(UniversalTranslator(Text))
            time.sleep(0.3)  # prevent CPU overload
        except Exception:
            time.sleep(0.3)

if __name__ == "__main__":
    while True:
        print(SpeechRecognition())
