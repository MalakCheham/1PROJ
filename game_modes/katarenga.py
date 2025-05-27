import pygame
import os
from core.langues import translate, draw_flags
from core.musique import draw_volume_bar
from core.joueur import Joueur
from core.plateau import Plateau
from core.mouvement import generer_coups_possibles

class KatarengaGame:
    def __init__(self, plateau, external_screen=None):
        self.screen = external_screen or pygame.display.set_mode((1100, 850))
        self.plateau = plateau
        self.font = pygame.font.SysFont("Helvetica", 28)
        self.font_title = pygame.font.SysFont("Helvetica", 36, bold=True)
        self.font_small = pygame.font.SysFont("Helvetica", 20)
        self.muted = False
        self.finished = False
        self.tour = 0
        self.joueurs = [Joueur(0, 'X'), Joueur(1, 'O')]
        self.selection = None
        self.coups_possibles = set()
        self.pions = {'X': set(), 'O': set()}
        self.init_pions()
        self.header_height = 90
        self.bar_rect = pygame.Rect(40, self.screen.get_height()-60, 180, 18)
        self.icon_rect = pygame.Rect(4, self.screen.get_height()-65, 28, 28)
        self.flag_fr_rect = pygame.Rect(self.screen.get_width()-68, self.screen.get_height()-116, 44, 44)
        self.flag_uk_rect = pygame.Rect(self.screen.get_width()-68, self.screen.get_height()-68, 44, 44)

    def init_pions(self):
        for j in range(8):
            self.pions['X'].add((0, j))
            self.pions['O'].add((7, j))

    def draw(self):
        self.screen.fill((255, 248, 225))
        self.draw_header()
        self.draw_plateau()
        draw_volume_bar(self.screen, self.muted, pygame.mixer.music.get_volume(), self.bar_rect, self.icon_rect)
        draw_flags(self.screen, self.flag_fr_rect, self.flag_uk_rect)
        self.draw_info()
        pygame.display.flip()

    def draw_header(self):
        screen = self.screen
        header_height = self.header_height
        screen_w = screen.get_width()
        pygame.draw.rect(screen, (240, 238, 220), (0, 0, screen_w, header_height))
        pygame.draw.line(screen, (200, 200, 180), (0, header_height), (screen_w, header_height), 2)
        titre = self.font_title.render("Katarenga", 1, (0,77,64))
        screen.blit(titre, titre.get_rect(center=(screen_w//2, header_height//2)))

    def draw_plateau(self):
        screen = self.screen
        screen_w, screen_h = screen.get_width(), screen.get_height()
        header_height = self.header_height
        footer_height = 80
        zone_top = header_height
        zone_bottom = screen_h - footer_height
        zone_height = zone_bottom - zone_top
        zone_width = screen_w
        TEXTURE_DIR = os.path.join("assets", "textures")
        TEXTURE_FILES = {
            'R': "case-rouge.png",
            'B': "case-bleu.png",
            'V': "case-vert.png",
            'J': "case-jaune.png",
        }
        tile_textures = {}
        cadre_margin = 120  # Augmente la marge pour réduire la taille du cadre et du plateau
        cadre_w = min(zone_width, zone_height) - 2*cadre_margin
        cadre_h = cadre_w
        cell_size = cadre_w // 8
        try:
            cadre_img = pygame.image.load(os.path.join(TEXTURE_DIR, "cadre.png")).convert_alpha()
            cadre_img = pygame.transform.smoothscale(cadre_img, (cadre_w, cadre_h))
            cadre_ok = True
        except Exception:
            cadre_img = None
            cadre_ok = False
        offset_x = (zone_width - cadre_w) // 2
        offset_y = zone_top + (zone_height - cadre_h) // 2
        # --- Ajout du cadre autour du plateau ---
        if cadre_ok and cadre_img:
            screen.blit(cadre_img, (offset_x, offset_y))
        else:
            pygame.draw.rect(screen, (62, 30, 11), (offset_x, offset_y, cadre_w, cadre_h), 6)
        for k, fname in TEXTURE_FILES.items():
            try:
                surf = pygame.image.load(os.path.join(TEXTURE_DIR, fname)).convert_alpha()
                tile_textures[k] = pygame.transform.smoothscale(surf, (cell_size, cell_size))
            except Exception:
                tile_textures[k] = None
        px = offset_x
        py = offset_y
        for i in range(8):
            for j in range(8):
                val = self.plateau.cases[i][j]
                tex = tile_textures.get(val)
                rect = pygame.Rect(px + j*cell_size, py + i*cell_size, cell_size, cell_size)
                if tex:
                    screen.blit(tex, rect)
                else:
                    color = (220,220,220)
                    pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (62, 30, 11), rect, 1)
                # Pions
                if (i, j) in self.pions['X']:
                    pygame.draw.circle(screen, (0,0,0), rect.center, cell_size//3)
                elif (i, j) in self.pions['O']:
                    pygame.draw.circle(screen, (255,255,255), rect.center, cell_size//3)
                # Sélection visuelle claire
                if self.selection == (i, j):
                    pygame.draw.rect(screen, (255, 215, 0), rect, 6)  # surlignage épais jaune
                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)      # bord noir pour contraste
                # Coups possibles
                elif (i, j) in self.coups_possibles:
                    pygame.draw.rect(screen, (0, 200, 0), rect, 4)    # surlignage vert
                    pygame.draw.circle(screen, (0, 200, 0), rect.center, cell_size//8)  # petit point vert
        # --- Bouton retour (en haut à gauche du plateau) ---
        retour_size = 48
        retour_x = offset_x - retour_size - 24
        retour_y = offset_y + cadre_h//2 - retour_size//2
        self.retour_rect = pygame.Rect(retour_x, retour_y, retour_size, retour_size)
        try:
            retour_img = pygame.image.load(os.path.join("assets", "en-arriere.png")).convert_alpha()
            retour_img = pygame.transform.smoothscale(retour_img, (retour_size, retour_size))
            screen.blit(retour_img, (retour_x, retour_y))
        except Exception:
            pygame.draw.rect(screen, (180, 180, 180), self.retour_rect)
            pygame.draw.polygon(screen, (80, 80, 80), [
                (retour_x+36, retour_y+12), (retour_x+12, retour_y+24), (retour_x+36, retour_y+36)
            ])

    def draw_info(self):
        joueur = self.joueurs[self.tour % 2]
        info = f"Tour: {self.tour+1} | Joueur: {'Noir' if joueur.symbole == 'X' else 'Blanc'}"
        info_render = self.font_small.render(info, True, (0,0,0))
        self.screen.blit(info_render, (40, self.header_height + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
            # Bouton retour
            if hasattr(self, 'retour_rect') and self.retour_rect.collidepoint(event.pos):
                # Revenir au menu choix jeux (PAGE_CHOICE_GAME)
                from gui import menu_gui
                if hasattr(self, 'screen'):
                    # On réutilise la fenêtre pygame existante
                    self.finished = True
                    menu_gui.PAGE_CHOICE_GAME  # pour l'import
                return
            # Volume/langues (utilise les fonctions globales)
            if self.bar_rect.collidepoint(event.pos):
                v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                pygame.mixer.music.set_volume(v)
                self.muted = (v == 0)
                return
            if self.icon_rect.collidepoint(event.pos):
                if not self.muted:
                    self.last_volume = pygame.mixer.music.get_volume()
                    pygame.mixer.music.set_volume(0.0)
                    self.muted = True
                else:
                    pygame.mixer.music.set_volume(getattr(self, 'last_volume', 0.5))
                    self.muted = False
                return
            if self.flag_fr_rect.collidepoint(event.pos):
                from core.parametres import set_language
                set_language("fr")
                pygame.time.wait(120)
                return
            if self.flag_uk_rect.collidepoint(event.pos):
                from core.parametres import set_language
                set_language("en")
                pygame.time.wait(120)
                return
            # Plateau (corrigé pour bien détecter la zone du plateau)
            screen_w, screen_h = self.screen.get_width(), self.screen.get_height()
            header_height = self.header_height
            footer_height = 80
            zone_top = header_height
            zone_bottom = screen_h - footer_height
            zone_height = zone_bottom - zone_top
            zone_width = screen_w
            cadre_margin = 120  # Augmente la marge pour réduire la taille du cadre et du plateau
            cadre_w = min(zone_width, zone_height) - 2*cadre_margin
            cadre_h = cadre_w
            cell_size = cadre_w // 8
            offset_x = (zone_width - cadre_w) // 2
            offset_y = zone_top + (zone_height - cadre_h) // 2
            px = offset_x
            py = offset_y
            for i in range(8):
                for j in range(8):
                    rect = pygame.Rect(px + j*cell_size, py + i*cell_size, cell_size, cell_size)
                    if rect.collidepoint(event.pos):
                        self.handle_board_click((i, j))
                        self.draw()  # Redessine pour feedback immédiat
                        return
        return self.finished

    def handle_board_click(self, pos):
        joueur, symbole = self.joueurs[self.tour % 2], self.joueurs[self.tour % 2].symbole
        if self.selection is None:
            # Seul le joueur courant peut sélectionner ses propres pions
            if pos in self.pions[symbole]:
                self.selection = pos
                couleur_depart = self.plateau.cases[self.selection[0]][self.selection[1]]
                self.coups_possibles = generer_coups_possibles(self.selection, couleur_depart, symbole, self.plateau, self.pions)
                self.draw()  # Redessine pour feedback immédiat
        else:
            depart, arrivee = self.selection, pos
            piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
            if arrivee in self.coups_possibles:
                if piece_arrivee and self.tour > 0:
                    self.pions[piece_arrivee].discard(arrivee)
                elif piece_arrivee:
                    self.selection = None
                    self.coups_possibles = set()
                    self.draw()
                    return
                self.pions[symbole].discard(depart)
                self.pions[symbole].add(arrivee)
                self.tour += 1
                self.selection = None
                self.coups_possibles = set()
                self.draw()
                # TODO: gérer la victoire selon les règles
            else:
                self.selection = None
                self.coups_possibles = set()
                self.draw()
