import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from decoupage import decouper

load_dotenv()
client = genai.Client()
MODELE = "gemini-embedding-001"

texte = Path("corpus/texte1.txt").read_text(encoding="utf-8")
passages = decouper(texte)
print(f"{len(passages)} passages à indexer")

index = []
for i in range(0, len(passages), 20):  # par lots de 20, pour ménager les limites
    lot = passages[i:i + 20]
    res = client.models.embed_content(
        model=MODELE,
        contents=lot,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    for passage, emb in zip(lot, res.embeddings):
        index.append({"texte": passage, "vecteur": emb.values})
    time.sleep(1)

Path("index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
print(f"Index enregistré : {len(index)} passages, {len(index[0]['vecteur'])} dimensions")

print("\n--- Fin de l'indexation ---\n")