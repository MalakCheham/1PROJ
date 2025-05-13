from core.plateau import Plateau
from core.joueur import Joueur
from jeux.katarenga import JeuKatarenga
from jeux.congress import JeuCongress
from jeux.isolation import JeuIsolation

def init_joueurs():
    return [Joueur(0, 'X'), Joueur(1, 'O')]

def init_pions():
    return {
        'X': {(0, 1), (0, 4), (1, 0), (1, 7)},
        'O': {(7, 1), (7, 4), (6, 0), (6, 7)}
    }

def choisir_jeu():
    print("=== Menu ===")
    print("1. Katarenga\n2. Congress\n3. Isolation")
    return input("Choix : ")

def main():
    choix = choisir_jeu()
    plateau = Plateau()
    joueurs = init_joueurs()

    if choix == '1':
        jeu = JeuKatarenga(plateau, joueurs, init_pions())
    elif choix == '2':
        jeu = JeuCongress(plateau, joueurs, init_pions())
    elif choix == '3':
        jeu = JeuIsolation(plateau, joueurs)
    else:
        print("Choix invalide.")
        return

    jeu.jouer()

if __name__ == '__main__':
    main()
