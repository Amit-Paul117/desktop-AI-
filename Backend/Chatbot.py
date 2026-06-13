from groq import Groq
from json import load, dump
import datetime
import os

# Config
USERNAME = "Amit Paul"
ASSISTANT_NAME = "Jarvis"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  

# Groq client
client = Groq(api_key=GROQ_API_KEY)

# System message
SYSTEM_PROMPT = f"""
Hello, I am {USERNAME}, You are a very accurate and advanced AI chatbot named {ASSISTANT_NAME} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SYSTEM_CHATBOT = [{"role": "system", "content": SYSTEM_PROMPT}]

CHATLOG_FILE = r"Data\ChatLog.json"


# --- Utility Functions ---
def load_chat_log():
    """Load chat messages from file."""
    if not os.path.exists(CHATLOG_FILE):
        return []
    with open(CHATLOG_FILE, "r") as f:
        return load(f)


def save_chat_log(messages):
    """Save chat messages to file."""
    with open(CHATLOG_FILE, "w") as f:
        dump(messages, f, indent=4)


def realtime_information():
    """Generate real-time date & time info."""
    now = datetime.datetime.now()
    return (
        "Please use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')} | Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : {now.strftime('%M')} minutes : {now.strftime('%S')} seconds.\n"
    )


def answer_modifier(answer):
 
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)


#Main Chatbot
def chatbot(query):
    try:
        messages = load_chat_log()
        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SYSTEM_CHATBOT
                     + [{"role": "system", "content": realtime_information()}]
                     + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s", "")
        messages.append({"role": "assistant", "content": answer})

        save_chat_log(messages)
        return answer_modifier(answer)

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Sorry, I encountered an error and couldn’t process your request."


# Run as script
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(chatbot(user_input))

    