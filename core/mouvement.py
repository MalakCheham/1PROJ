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

def est_mouvement_roi(depart, arrivee):
    dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
    return dl <= 1 and dc <= 1 and (dl != 0 or dc != 0)

def est_mouvement_cavalier(depart, arrivee):
    dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
    return (dl == 2 and dc == 1) or (dl == 1 and dc == 2)

def est_mouvement_fou(depart, arrivee, plateau, pions):
    if abs(arrivee[0] - depart[0]) != abs(arrivee[1] - depart[1]):
        return False
    sl = 1 if arrivee[0] > depart[0] else -1
    sc = 1 if arrivee[1] > depart[1] else -1
    l, c = depart[0] + sl, depart[1] + sc
    while (l, c) != arrivee:
        if not (0 <= l < 8 and 0 <= c < 8):
            return False
        if (l, c) in pions['X'] or (l, c) in pions['O']:
            return False
        if plateau.cases[l][c] == 'J':
            return (l, c) == arrivee
        l += sl
        c += sc
    return True

def est_mouvement_tour(depart, arrivee, plateau, pions):
    if depart[0] != arrivee[0] and depart[1] != arrivee[1]:
        return False
    sl = 0 if depart[0] == arrivee[0] else (1 if arrivee[0] > depart[0] else -1)
    sc = 0 if depart[1] == arrivee[1] else (1 if arrivee[1] > depart[1] else -1)
    l, c = depart[0] + sl, depart[1] + sc
    while (l, c) != arrivee:
        if not (0 <= l < 8 and 0 <= c < 8):
            return False
        if (l, c) in pions['X'] or (l, c) in pions['O']:
            return False
        if plateau.cases[l][c] == 'R':
            return (l, c) == arrivee
        l += sl
        c += sc
    return True

def generer_coups_possibles(depart, couleur, symbole, plateau, pions, capture=True):
    coups = set()
    for i in range(8):
        for j in range(8):
            arrivee = (i, j)
            piece_arrivee = next((s for s in ['X', 'O'] if arrivee in pions[s]), None)
            if capture:
                if piece_arrivee is None or piece_arrivee != symbole:
                    mouvement_valide = (
                        (couleur == 'B' and est_mouvement_roi(depart, arrivee)) or
                        (couleur == 'V' and est_mouvement_cavalier(depart, arrivee)) or
                        (couleur == 'J' and est_mouvement_fou(depart, arrivee, plateau, pions)) or
                        (couleur == 'R' and est_mouvement_tour(depart, arrivee, plateau, pions))
                    )
                    if mouvement_valide:
                        coups.add(arrivee)
            else:
                # Pas de capture : on ne peut pas aller sur une case occupée (congress, isolation)
                if (arrivee in pions['X']) or (arrivee in pions['O']):
                    continue
                mouvement_valide = (
                    (couleur == 'B' and est_mouvement_roi(depart, arrivee)) or
                    (couleur == 'V' and est_mouvement_cavalier(depart, arrivee)) or
                    (couleur == 'J' and est_mouvement_fou(depart, arrivee, plateau, pions)) or
                    (couleur == 'R' and est_mouvement_tour(depart, arrivee, plateau, pions))
                )
                if mouvement_valide:
                    coups.add(arrivee)
    return coups
