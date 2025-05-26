import pygame
import sys

COULEURS = ["R", "J", "B", "V"]
COULEURS_HEX = {
    "R": (255, 153, 153), "J": (255, 255, 179), "B": (153, 204, 255), "V": (179, 255, 179)
}

class QuadrantEditorLivePygame:
    def __init__(self, retour_callback=None, network_callback=None):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 650))
        pygame.display.set_caption("Créer un Quadrant 4x4")
        self.font = pygame.font.SysFont("Helvetica", 24, bold=True)
        self.small_font = pygame.font.SysFont("Helvetica", 18)
        self.retour_callback = retour_callback
        self.network_callback = network_callback
        self.current_color = "R"
        self.quadrants = []
        self.grille = [[None for _ in range(4)] for _ in range(4)]
        self.running = True
        self.play_button_enabled = False
        self.info_text = "Quadrant 1/4"
        self.main_loop()

    def draw(self):
        self.screen.fill((255, 248, 225))
        # Titre
        titre = self.font.render("Créer un Quadrant 4x4", True, (0, 102, 68))
        self.screen.blit(titre, (100, 20))
        # Grille
        grid_x, grid_y = 100, 70
        cell_size = 60
        for i in range(4):
            for j in range(4):
                color = COULEURS_HEX[self.grille[i][j]] if self.grille[i][j] else (220, 220, 220)
                rect = pygame.Rect(grid_x + j*cell_size, grid_y + i*cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0,0,0), rect, 2)
        # Choix couleurs
        for idx, c in enumerate(COULEURS):
            pygame.draw.rect(self.screen, COULEURS_HEX[c], (60 + idx*100, 350, 60, 40))
            if self.current_color == c:
                pygame.draw.rect(self.screen, (0,0,0), (60 + idx*100, 350, 60, 40), 3)
        # Boutons
        self.draw_button((60, 410, 180, 40), "✅ Sauvegarder Quadrant", enabled=True)
        self.draw_button((260, 410, 180, 40), "📋 Nouveau Quadrant", enabled=True)
        self.draw_button((60, 470, 380, 40), "🎮 Jouer avec ces quadrants", enabled=self.play_button_enabled)
        self.draw_button((60, 530, 120, 35), "⬅ Retour", enabled=True)
        # Info
        info = self.small_font.render(self.info_text, True, (0,0,0))
        self.screen.blit(info, (200, 580))
        pygame.display.flip()

    def draw_button(self, rect, text, enabled=True):
        color = (76, 175, 80) if enabled else (180, 180, 180)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0,0,0), rect, 2)
        label = self.small_font.render(text, True, (255,255,255) if enabled else (100,100,100))
        self.screen.blit(label, (rect[0]+10, rect[1]+8))

    def main_loop(self):
        while self.running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # Grille
                    grid_x, grid_y, cell_size = 100, 70, 60
                    if grid_x <= x < grid_x+4*cell_size and grid_y <= y < grid_y+4*cell_size:
                        i = (y-grid_y)//cell_size
                        j = (x-grid_x)//cell_size
                        self.grille[i][j] = self.current_color
                    # Choix couleur
                    for idx, c in enumerate(COULEURS):
                        if 60+idx*100 <= x < 60+idx*100+60 and 350 <= y < 390:
                            self.current_color = c
                    # Sauvegarder
                    if 60 <= x < 240 and 410 <= y < 450:
                        self.valider_quadrant()
                    # Nouveau Quadrant
                    if 260 <= x < 440 and 410 <= y < 450:
                        self.reset()
                    # Jouer
                    if 60 <= x < 440 and 470 <= y < 510 and self.play_button_enabled:
                        self.construire_plateau()
                    # Retour
                    if 60 <= x < 180 and 530 <= y < 565:
                        self.running = False
                        if self.retour_callback:
                            self.retour_callback()

    def valider_quadrant(self):
        if any(None in row for row in self.grille):
            self.show_message("Incomplet", "Toutes les cases doivent être colorées.")
            return
        self.quadrants.append({"recto": [row[:] for row in self.grille]})
        if len(self.quadrants) == 4:
            self.show_message("OK", "Les 4 quadrants sont prêts. Cliquez sur 'Jouer avec ces quadrants'.")
            self.play_button_enabled = True
            self.info_text = "Quadrant 4/4"
        else:
            self.reset()
            self.info_text = f"Quadrant {len(self.quadrants)+1}/4"

    def reset(self):
        self.grille = [[None for _ in range(4)] for _ in range(4)]

    def show_message(self, title, message):
        # Simple message using pygame
        msg_font = pygame.font.SysFont("Helvetica", 20, bold=True)
        msg_box = pygame.Surface((400, 120))
        msg_box.fill((255,255,255))
        pygame.draw.rect(msg_box, (0,0,0), (0,0,400,120), 2)
        title_surf = msg_font.render(title, True, (0,0,0))
        msg_surf = self.small_font.render(message, True, (0,0,0))
        msg_box.blit(title_surf, (20, 10))
        msg_box.blit(msg_surf, (20, 50))
        self.screen.blit(msg_box, (50, 250))
        pygame.display.flip()
        pygame.time.wait(1200)

    def construire_plateau(self):
        if len(self.quadrants) != 4:
            self.show_message("Erreur", "Il faut 4 quadrants pour construire le plateau.")
            return
        try:
            import sys
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
            from core.plateau import Plateau
            from core.joueur import Joueur
            # Import du jeu Katarenga depuis gui/jeux_gui/ uniquement
            from gui.jeux_gui.katarenga import JeuKatarenga
        except Exception as e:
            self.show_message("Erreur import", f"Impossible d'importer les modules du jeu : {e}")
            return
        plateau = Plateau()
        positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for i, q in enumerate(self.quadrants):
            bloc = q["recto"]
            for dx in range(4):
                for dy in range(4):
                    plateau.cases[positions[i][0] + dx][positions[i][1] + dy] = bloc[dx][dy]
        pions = {
            'X': {(0, j) for j in range(8)},
            'O': {(7, j) for j in range(8)}
        }
        joueurs = [Joueur(0, 'X'), Joueur(1, 'O')]
        if self.network_callback:
            self.network_callback(plateau, pions)
        else:
            self.running = False
            JeuKatarenga(plateau, joueurs, pions=pions).jouer()

# Pour tester directement ce module
if __name__ == "__main__":
    QuadrantEditorLivePygame()
