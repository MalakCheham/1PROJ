from constantes import COLOR_MAP, ORIENTATIONS_VALIDES, QUADRANTS_COULEURS, MODELE_QUADRANT, EMPLACEMENTS_COORDONNEES, TAILLE_QUADRANT

def creer_quadrant(quadrant_id):
    """Crée un quadrant avec une disposition de cases spécifique."""
    modele = MODELE_QUADRANT
    couleurs = QUADRANTS_COULEURS[quadrant_id]

    return modele, couleurs["recto"], couleurs["verso"]

def afficher_quadrant(modele, couleurs):
    """Affiche un quadrant avec des points mais en conservant les couleurs."""
    for i, ligne in enumerate(modele):
        for j, case in enumerate(ligne):
            couleur = couleurs[i][j]
            if couleur in COLOR_MAP:
                print(f"{COLOR_MAP[couleur]}{case}{COLOR_MAP['reset']} ", end="")
            else:
                print(f"{case} ", end="")
        print()

def choisir_quadrant():
    """Permet au joueur de choisir un quadrant."""
    while True:
        try:
            choix = int(input("Quel quadrant choisissez-vous ? (1-4) "))
            if 1 <= choix <= 4:
                return creer_quadrant(choix)
            else:
                print("Choix invalide.")
        except ValueError:
            print("Choix invalide.")

def choisir_face():
    """Permet au joueur de choisir la face d'un quadrant."""
    while True:
        try:
            choix = int(input("Quelle face choisissez-vous ? (1 ou 2) ")) - 1
            if choix in (0, 1):
                return choix
            else:
                print("Choix invalide.")
        except ValueError:
            print("Choix invalide.")

def choisir_orientation():
    """Permet au joueur de choisir l'orientation d'un quadrant."""
    while True:
        try:
            choix = int(input("Quelle orientation choisissez-vous ? (0, 90, 180 ou 270) "))
            if choix in ORIENTATIONS_VALIDES:
                return choix // 90  # Convertir en index (0, 1, 2, 3)
            else:
                print("Choix invalide. Veuillez entrer 0, 90, 180 ou 270.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre (0, 90, 180 ou 270).")