from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()  # lit automatiquement GEMINI_API_KEY

reponse = client.models.generate_content(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(
        system_instruction="Tu es un assistant pédagogue et concis."
    ),
    contents="Explique ce qu'est un embedding en 3 phrases.",
)

print(reponse.text)