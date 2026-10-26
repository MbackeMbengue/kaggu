import re
import sys
from pathlib import Path
import ftfy

RE_VERS = re.compile(r"^(\d+)\s*[.\-–]\s*")  # accepte "187." et "187-"


def debute_en_majuscules(ligne):
    """Vrai si les deux premiers mots sont entièrement en majuscules."""
    mots = ligne.split()[:2]
    return len(mots) == 2 and all(m.isupper() for m in mots)


def nettoyer(brut, premier_attendu):
    sortie, titres, attendu = [], [], premier_attendu
    ligne_vide_avant = True

    for brute in brut.splitlines():
        ligne = re.sub(r"\s+", " ", ftfy.fix_text(brute)).strip()
        if not ligne:
            ligne_vide_avant = True
            continue
        m = RE_VERS.match(ligne)
        if m and int(m.group(1)) == attendu:
            # nouveau vers, numérotation uniformisée en "N. "
            sortie.append(f"{attendu}. {ligne[m.end():]}")
            attendu += 1
        elif not sortie or ligne_vide_avant or debute_en_majuscules(ligne):
            sortie.append(ligne)              # intertitre
            titres.append(ligne)
        else:
            sortie[-1] += " " + ligne         # suite d'un vers (ou d'un titre) coupé par le PDF
        ligne_vide_avant = False
    return sortie, titres, attendu - 1


if __name__ == "__main__":
    source, premier = Path(sys.argv[1]), int(sys.argv[2])
    sortie, titres, dernier = nettoyer(source.read_text(encoding="utf-8"), premier)
    cible = source.with_name(source.stem + "_propre.txt")
    cible.write_text("\n".join(sortie) + "\n", encoding="utf-8")

    print(f"Fichier écrit : {cible}")
    print(f"Vers reconnus : {premier} à {dernier}")
    print(f"\nIntertitres détectés ({len(titres)}) :")
    for t in titres:
        print(f"  - {t}")
    print("\nLes 5 lignes les plus longues (à vérifier : vers fusionnés ?) :")
    for l in sorted(sortie, key=len, reverse=True)[:5]:
        print(f"  [{len(l)} car.] {l[:90]}…")