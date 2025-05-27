import pygame
import os
from core.constantes import TAILLE_PLATEAU

COLOR_MAP = {
    'R': (255, 153, 153),  # Rouge
    'J': (255, 255, 179),  # Jaune
    'B': (153, 204, 255),  # Bleu
    'V': (179, 255, 179),  # Vert
    None: (220, 220, 220)
}

class PlateauPreview:
    def __init__(self, plateau, pions=None, retour_callback=None):
        pygame.init()
        self.screen = pygame.display.set_mode((700, 700))
        pygame.display.set_caption("Aperçu du Plateau")
        self.font = pygame.font.SysFont("Helvetica", 28, bold=True)
        self.small_font = pygame.font.SysFont("Helvetica", 18)
        self.plateau = plateau
        self.pions = pions or {}
        self.retour_callback = retour_callback
        self.running = True
        self.main_loop()

    def draw(self):
        self.screen.fill((255, 248, 225))
        titre = self.font.render("Plateau généré", True, (0, 102, 68))
        self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 20))
        grid_x, grid_y = 80, 80
        cell_size = 60
        for i in range(TAILLE_PLATEAU):
            for j in range(TAILLE_PLATEAU):
                color = COLOR_MAP.get(self.plateau.cases[i][j], (220, 220, 220))
                rect = pygame.Rect(grid_x + j*cell_size, grid_y + i*cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0,0,0), rect, 2)
                pion = None
                if isinstance(self.pions, dict):
                    pion = self.pions.get((i, j))
                elif isinstance(self.pions, list):
                    pion = self.pions[i][j]
                if pion:
                    col = (245,245,245) if pion == 'B' else (30,30,30)
                    pygame.draw.circle(self.screen, col, rect.center, cell_size//2 - 8)
        # Bouton retour
        btn_rect = pygame.Rect(self.screen.get_width()//2-80, 620, 160, 48)
        pygame.draw.rect(self.screen, (76,175,80), btn_rect, border_radius=14)
        pygame.draw.rect(self.screen, (0,0,0), btn_rect, 2, border_radius=14)
        btn_label = self.small_font.render("Retour", 1, (255,255,255))
        self.screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))
        self.btn_retour_rect = btn_rect
        pygame.display.flip()

    def main_loop(self):
        while self.running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
                    if self.btn_retour_rect.collidepoint(event.pos):
                        self.running = False
                        if self.retour_callback:
                            self.retour_callback()
        pygame.quit()
