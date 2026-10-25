import json
from pathlib import Path
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODELE = "gemini-embedding-001"

index = json.loads(Path("index.json").read_text(encoding="utf-8"))
matrice = np.array([d["vecteur"] for d in index])
matrice = matrice / np.linalg.norm(matrice, axis=1, keepdims=True)  # normalisation

while True:
    question = input("\nTa question (Ctrl+C pour quitter) : ")
    res = client.models.embed_content(
        model=MODELE,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    q = np.array(res.embeddings[0].values)
    q = q / np.linalg.norm(q)

    scores = matrice @ q  # similarité cosinus avec chaque passage
    for i in np.argsort(scores)[::-1][:3]:
        print(f"\n--- score {scores[i]:.3f} ---\n{index[i]['texte']}")