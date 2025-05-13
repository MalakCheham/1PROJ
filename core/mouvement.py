MOVES = {
    "B": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
    "V": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)],
    "J": "diagonal",
    "R": "straight"
}

class Mouvement:
    def __init__(self, plateau, pions):
        self.plateau = plateau
        self.pions = pions

    def get_possible_moves(self, board, pieces, r, c):
        symbole = "W" if (r, c) in pieces["W"] else "B"
        case_type = board[r][c]
        moves = []

        if case_type in ["B", "V"]:
            for dr, dc in MOVES[case_type]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and (nr, nc) not in pieces[symbole]:
                    moves.append((nr, nc))

        elif case_type == "J":
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nr, nc = r, c
                while True:
                    nr, nc = nr + dr, nc + dc
                    if not (0 <= nr < 8 and 0 <= nc < 8):
                        break
                    if (nr, nc) in pieces[symbole]:
                        break
                    moves.append((nr, nc))
                    if board[nr][nc] == "J":
                        break

        elif case_type == "R":
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r, c
                while True:
                    nr, nc = nr + dr, nc + dc
                    if not (0 <= nr < 8 and 0 <= nc < 8):
                        break
                    if (nr, nc) in pieces[symbole]:
                        break
                    moves.append((nr, nc))
                    if board[nr][nc] == "R":
                        break

        return moves

    def est_mouvement_valide(self, pions, symbole, depart, arrivee):
        r, c = depart
        return arrivee in self.get_possible_moves(self.plateau.grille, pions, r, c)
