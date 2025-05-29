"""network utils for the game"""
def plateau_to_str(plateau):
    return '\n'.join([''.join(row) for row in plateau.cells])

def pions_to_str(pions):
    return '|'.join([f"{symb}:{';'.join([f'{i},{j}' for (i,j) in positions])}" for symb, positions in pions.items()])

def str_to_plateau(board_str):
    from core.plateau import Board
    lines = board_str.strip().split('\n')
    board = Board()
    board.cells = [list(line) for line in lines]
    return board

def str_to_pions(pieces_str):
    pions = {'X': set(), 'O': set()}
    for part in pieces_str.split('|'):
        if not part: continue
        symb, positions = part.split(':')
        if positions:
            pions[symb] = set(tuple(map(int, pos.split(','))) for pos in positions.split(';') if pos)
    return pions
