from plateau import creer_plateau, afficher_plateau
from mouvements import est_mouvement_valide
from constantes import SYMBOL_JOUEUR_0, SYMBOL_JOUEUR_1

def est_victoire(pions, joueur):
    """Vérifie si le joueur a gagné."""
    symbole = 'X' if joueur == 0 else 'O'
    positions = [(ligne, colonne) for ligne in range(8) for colonne in range(8) if pions[ligne][colonne] == symbole]

    if not positions:
        return False

    vus = {positions[0]}
    a_voir = [positions[0]]

    while a_voir:
        ligne, colonne = a_voir.pop()
        voisins = [(ligne - 1, colonne), (ligne + 1, colonne), (ligne, colonne - 1), (ligne, colonne + 1)]
        for voisin in voisins:
            if voisin in positions and voisin not in vus:
                vus.add(voisin)
                a_voir.append(voisin)

    return len(vus) == len(positions)

def rejouer():
    """Permet de rejouer une partie."""
    while True:
        choix = input("Voulez-vous rejouer ? (o/n) ").lower()
        if choix == 'o':
            jouer_congress()
            break
        elif choix == 'n':
            print("Merci d'avoir joué !")
            break
        else:
            print("Choix invalide.")

def jouer_congress():
    """Fonction principale pour jouer au jeu Congress."""
    plateau, pions = creer_plateau()
    afficher_plateau(plateau, pions)

    joueur_actuel = 0
    while True:
        print(f"Tour du joueur {joueur_actuel} ({SYMBOL_JOUEUR_0} pour joueur 0, {SYMBOL_JOUEUR_1} pour joueur 1)")

        try:
            ligne_depart = int(input("Entrez la ligne du pion à déplacer : "))
            colonne_depart = int(input("Entrez la colonne du pion à déplacer : "))
            ligne_arrivee = int(input("Entrez la ligne de destination : "))
            colonne_arrivee = int(input("Entrez la colonne de destination : "))

            pion_depart = (ligne_depart, colonne_depart)
            pion_arrivee = (ligne_arrivee, colonne_arrivee)

            if est_mouvement_valide(pions, joueur_actuel, pion_depart, pion_arrivee):
                pions[ligne_arrivee][colonne_arrivee] = pions[ligne_depart][colonne_depart]
                pions[ligne_depart][colonne_depart] = None
                afficher_plateau(plateau, pions)

                if est_victoire(pions, joueur_actuel):
                    print(f"Félicitations ! Le joueur {joueur_actuel} a gagné !")
                    break

                joueur_actuel = 1 - joueur_actuel
            else:
                print("Mouvement invalide. Réessayez.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer des coordonnées valides.")

if __name__ == "__main__":
    jouer_congress()