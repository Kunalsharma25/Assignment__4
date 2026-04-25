import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
print(f"Key: {groq_key[:10]}...")

try:
    client = Groq(api_key=groq_key)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
