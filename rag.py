import json
from pathlib import Path
import numpy as np
import time
from google.genai import errors
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv() # pour charger les variables d'environnement
client = genai.Client() # pour créer le client GenAI
MODELE_EMB = "gemini-embedding-001" # modèle d'embedding
MODELE_LLM = "gemini-3.6-flash" # modèle de LLM

index = json.loads(Path("index.json").read_text(encoding="utf-8")) # lire l'index
matrice = np.array([d["vecteur"] for d in index]) # extraire les vecteurs
matrice = matrice / np.linalg.norm(matrice, axis=1, keepdims=True) # normalisation des vecteurs pour la similarité cosinus

CONSIGNE = (
    "Tu réponds UNIQUEMENT à partir des passages fournis, extraits du "
    "Viatique des Adolescents de Cheikh Ahmadou Bamba. "
    "Cite les numéros des vers sur lesquels tu t'appuies. "
    "Pour désigner les vers du poème, utilise toujours le mot « vers », "
    "jamais « verset » (réservé au Coran). "
    "Si le sujet n'est abordé que partiellement, dis ce que les passages en disent "
    "et précise ce qu'ils ne disent pas. "
    "Si les passages ne répondent pas à la question, dis clairement : "
    "« Je ne trouve pas cela dans les textes disponibles. » N'invente rien."
)


def chercher(question, k=3):
    '''
    Cherche les passages les plus similaires au question.
    Retourne une liste de k passages.
    '''
    res = client.models.embed_content(
        model=MODELE_EMB,
        contents=question,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    ) # embedding
    q = np.array(res.embeddings[0].values) # extraire le vecteur
    q = q / np.linalg.norm(q) # normalisation
    scores = matrice @ q # similarité cosinus avec chaque passage
    
    return [index[i] for i in np.argsort(scores)[::-1][:k]] # trier et retourner les k passages les plus similaires

def elargir_aux_sections(passages):
    """Remplace les passages trouvés par leurs sections complètes,
    dans l'ordre de pertinence, sans doublon."""
    sections = []
    for p in passages:
        cle = (p["oeuvre"], p["section"])
        if cle not in sections:
            sections.append(cle)

    resultat = []
    for oeuvre, section in sections:
        morceaux = [d for d in index if d["oeuvre"] == oeuvre and d["section"] == section]
        # Recoller les morceaux en retirant les vers dupliqués par le chevauchement
        lignes = list(dict.fromkeys(l for m in morceaux for l in m["texte"].split("\n")))
        nums = [n for m in morceaux for n in (m["vers_debut"], m["vers_fin"]) if n is not None]
        debut, fin = (min(nums), max(nums)) if nums else (None, None)
        resultat.append({
            "oeuvre": oeuvre,
            "section": section,
            "vers_debut": debut,
            "vers_fin": fin,
            "reference": f"{oeuvre} — {section}" + (f" (v. {debut}–{fin})" if nums else ""),
            "texte": "\n".join(lignes),
        })
    return resultat

def repondre(question):
    passages = elargir_aux_sections(chercher(question))
    contexte = "\n\n".join(f"[{p['reference']}]\n{p['texte']}" for p in passages)

    for tentative in range(4):
        try:
            reponse = client.models.generate_content(
                model=MODELE_LLM,
                config=types.GenerateContentConfig(system_instruction=CONSIGNE, temperature=0.1),
                contents=f"PASSAGES :\n{contexte}\n\nQUESTION : {question}",
            )
            return reponse.text, passages
        except errors.ServerError:
            attente = 2 ** tentative * 5  # 5 s, 10 s, 20 s, 40 s
            print(f"(Serveur saturé, nouvel essai dans {attente} s…)")
            time.sleep(attente)

    return "Le service est momentanément indisponible, réessaie plus tard.", passages

if __name__ == "__main__":
    while True:
        question = input("\nTa question (Ctrl+C pour quitter) : ")
        texte, _ = repondre(question)
        print(f"\n{texte}")