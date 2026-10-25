def decouper(texte, taille_max=800):
    """Regroupe les lignes du texte en passages d'environ taille_max caractères.
    Chaque passage reprend la dernière ligne du précédent (chevauchement),
    pour ne pas couper une idée en deux."""
    lignes = [l.strip() for l in texte.splitlines() if l.strip()] # enlever les lignes vides
    passages, courant = [], []  # passages, passage en cours

    for ligne in lignes:
        if courant and len("\n".join(courant + [ligne])) > taille_max: # passage trop long
            passages.append("\n".join(courant)) # on enregistre le passage
            courant = courant[-1:] if len(courant) > 1 else [] # on garde la dernière ligne pour le chevauchement
        courant.append(ligne) # on ajoute la ligne

    if courant: # il reste un passage en cours
        passages.append("\n".join(courant)) # on enregistre le dernier passage
    return passages # on renvoie la liste des passages


if __name__ == "__main__":  # pour tester
    from pathlib import Path # pour lire le texte
    texte = Path("corpus/texte1.txt").read_text(encoding="utf-8") # lire le texte
    for i, p in enumerate(decouper(texte)): # parcourir les passages
        print(f"\n=== Passage {i} ({len(p)} caractères) ===\n{p}") # afficher le passage