from board import display_board
from piece import get_possible_moves

class Katarenga:
    def __init__(self, board):
        self.board = board
        self.pieces = {"W": set(), "B": set()}  # Initialisation correcte

        self.init_pieces()
    
    def init_pieces(self):
        """Place les pions au départ."""
        for i in range(8):
            self.pieces["W"].add((1, i))
            self.pieces["B"].add((6, i))

    def move_piece(self, player, r, c, nr, nc):
        """Déplace un pion s'il est dans les mouvements possibles."""
        if (r, c) not in self.pieces[player]:
            print("Mauvais pion sélectionné !")
            return False

        possible_moves = get_possible_moves(self.board, self.pieces, r, c)
        if (nr, nc) not in possible_moves:
            print("Déplacement invalide !")
            return False

        # Capture
        opponent = "B" if player == "W" else "W"
        if (nr, nc) in self.pieces[opponent]:
            self.pieces[opponent].remove((nr, nc))

        # Déplacement
        self.pieces[player].remove((r, c))
        self.pieces[player].add((nr, nc))
        return True

    def check_victory(self):
        """Vérifie si un joueur a gagné."""
        if len(self.pieces["W"]) < 3:
            print("Les Noirs gagnent par capture !")
            return True
        if len(self.pieces["B"]) < 3:
            print("Les Blancs gagnent par capture !")
            return True
        return False

    def play(self):
        """Boucle principale du jeu."""
        turn = "W"
        while True:
            display_board(self.board, self.pieces)
            print(f"Tour du joueur {turn}")

            try:
                r, c = map(int, input("Sélectionnez un pion (ligne colonne) : ").split())
                nr, nc = map(int, input("Sélectionnez une destination (ligne colonne) : ").split())
            except ValueError:
                print("Entrée invalide !")
                continue

            if self.move_piece(turn, r, c, nr, nc):
                if self.check_victory():
                    break
                turn = "B" if turn == "W" else "W"
