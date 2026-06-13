# Backend/RealtimeSearchEngine.py
import json
import datetime
import os
import traceback
from dotenv import dotenv_values
from groq import Groq

# Optional: pip install googlesearch-python
try:
    from googlesearch import search as Search
except ImportError:
    Search = None

class RealtimeSearchEngine:
    def __init__(self):
        env_vars = dotenv_values(".env")
        self.USERNAME = env_vars.get("USERNAME", "Amit Paul")
        self.ASSISTANT_NAME = env_vars.get("ASSISTANT_NAME", "jarvis")
        self.GROQ_API_KEY = env_vars.get("GROQ_API_KEY", "your-api-key-here")
        self.client = Groq(api_key=self.GROQ_API_KEY)
        
        self.system_prompt = f"""Hello, I am {self.USERNAME}, You are a very accurate and advanced AI chatbot named {self.ASSISTANT_NAME} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""
        
        self.initialize_chatlog()
        
        self.system_chatbot = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello sir, how can I help you?"}
        ]

    def initialize_chatlog(self):
        """Ensure chatlog file exists"""
        if not os.path.exists("Data"):
            os.makedirs("Data")
        
        self.chatlog_path = os.path.join("Data", "ChatLog.json")
        if not os.path.exists(self.chatlog_path):
            with open(self.chatlog_path, "w") as f:
                json.dump([], f)

    def google_search(self, query):
        """Perform a Google search and return formatted results"""
        if Search is None:
            return f"No search library available. (Query: {query})"

        try:
            results = list(Search(query, advanced=True, num_results=5))
            answer = f"The search results for '{query}' are: \n[start]\n"
            answer += "\n".join(str(result) for result in results)
            answer += "\n[end]"
            return answer
        except Exception as e:
            return f"Search error: {str(e)}"

    @staticmethod
    def answer_modifier(answer):
        """Clean up the answer by removing empty lines"""
        return "\n".join(line for line in answer.split("\n") if line.strip())

    def get_current_information(self):
        """Get current date/time information"""
        now = datetime.datetime.now()
        return (
            f"Use This Real-time Information if needed:\n"
            f"Day: {now.strftime('%A')}\n"
            f"Month: {now.strftime('%B')}\n"
            f"Year: {now.strftime('%Y')}\n"
            f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds."
        )

    def search(self, prompt):
        """Main method to perform realtime search and generate response"""
        try:
            # Load chat history
            with open(self.chatlog_path, "r") as f:
                messages = json.load(f)
            
            messages.append({"role": "user", "content": prompt})
            
            # Add search results temporarily
            self.system_chatbot.append({
                "role": "system", 
                "content": self.google_search(prompt)
            })
            
            # Generate response
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=self.system_chatbot + [
                    {"role": "system", "content": self.get_current_information()}
                ] + messages,
                temperature=0.7,
                max_tokens=2048,
                top_p=1,
                stream=True,
                stop=None
            )
            
            answer = ""
            for chunk in completion:
                if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content
            
            answer = self.answer_modifier(answer.strip().replace("</s>", ""))
            
            # Update chat history
            messages.append({"role": "assistant", "content": answer})
            with open(self.chatlog_path, "w") as f:
                json.dump(messages, f, indent=4)
            
            return answer
            
        except Exception as e:
            traceback.print_exc()
            return f"Error: {str(e)}"
        finally:
            # Remove temporary search results
            if len(self.system_chatbot) > 3:
                self.system_chatbot.pop()

# Test code
if __name__ == "__main__":
    engine = RealtimeSearchEngine()
    print("Realtime Search Engine Test Mode (type 'exit' to quit)")
    while True:
        prompt = input("\nEnter your query: ")
        if prompt.lower() in ("exit", "quit"):
            break
        print(engine.search(prompt))