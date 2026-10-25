import json
import re
import time
from pathlib import Path
from rag import chercher, index


def rang_du_vers(passages, numero):
    for rang, p in enumerate(passages, start=1):
        if p["vers_debut"] is not None and p["vers_debut"] <= numero <= p["vers_fin"]:
            return rang
    return None


tests = json.loads(Path("tests/questions.json").read_text(encoding="utf-8"))

for test in tests:
    if test.get("doit_refuser"):
        continue
    classement = chercher(test["question"], k=len(index))  # tous les passages, triés
    rangs = {v: rang_du_vers(classement, v) for v in test["vers_attendus"]}
    pire = max(rangs.values())
    print(f"{'✅' if pire <= 3 else '❌'} {test['question']}")
    print(f"     rang de chaque vers attendu : {rangs}")
    time.sleep(1)