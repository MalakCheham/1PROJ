
"""network utils for the game"""
def plateau_to_str(plateau):
    return '\n'.join([''.join(row) for row in plateau.cases])

def pions_to_str(pions):
    return '|'.join([f"{symb}:{';'.join([f'{i},{j}' for (i,j) in positions])}" for symb, positions in pions.items()])

def str_to_plateau(s):
    from core.plateau import Plateau
    lines = s.strip().split('\n')
    plateau = Plateau()
    plateau.cases = [list(line) for line in lines]
    return plateau

def str_to_pions(s):
    pions = {'X': set(), 'O': set()}
    for part in s.split('|'):
        if not part: continue
        symb, positions = part.split(':')
        if positions:
            pions[symb] = set(tuple(map(int, pos.split(','))) for pos in positions.split(';') if pos)
    return pions
