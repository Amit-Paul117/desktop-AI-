
from Frontend.GUI import(
    GraphicalUserInterface,
    SetAssistantStatus,
    SetMicrophoneStatus,
    TempDirectoryPath,
    AnsweModifier,
    QueryModifier,
    GetMicrophoneStatus,
    ShowTextToScreen,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import chatbot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from time import sleep
import subprocess 
import threading
import json
import os
from Backend import Automation


env_vars = dotenv_values(".env")
Username= env_vars.get("USERNAME")
Assistantname = env_vars.get("ASSISTANT_NAME")
DefaultMessage = f'''{Username} : Hello{Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []   # ✅ renamed to avoid conflict
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding = 'utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)
                
def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        Chatlog_data = json.load(file)
    return Chatlog_data

def ChatLogIntigration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:       
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n" 
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    
    formatted_chatlog = formatted_chatlog.replace("user", f"{Username} ")
    formatted_chatlog = formatted_chatlog.replace("assistant", f"{Assistantname} ")
    
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnsweModifier(formatted_chatlog))
        
        
def ShowChatOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
    except FileNotFoundError:
        data = ""
    
    if data.strip():
        lines = data.split('\n')
        result = '\n'.join(lines)
        
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(result)
            
            
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntigration()
    ShowChatOnGUI()
    
InitialExecution()


# ✅ Safe wrapper for realtime search
def SafeRealtimeSearch(query):
    try:
        return RealtimeSearchEngine(query)
    except Exception as e:
        return "Sorry, I couldn't fetch the realtime data right now."


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuer = ""
    
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition() 
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    
    print("")
    print(f"Decision : {Decision}")
    print("")
    
    G = any([i for i in Decision if i.startswith("general")])
    R =  any([i for i in Decision if i.startswith("realtime")])
    
    Mearged_query  = " and".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuer = str(queries)
            ImageExecution = True  
            
            

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                
                import asyncio 

                asyncio.run(Automation.Automation(list(Decision)))
                TaskExecution = True
                
    if ImageExecution == True:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuer},True")
            
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
            
            
    if G and R or R:
        SetAssistantStatus("Searching....")
        Answer = SafeRealtimeSearch(QueryModifier(Mearged_query))   # ✅ safe wrapper
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ","")
                Answer = chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime","")
                Answer = SafeRealtimeSearch(QueryModifier(QueryFinal))   # ✅ safe wrapper
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye boss!"
                Answer = chatbot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering....")
                os._exit(1)


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")
                
def SecondThread():
    GraphicalUserInterface()
    
if __name__ == "__main__":
    print("Initializing JARVIS AI...")
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
