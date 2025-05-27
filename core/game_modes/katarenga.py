import pygame
import sys
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles

class KatarengaGamePygame:
    def __init__(self, plateau, joueurs, pions=None, mode="1v1", noms_joueurs=None):
        pygame.init()
        self.screen = pygame.display.set_mode((700, 700))
        pygame.display.set_caption("Katarenga (Pygame)")
        self.clock = pygame.time.Clock()
        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]
        self.font = pygame.font.SysFont("Helvetica", 24)
        self.font_small = pygame.font.SysFont("Helvetica", 16)
        self.tour = 0
        self.selection = None
        self.coups_possibles = set()
        if pions is not None:
            self.pions = pions
        else:
            self.pions = {'X': {(0, j) for j in range(8)}, 'O': {(7, j) for j in range(8)}}
        self.timer_seconds = 0
        self.timer_running = True
        self.run()

    def draw(self):
        self.screen.fill((230, 242, 255))
        taille = 60
        colors = {'R': (255,153,153), 'J': (255,255,179), 'B': (153,204,255), 'V': (179,255,179)}
        for i in range(8):
            for j in range(8):
                fill = colors.get(self.plateau.cases[i][j], (255,255,255))
                rect = pygame.Rect(j*taille+50, i*taille+50, taille, taille)
                pygame.draw.rect(self.screen, fill, rect)
                pygame.draw.rect(self.screen, (0,0,0), rect, 2)
                for symbol, color in [('X', (0,0,0)), ('O', (255,255,255))]:
                    if (i, j) in self.pions[symbol]:
                        pygame.draw.circle(self.screen, color, rect.center, taille//2-8)
                if self.selection == (i, j):
                    pygame.draw.rect(self.screen, (0,0,255), rect, 3)
                if (i, j) in self.coups_possibles:
                    pygame.draw.circle(self.screen, (120,255,120), rect.center, 12)
        # Infos joueur
        joueur = self.joueurs[self.tour % 2]
        info = f"Tour de {self.noms_joueurs[self.tour % 2]} ({'Blanc' if joueur.symbole=='X' else 'Noir'})"
        info_surf = self.font.render(info, True, (0,77,64))
        self.screen.blit(info_surf, (50, 10))
        # Timer
        min_sec = f"{self.timer_seconds//60:02d}:{self.timer_seconds%60:02d}"
        timer_surf = self.font_small.render(min_sec, True, (0,77,64))
        self.screen.blit(timer_surf, (600, 20))
        # Bouton retour
        retour_rect = pygame.Rect(20, 650, 120, 40)
        pygame.draw.rect(self.screen, (76,175,80), retour_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0,0,0), retour_rect, 2, border_radius=12)
        retour_label = self.font_small.render("Retour menu", True, (255,255,255))
        self.screen.blit(retour_label, retour_label.get_rect(center=retour_rect.center))
        self.retour_rect = retour_rect
        # Bouton aide
        aide_rect = pygame.Rect(560, 650, 120, 40)
        pygame.draw.rect(self.screen, (76,175,80), aide_rect, border_radius=12)
        pygame.draw.rect(self.screen, (0,0,0), aide_rect, 2, border_radius=12)
        aide_label = self.font_small.render("Aide", True, (255,255,255))
        self.screen.blit(aide_label, aide_label.get_rect(center=aide_rect.center))
        self.aide_rect = aide_rect
        pygame.display.flip()

    def handle_click(self, pos):
        if self.retour_rect.collidepoint(pos):
            pygame.quit(); sys.exit()
        if self.aide_rect.collidepoint(pos):
            self.show_rules()
            return
        taille = 60
        for i in range(8):
            for j in range(8):
                rect = pygame.Rect(j*taille+50, i*taille+50, taille, taille)
                if rect.collidepoint(pos):
                    self.handle_board_click((i, j))
                    return

    def handle_board_click(self, position):
        joueur, symbole = self.joueurs[self.tour % 2], self.joueurs[self.tour % 2].symbole
        if self.selection is None:
            if position in self.pions[symbole]:
                self.selection = position
                couleur_depart = self.plateau.cases[self.selection[0]][self.selection[1]]
                self.coups_possibles = self.generer_coups_possibles(self.selection, couleur_depart, symbole)
        else:
            depart, arrivee = self.selection, position
            piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
            if arrivee in self.coups_possibles:
                if piece_arrivee and self.tour > 0:
                    self.pions[piece_arrivee].discard(arrivee)
                elif piece_arrivee:
                    return
                self.pions[symbole].discard(depart)
                self.pions[symbole].add(arrivee)
                self.tour += 1
                self.selection = None
                self.coups_possibles = set()
                self.check_victory()
            else:
                self.selection = None
                self.coups_possibles = set()

    def generer_coups_possibles(self, depart, couleur, symbole):
        coups = set()
        for i in range(8):
            for j in range(8):
                arrivee = (i, j)
                piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
                if piece_arrivee is None or piece_arrivee != symbole:
                    mouvement_valide = (couleur == 'B' and self.est_mouvement_roi(depart, arrivee)) or \
                                       (couleur == 'V' and self.est_mouvement_cavalier(depart, arrivee)) or \
                                       (couleur == 'J' and self.est_mouvement_fou(depart, arrivee)) or \
                                       (couleur == 'R' and self.est_mouvement_tour(depart, arrivee))
                    if mouvement_valide:
                        coups.add(arrivee)
        return coups

    def est_mouvement_roi(self, depart, arrivee):
        dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
        return dl <= 1 and dc <= 1 and (dl != 0 or dc != 0)

    def est_mouvement_cavalier(self, depart, arrivee):
        dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
        return (dl == 2 and dc == 1) or (dl == 1 and dc == 2)

    def est_mouvement_fou(self, depart, arrivee):
        if abs(arrivee[0] - depart[0]) != abs(arrivee[1] - depart[1]):
            return False
        sl = 1 if arrivee[0] > depart[0] else -1
        sc = 1 if arrivee[1] > depart[1] else -1
        l, c = depart[0] + sl, depart[1] + sc
        while (l, c) != arrivee:
            if not (0 <= l < 8 and 0 <= c < 8):
                return False
            if (l, c) in self.pions['X'] or (l, c) in self.pions['O']:
                return False
            l += sl
            c += sc
        return True

    def est_mouvement_tour(self, depart, arrivee):
        if depart[0] != arrivee[0] and depart[1] != arrivee[1]:
            return False
        sl = 0 if depart[0] == arrivee[0] else (1 if arrivee[0] > depart[0] else -1)
        sc = 0 if depart[1] == arrivee[1] else (1 if arrivee[1] > depart[1] else -1)
        l, c = depart[0] + sl, depart[1] + sc
        while (l, c) != arrivee:
            if not (0 <= l < 8 and 0 <= c < 8):
                return False
            if (l, c) in self.pions['X'] or (l, c) in self.pions['O']:
                return False
            l += sl
            c += sc
        return True

    def check_victory(self):
        joueur = self.joueurs[self.tour % 2]
        ligne_victoire = 7 if joueur.symbole == 'X' else 0
        if any(p[0] == ligne_victoire for p in self.pions[joueur.symbole]):
            print(f"Victoire de {self.noms_joueurs[self.tour % 2]} !")
            pygame.time.wait(2000)
            pygame.quit(); sys.exit()
        elif not self.pions['O' if joueur.symbole == 'X' else 'X']:
            print(f"Victoire de {self.noms_joueurs[self.tour % 2]} par capture !")
            pygame.time.wait(2000)
            pygame.quit(); sys.exit()

    def show_rules(self):
        print(get_regles("katarenga"))

    def run(self):
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                if event.type == pygame.USEREVENT and self.timer_running:
                    self.timer_seconds += 1
            self.draw()
            self.clock.tick(30)

# Pour test indépendant
if __name__ == '__main__':
    plateau = Plateau()
    joueurs = [Joueur("Joueur 1", 'O'), Joueur("Joueur 2", 'X')]
    KatarengaGamePygame(plateau, joueurs)