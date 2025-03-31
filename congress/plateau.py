from constantes import TAILLE_PLATEAU, PIONS_INITIAUX, SYMBOL_JOUEUR_0, SYMBOL_JOUEUR_1, COLOR_MAP, EMPLACEMENTS_COORDONNEES
from quadrant import creer_quadrant, choisir_quadrant, choisir_face, choisir_orientation, afficher_quadrant

def afficher_emplacements_remplis(emplacements_remplis):
    """Affiche les emplacements déjà remplis sous forme de carré."""
    carre = [['.', '.'], ['.', '.']]
    for emplacement in emplacements_remplis:
        ligne = (emplacement - 1) // 2
        colonne = (emplacement - 1) % 2
        carre[ligne][colonne] = 'X'

    print("Emplacements déjà remplis :")
    for ligne in carre:
        print(' '.join(ligne))

def choisir_emplacement(emplacements_remplis):
    """Permet au joueur de choisir un emplacement non rempli."""
    while True:
        try:
            choix = int(input("Quel emplacement choisissez-vous ? (1-4) "))
            if choix in range(1, 5) and choix not in emplacements_remplis:
                return choix
            elif choix in emplacements_remplis:
                print("Cet emplacement est déjà rempli. Veuillez en choisir un autre.")
            else:
                print("Choix invalide.")
        except ValueError:
            print("Choix invalide.")

def creer_plateau():
    """Crée un plateau avec 4 quadrants choisis par le joueur."""
    plateau = [[None for _ in range(8)] for _ in range(8)]
    pions = [[None for _ in range(8)] for _ in range(8)]
    emplacements_remplis = []

    for i in range(4):
        print(f"Quadrant {i + 1}:")
        afficher_emplacements_remplis(emplacements_remplis)

        emplacement = choisir_emplacement(emplacements_remplis)
        emplacements_remplis.append(emplacement)

        ligne_debut, colonne_debut = EMPLACEMENTS_COORDONNEES[emplacement]

        modele, recto, verso = creer_quadrant(emplacement)

        print("Face 1 (Recto):")
        afficher_quadrant(modele, recto)
        print("Face 2 (Verso):")
        afficher_quadrant(modele, verso)

        face = choisir_face()
        couleurs = recto if face == 0 else verso

        orientation = choisir_orientation()

        for ligne in range(4):
            for colonne in range(4):
                if orientation == 0:
                    plateau[ligne + ligne_debut][colonne + colonne_debut] = couleurs[ligne][colonne]
                elif orientation == 1:
                    plateau[colonne + ligne_debut][3 - ligne + colonne_debut] = couleurs[ligne][colonne]
                elif orientation == 2:
                    plateau[3 - ligne + ligne_debut][3 - colonne + colonne_debut] = couleurs[ligne][colonne]
                elif orientation == 3:
                    plateau[3 - colonne + ligne_debut][ligne + colonne_debut] = couleurs[ligne][colonne]

    # Ajouter les pions initiaux à partir de la constante
    for (ligne, colonne), symbole in PIONS_INITIAUX.items():
        pions[ligne][colonne] = symbole
    
    return plateau, pions

def afficher_plateau(plateau, pions):
    """Affiche le plateau de jeu avec les couleurs des cases et les pions colorés."""
    print("  0  1  2  3  4  5  6  7")
    for ligne in range(TAILLE_PLATEAU):
        print(f"{ligne} ", end="")
        for colonne in range(TAILLE_PLATEAU):
            case = plateau[ligne][colonne]
            pion = pions[ligne][colonne] if pions[ligne][colonne] is not None else None

            if pion is not None:
                if case in COLOR_MAP:
                    print(f"{COLOR_MAP[case]}{pion}{COLOR_MAP['reset']} ", end=" ")
                else:
                    print(f"{pion} ", end=" ")
            else:
                if case in COLOR_MAP:
                    print(f"{COLOR_MAP[case]}.{COLOR_MAP['reset']} ", end=" ")
                else:
                    print(". ", end=" ")
        print()