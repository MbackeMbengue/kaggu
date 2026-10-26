import json
import time
import unicodedata
from pathlib import Path
from rag import repondre


def normaliser(texte):
    """Minuscules et sans accents, pour comparer 'Imân' et 'iman'."""
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def contient_vers(passages, numero):
    """Vrai si l'un des passages couvre le vers demandé."""
    return any(
        p["vers_debut"] is not None and p["vers_debut"] <= numero <= p["vers_fin"]
        for p in passages
    )


tests = json.loads(Path("tests/questions.json").read_text(encoding="utf-8"))
reussis = 0

for n, test in enumerate(tests, start=1):
    reponse, passages = repondre(test["question"])
    rep = normaliser(reponse)
    erreurs = []

    if test.get("doit_refuser"):
        if "je ne trouve pas" not in rep:
            erreurs.append("aurait dû refuser")
    else:
        manquants = [v for v in test["vers_attendus"] if not contient_vers(passages, v)]
        if manquants:
            erreurs.append(f"recherche : vers {manquants} absents des passages")
        if "je ne trouve pas" in rep:
            erreurs.append("refus à tort")
        mots = [m for m in test["mots_cles"] if normaliser(m) not in rep]
        if mots:
            erreurs.append(f"mots-clés absents de la réponse : {mots}")

    if "verset" in rep:
        erreurs.append("emploie le mot « verset »")

    if erreurs:
        print(f"❌ {n}. {test['question']}")
        for e in erreurs:
            print(f"     - {e}")
        print(f"     Réponse : {reponse[:150]}…")
    else:
        reussis += 1
        print(f"✅ {n}. {test['question']}")

    time.sleep(4)  # pour rester sous les limites du palier gratuit

print(f"\nScore : {reussis}/{len(tests)}")