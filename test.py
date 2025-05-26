import pygame
import sys
import os

# --- CONFIGURATION DU PLATEAU ---
ROWS, COLS = 8, 8
SQUARE_SIZE = 67
TEXTURE_DIR = os.path.join("assets", "textures")

TEXTURE_FILES = {
    0: "case-rouge.png",
    1: "case-bleu.png",
    2: "case-vert.png",
    3: "case-jaune.png",
}

BOARD_PATTERN = [
    [0,1,2,3,0,1,2,3],
    [1,2,3,0,1,2,3,0],
    [2,3,0,1,2,3,0,1],
    [3,0,1,2,3,0,1,2],
    [0,1,2,3,0,1,2,3],
    [1,2,3,0,1,2,3,0],
    [2,3,0,1,2,3,0,1],
    [3,0,1,2,3,0,1,2],
]

PIECES = [
    [None]*8 for _ in range(7)
] + [[None, 'B', None, 'N', None, 'B', None, 'N']]

PIECE_RADIUS = SQUARE_SIZE//2 - 8
COLOR_WHITE = (245,245,245)
COLOR_BLACK = (30,30,30)

# --- INITIALISATION PYGAME ---
pygame.init()
win_w = (COLS + 2) * 80
win_h = (ROWS + 2) * 80
screen = pygame.display.set_mode((win_w, win_h))
pygame.display.set_caption("Plateau texturé avec cadre")
clock = pygame.time.Clock()

# --- CHARGEMENT DES TEXTURES ---
tile_textures = {}
for idx, fname in TEXTURE_FILES.items():
    surf = pygame.image.load(os.path.join(TEXTURE_DIR, fname)).convert_alpha()
    tile_textures[idx] = pygame.transform.smoothscale(surf, (SQUARE_SIZE, SQUARE_SIZE))

def draw_border():
    # Affiche le cadre complet (cadre.png) à la taille d'origine
    cadre_img = pygame.image.load(os.path.join(TEXTURE_DIR, "cadre_fin.png")).convert_alpha()
    cadre_w = (COLS + 2) * 80
    cadre_h = (ROWS + 2) * 80
    cadre_img = pygame.transform.smoothscale(cadre_img, (cadre_w, cadre_h))
    screen.blit(cadre_img, (0, 0))


def draw_board():
    # Centre le plateau dans le cadre
    cadre_w = (COLS + 2) * 80
    cadre_h = (ROWS + 2) * 80
    plateau_w = COLS * SQUARE_SIZE
    plateau_h = ROWS * SQUARE_SIZE
    offset_x = (cadre_w - plateau_w) // 2
    offset_y = (cadre_h - plateau_h) // 2
    for r in range(ROWS):
        for c in range(COLS):
            tex = BOARD_PATTERN[r][c]
            screen.blit(tile_textures[tex], (offset_x + c*SQUARE_SIZE, offset_y + r*SQUARE_SIZE))
    # Trait marron foncé autour du plateau
    rect = pygame.Rect(offset_x, offset_y, plateau_w, plateau_h)
    pygame.draw.rect(screen, (62, 30, 11), rect, 3)


def draw_pieces():
    cadre_w = (COLS + 2) * 80
    cadre_h = (ROWS + 2) * 80
    plateau_w = COLS * SQUARE_SIZE
    plateau_h = ROWS * SQUARE_SIZE
    offset_x = (cadre_w - plateau_w) // 2
    offset_y = (cadre_h - plateau_h) // 2
    for r in range(ROWS):
        for c in range(COLS):
            p = PIECES[r][c]
            if not p:
                continue
            cx = offset_x + c*SQUARE_SIZE + SQUARE_SIZE//2
            cy = offset_y + r*SQUARE_SIZE + SQUARE_SIZE//2
            col = COLOR_WHITE if p == "B" else COLOR_BLACK
            pygame.draw.circle(screen, col, (cx, cy), PIECE_RADIUS)


def main():
    running = True
    while running:
        clock.tick(30)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        draw_border()
        draw_board()
        draw_pieces()
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
