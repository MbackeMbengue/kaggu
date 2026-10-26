import json
import re
from pathlib import Path


def numero_du_vers(ligne):
    """Renvoie le numéro si la ligne commence par 'N. ', sinon None."""
    m = re.match(r"^(\d+)\.\s", ligne)
    return int(m.group(1)) if m else None


def grouper(lignes, taille_max=800):
    """Regroupe des lignes en blocs d'environ taille_max caractères,
    avec un vers de chevauchement entre deux blocs."""
    blocs, courant = [], []
    for ligne in lignes:
        if courant and len("\n".join(courant + [ligne])) > taille_max:
            blocs.append(courant)
            courant = courant[-1:] if len(courant) > 1 else []
        courant.append(ligne)
    if courant:
        blocs.append(courant)
    return blocs


def decouper_par_sections(texte, plan, taille_max=800):
    sections = [dict(s, lignes=[]) for s in plan["sections"]]
    courante, vu_un_vers = 0, False

    # 1. Ranger chaque ligne dans sa section
    for ligne in (l.strip() for l in texte.splitlines()):
        if not ligne:
            continue
        num = numero_du_vers(ligne)
        if num is None:
            if vu_un_vers:
                continue  # intertitre du texte : remplacé par le titre du plan
        else:
            vu_un_vers = True
            trouvees = [i for i, s in enumerate(sections) if s["debut"] <= num <= s["fin"]]
            if not trouvees:
                raise ValueError(f"Le vers {num} n'appartient à aucune section du plan")
            courante = trouvees[0]
        sections[courante]["lignes"].append(ligne)

    # 2. Découper chaque section séparément, et ajouter les métadonnées
    passages = []
    for s in sections:
        for bloc in grouper(s["lignes"], taille_max):
            nums = [n for n in map(numero_du_vers, bloc) if n is not None]
            debut, fin = (nums[0], nums[-1]) if nums else (None, None)
            if not nums:
                ref_vers = "avant-propos"
            elif debut == fin:
                ref_vers = f"v. {debut}"
            else:
                ref_vers = f"v. {debut}–{fin}"
            passages.append({
                "oeuvre": plan["titre"],
                "section": s["titre"],
                "vers_debut": debut,
                "vers_fin": fin,
                "reference": f"{plan['titre']} — {s['titre']} ({ref_vers})",
                "texte": "\n".join(bloc),
            })
    return passages


if __name__ == "__main__":
    texte = Path("corpus/texte1.txt").read_text(encoding="utf-8")
    plan = json.loads(Path("corpus/texte1_plan.json").read_text(encoding="utf-8"))
    for p in decouper_par_sections(texte, plan):
        print(f"{p['reference']} — {len(p['texte'])} caractères")