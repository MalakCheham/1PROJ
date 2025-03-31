from constantes import SYMBOL_JOUEUR_0, SYMBOL_JOUEUR_1

def est_mouvement_valide(pions, joueur, pion_depart, pion_arrivee):
    """Vérifie si le mouvement d'un pion est valide."""
    ligne_depart, colonne_depart = pion_depart
    ligne_arrivee, colonne_arrivee = pion_arrivee

    if not (0 <= ligne_depart < 8 and 0 <= colonne_depart < 8 and 0 <= ligne_arrivee < 8 and 0 <= colonne_arrivee < 8):
        return False

    symbole_joueur = SYMBOL_JOUEUR_0 if joueur == 0 else SYMBOL_JOUEUR_1
    if pions[ligne_depart][colonne_depart] != symbole_joueur:
        return False

    if pions[ligne_arrivee][colonne_arrivee] is not None:
        return False

    couleur_case_depart = (ligne_depart + colonne_depart) % 4

    if couleur_case_depart == 0:
        return mouvement_roi(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee)
    elif couleur_case_depart == 1:
        return mouvement_cavalier(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee)
    elif couleur_case_depart == 2:
        return mouvement_fou(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee)
    else:
        return mouvement_tour(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee)

def mouvement_roi(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee):
    """Logique pour le roi."""
    return abs(ligne_arrivee - ligne_depart) <= 1 and abs(colonne_arrivee - colonne_depart) <= 1

def mouvement_cavalier(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee):
    """Logique pour le cavalier."""
    return (abs(ligne_arrivee - ligne_depart) == 2 and abs(colonne_arrivee - colonne_depart) == 1) or \
           (abs(ligne_arrivee - ligne_depart) == 1 and abs(colonne_arrivee - colonne_depart) == 2)

def mouvement_fou(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee):
    """Logique pour le fou."""
    if abs(ligne_arrivee - ligne_depart) != abs(colonne_arrivee - colonne_depart):
        return False

    direction_ligne = 1 if ligne_arrivee > ligne_depart else -1
    direction_colonne = 1 if colonne_arrivee > colonne_depart else -1
    ligne, colonne = ligne_depart + direction_ligne, colonne_depart + direction_colonne
    while ligne != ligne_arrivee and colonne != colonne_arrivee:
        if pions[ligne][colonne] is not None:
            return False
        ligne += direction_ligne
        colonne += direction_colonne
    return True

def mouvement_tour(pions, ligne_depart, colonne_depart, ligne_arrivee, colonne_arrivee):
    """Logique pour la tour."""
    if ligne_arrivee != ligne_depart and colonne_arrivee != colonne_depart:
        return False

    if ligne_arrivee == ligne_depart:
        direction = 1 if colonne_arrivee > colonne_depart else -1
        colonne = colonne_depart + direction
        while colonne != colonne_arrivee:
            if pions[ligne_depart][colonne] is not None:
                return False
            if (ligne_depart + colonne) % 4 == 3:
                return colonne == colonne_arrivee
            colonne += direction
    else:
        direction = 1 if ligne_arrivee > ligne_depart else -1
        ligne = ligne_depart + direction
        while ligne != ligne_arrivee:
            if pions[ligne][colonne_depart] is not None:
                return False
            if (ligne + colonne_depart) % 4 == 3:
                return ligne == ligne_arrivee
            ligne += direction
    return True