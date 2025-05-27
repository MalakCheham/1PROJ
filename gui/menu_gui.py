import pygame, sys, os
import math
import random
from core.parametres import set_language
from core.langues import translate, draw_flags, draw_hover_shadow
from core.musique import init_audio, draw_volume_bar
from core.quadrants import generer_plateau_automatique
from gui.utils.plateau_preview import draw_plateau_preview
from gui.utils.game_config import draw_config_jeu
from gui.utils.choice_game import draw_choice_game
from gui.utils.ui_common import draw_custom_board

PAGE_HOME = "home"
PAGE_CHOICE_GAME = "choice_game"
PAGE_CONFIG_GAME = "config_game"
PAGE_PREVIEW_GAME = "preview_game"
PAGE_CUSTOM_BOARD = "custom_board"
PAGE_GAME = "game"

MODES_JEU = [
    {
        "id": "katarenga",
        "titre": "Katarenga",
        "image": os.path.join("assets", "congress.png"),
        "desc": "Un mode de jeu inspiré du shogi et des échecs.",
    },
    {
        "id": "congress",
        "titre": "Congress",
        "image": os.path.join("assets", "congress.png"),
        "desc": "Un mode de réflexion où chaque coup compte.",
    },
    {
        "id": "isolation",
        "titre": "Isolation",
        "image": os.path.join("assets", "congress.png"),
        "desc": "Un mode duel tactique pour isoler l'adversaire.",
    },
]

class PortailGame:
    """
    Fonctionnalité principale du portail d'accueil du jeu.
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Portail d'accueil du jeu")
        pygame.display.set_icon(pygame.image.load(os.path.join("assets", "logo.png")))
        
        self.screen = pygame.display.set_mode((1100, 850))
        self.font = pygame.font.SysFont("Helvetica", 28)
        self.font_small = pygame.font.SysFont("Helvetica", 20)
        self.font_title = pygame.font.SysFont("Helvetica", 36, bold=True)
        self.logo = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets", "logo.png")), (300, 300))
        self.username = ""
        self.input_active = False
        self.muted = False
        self.last_volume = init_audio()
        self.page = PAGE_HOME
        self.clock = pygame.time.Clock()
        self.custom_board_state = {
            "grille": [[None for _ in range(4)] for _ in range(4)],
            "current_color": "R",
            "quadrants": [],
            "info_text": "Quadrant 1/4"
        }
        self.run()
    
    """
    Affiche l'écran d'accueil du portail avec le logo, les drapeaux de langue
    """
    def draw_accueil(self):
        screen = self.screen
        screen.fill((249,246,227))
        cx = screen.get_width()//2
        screen.blit(self.logo, self.logo.get_rect(center=(cx,220)))
        flag_size, margin = 44, 24
        self.flag_fr_rect = pygame.Rect(screen.get_width()-flag_size-margin, screen.get_height()-2*flag_size-margin-8, flag_size, flag_size)
        self.flag_uk_rect = pygame.Rect(screen.get_width()-flag_size-margin, screen.get_height()-flag_size-margin, flag_size, flag_size)
        draw_flags(screen, self.flag_fr_rect, self.flag_uk_rect)
        titre = self.font_title.render(translate("bienvenue_portail"), 1, (0,77,64))
        screen.blit(titre, titre.get_rect(center=(cx,370)))
        saisie = self.font.render(translate("entrez_nom_utilisateur"), 1, (0,0,0))
        screen.blit(saisie, saisie.get_rect(center=(cx,430)))
        self.input_rect = pygame.Rect(cx-150,480,300,45)
        pygame.draw.rect(screen, (255,255,255), self.input_rect, border_radius=16)
        pygame.draw.rect(screen, (0,0,0), self.input_rect, 2, border_radius=16)
        user_text = self.font_small.render(self.username, 1, (0,0,0))
        screen.blit(user_text, user_text.get_rect(x=self.input_rect.x+10, centery=self.input_rect.centery))
        if self.input_active:
            x = self.input_rect.x+10+user_text.get_width()+2
            y = self.input_rect.y+8
            if (pygame.time.get_ticks()//500)%2==0:
                pygame.draw.rect(screen, (0,77,64), (x, y, 3, self.input_rect.height-16), border_radius=2)
        self.btn_rect = pygame.Rect(cx-175,560,350,65)
        btn_hovered = self.btn_rect.collidepoint(pygame.mouse.get_pos())
        color = (66,155,70) if btn_hovered else (76,175,80)
        btn_draw_rect = self.btn_rect.copy(); btn_draw_rect.y -= 2 if btn_hovered else 0
        if btn_hovered:
            draw_hover_shadow(screen, self.btn_rect, color=(76,175,80,38), offset=6, border_radius=22)
        pygame.draw.rect(screen, color, btn_draw_rect, border_radius=22)
        pygame.draw.rect(screen, (0,0,0), btn_draw_rect, 2, border_radius=22)
        btn_label = self.font.render(translate("entrez_portail"), 1, (255,255,255))
        screen.blit(btn_label, btn_label.get_rect(center=btn_draw_rect.center))
        self.bar_rect = pygame.Rect(40, screen.get_height()-60, 180, 18)
        self.icon_rect = pygame.Rect(4, screen.get_height()-65, 28, 28)
        draw_volume_bar(screen, self.muted, pygame.mixer.music.get_volume(), self.bar_rect, self.icon_rect)
    
    """
    Affiche l'en-tête commun avec logo
    """
    def draw_header(self):
        screen = self.screen
        header_height = 90
        screen_w = screen.get_width()
        # Fond header
        pygame.draw.rect(screen, (240, 238, 220), (0, 0, screen_w, header_height))
        pygame.draw.line(screen, (200, 200, 180), (0, header_height), (screen_w, header_height), 2)
        # Logo à gauche
        logo_size = self.font_title.get_height() + 10
        logo_img = pygame.transform.smoothscale(self.logo, (logo_size, logo_size))
        screen.blit(logo_img, (30, header_height//2 - logo_size//2))
        # Titre
        titre = self.font_title.render(f"{translate('bienvenue')} {self.username}", 1, (0,77,64))
        titre_rect = titre.get_rect()
        titre_rect.centery = header_height//2
        titre_rect.x = 50 + logo_size
        screen.blit(titre, titre_rect)
        # Bouton cercle lyrique à droite
        circle_radius = logo_size // 2
        circle_x = screen_w - 40 - circle_radius
        circle_y = header_height//2
        mouse_pos = pygame.mouse.get_pos()
        lyrique_hovered = (circle_x - mouse_pos[0])**2 + (circle_y - mouse_pos[1])**2 <= circle_radius**2
        # Animation hover (halo + translation)
        draw_circle_rect = pygame.Rect(circle_x-circle_radius, circle_y-circle_radius, 2*circle_radius, 2*circle_radius)
        if lyrique_hovered:
            halo = pygame.Surface((2*circle_radius+12, 2*circle_radius+12), pygame.SRCALPHA)
            pygame.draw.ellipse(halo, (76,175,80,38), halo.get_rect())
            screen.blit(halo, (draw_circle_rect.x-6, draw_circle_rect.y-6))
            draw_circle_rect.y -= 2
        pygame.draw.circle(screen, (220, 230, 240), draw_circle_rect.center, circle_radius)
        pygame.draw.circle(screen, (0, 77, 64), draw_circle_rect.center, circle_radius, 2)
        try:
            lyrique_img = pygame.image.load(os.path.join("assets", "lyrique.png"))
            lyrique_img = pygame.transform.smoothscale(lyrique_img, (logo_size-8, logo_size-8))
            screen.blit(lyrique_img, (draw_circle_rect.centerx - (logo_size-8)//2, draw_circle_rect.centery - (logo_size-8)//2))
        except:
            pass
        self.lyrique_circle = (draw_circle_rect.centerx, draw_circle_rect.centery, circle_radius)
        # Affichage du sous-menu déconnexion si besoin
        mouse_pos = pygame.mouse.get_pos()
        lyrique_hovered = (circle_x - mouse_pos[0])**2 + (circle_y - mouse_pos[1])**2 <= circle_radius**2
        if getattr(self, 'show_logout_menu', False):
            logout_label = self.font_small.render(translate("se_deconnecter"), True, (0,77,64))
            w, h = logout_label.get_size()
            menu_rect = pygame.Rect(circle_x - w - 16, circle_y + circle_radius + 10, w + 32, h + 16)
            pygame.draw.rect(screen, (255,255,255), menu_rect, border_radius=8)
            pygame.draw.rect(screen, (0,77,64), menu_rect, 2, border_radius=8)
            screen.blit(logout_label, logout_label.get_rect(center=menu_rect.center))
            self.logout_rect = menu_rect
        else:
            self.logout_rect = None

    """
    Affiche le menu de choix du jeu
    """
    def draw_choix_jeu(self):
        self.screen.fill((249,246,227))
        self.mode_btn_rects = draw_choice_game(
            self.screen,
            self.font,
            self.font_small,
            self.font_title,
            MODES_JEU,
            self.muted,
            self.bar_rect,
            self.icon_rect,
            self.flag_fr_rect,
            self.flag_uk_rect,
            header_func=self.draw_header
        )
    
    """
    Affiche la page de configuration du jeu
    """
    def draw_config_jeu(self, mode_id):
        self.screen.fill((249,246,227))
        self.btn_retour_rect = None
        self.btn_jouer_rect = None
        self.plateau_radio_rects = []
        self.help_icon_rect = None
        self.help_close_rect = None
        rects = draw_config_jeu(
            self.screen,
            self.font,
            self.font_small,
            self.font_title,
            mode_id,
            getattr(self, 'selected_plateau', 'auto'),
            getattr(self, 'show_help_menu', False),
            getattr(self, 'help_close_rect', None),
            getattr(self, 'show_logout_menu', False),
            getattr(self, 'logout_rect', None),
            self.muted,
            self.bar_rect,
            self.icon_rect,
            self.flag_fr_rect,
            self.flag_uk_rect,
            header_func=self.draw_header
        )
        self.btn_retour_rect = rects['btn_retour_rect']
        self.btn_jouer_rect = rects['btn_jouer_rect']
        self.plateau_radio_rects = rects['plateau_radio_rects']
        self.help_icon_rect = rects['help_icon_rect']
        self.help_close_rect = rects['help_close_rect']
    
    """
    Affiche la prévisualisation du plateau généré
    """
    def draw_preview_game(self):
        self.screen.fill((249,246,227))
        self.preview_btn_retour_rect = draw_plateau_preview(
            self.screen,
            self.font_title,
            self.font_small,
            self.preview_plateau,
            self.muted,
            None, None, None, None,
            header_func=self.draw_header
        )
    
    """
    Affiche l'éditeur de quadrants personnalisés
    """
    def draw_custom_board(self):
        self.screen.fill((249,246,227))
        # Affiche l'éditeur de quadrants personnalisés mutualisé
        res = draw_custom_board(
            self.screen,
            self.font,
            self.font_small,
            self.font_title,
            self.muted,
            self.bar_rect,
            self.icon_rect,
            self.flag_fr_rect,
            self.flag_uk_rect,
            header_func=self.draw_header,
            editor_state=self.custom_board_state,
            show_logout_menu=getattr(self, 'show_logout_menu', False),
            logout_rect=getattr(self, 'logout_rect', None)
        )
        self.custom_btns = res["btn_rects"]
        self.custom_palette_rects = res["palette_rects"]
        self.custom_grid_rect = res["grid_rect"]
        self.custom_retour_rect = res["retour_rect"]

    """
    Gestion des événements
    """
    def handle_event(self, event):
        if self.page == PAGE_HOME:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
                if self.flag_fr_rect.collidepoint(event.pos): set_language("fr"); pygame.time.wait(120)
                if self.flag_uk_rect.collidepoint(event.pos): set_language("en"); pygame.time.wait(120)
                if self.input_rect.collidepoint(event.pos): self.input_active = True
                else: self.input_active = False
                if self.btn_rect.collidepoint(event.pos) and self.username.strip():
                    self.page = PAGE_CHOICE_GAME
                    return
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
                if self.icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume(); pygame.mixer.music.set_volume(0.0); self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5); self.muted = False
            elif event.type == pygame.MOUSEMOTION and hasattr(event, 'pos') and event.buttons[0]:
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
        elif self.page == PAGE_CHOICE_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):

                if hasattr(self, 'lyrique_circle'):
                    x, y, r = self.lyrique_circle
                    if (event.pos[0]-x)**2 + (event.pos[1]-y)**2 <= r**2:
                        self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
                        return

                if getattr(self, 'show_logout_menu', False) and getattr(self, 'logout_rect', None):
                    if self.logout_rect.collidepoint(event.pos):
                        self.page = PAGE_HOME
                        self.show_logout_menu = False
                        return
                    else:
                        self.show_logout_menu = False
                        return

                if getattr(self, 'show_logout_menu', False):
                    self.show_logout_menu = False
                    return
                for btn_rect, mode_id in getattr(self, 'mode_btn_rects', []):
                    if btn_rect.collidepoint(event.pos):
                        self.selected_mode = mode_id
                        self.page = PAGE_CONFIG_GAME
                        return
                if self.flag_fr_rect.collidepoint(event.pos): set_language("fr"); pygame.time.wait(120)
                if self.flag_uk_rect.collidepoint(event.pos): set_language("en"); pygame.time.wait(120)
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
                if self.icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume(); pygame.mixer.music.set_volume(0.0); self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5); self.muted = False
            elif event.type == pygame.MOUSEMOTION and hasattr(event, 'pos') and event.buttons[0]:
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
        
        elif self.page == PAGE_CONFIG_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
                # Gestion du bouton cercle lyrique
                if hasattr(self, 'lyrique_circle'):
                    x, y, r = self.lyrique_circle
                    if (event.pos[0]-x)**2 + (event.pos[1]-y)**2 <= r**2:
                        self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
                        return
                # Gestion du sous-menu déconnexion
                if getattr(self, 'show_logout_menu', False) and getattr(self, 'logout_rect', None):
                    if self.logout_rect.collidepoint(event.pos):
                        self.page = PAGE_HOME
                        self.show_logout_menu = False
                        return
                    else:
                        self.show_logout_menu = False
                        return
                if getattr(self, 'show_logout_menu', False):
                    self.show_logout_menu = False
                    return
                # Icône d'aide
                if hasattr(self, 'help_icon_rect') and self.help_icon_rect.collidepoint(event.pos):
                    self.show_help_menu = True
                    return
                # Fermer l'aide
                if getattr(self, 'show_help_menu', False) and getattr(self, 'help_close_rect', None):
                    if self.help_close_rect.collidepoint(event.pos):
                        self.show_help_menu = False
                        return
                if getattr(self, 'show_help_menu', False):
                    # Si clic ailleurs que sur la popup, on ferme
                    if not self.help_close_rect or not self.help_close_rect.collidepoint(event.pos):
                        popup_rect = pygame.Rect(self.help_close_rect.x-442, self.help_close_rect.y-44, 480, 320)
                        if not popup_rect.collidepoint(event.pos):
                            self.show_help_menu = False
                            return
                # Bouton retour
                if hasattr(self, 'btn_retour_rect') and self.btn_retour_rect.collidepoint(event.pos):
                    self.page = PAGE_CHOICE_GAME
                    return
                # Bouton jouer
                if hasattr(self, 'btn_jouer_rect') and self.btn_jouer_rect.collidepoint(event.pos):
                    if getattr(self, 'selected_plateau', 'auto') == 'perso':
                        # Passage à l'éditeur de quadrants personnalisés
                        self.custom_board_state = {
                            "grille": [[None for _ in range(4)] for _ in range(4)],
                            "current_color": "R",
                            "quadrants": [],
                            "info_text": "Quadrant 1/4"
                        }
                        self.page = PAGE_CUSTOM_BOARD
                        return
                    else:
                        from core.plateau import Plateau
                        plateau = Plateau()
                        plateau.cases = generer_plateau_automatique()
                        self.preview_plateau = plateau
                        self.preview_pions = None
                        self.page = PAGE_PREVIEW_GAME
                        return
                # Radio boutons plateau
                for rect, value in getattr(self, 'plateau_radio_rects', []):
                    if rect.collidepoint(event.pos):
                        self.selected_plateau = value
                        return
                if self.flag_fr_rect.collidepoint(event.pos): set_language("fr"); pygame.time.wait(120)
                if self.flag_uk_rect.collidepoint(event.pos): set_language("en"); pygame.time.wait(120)
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
                if self.icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume(); pygame.mixer.music.set_volume(0.0); self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5); self.muted = False
            elif event.type == pygame.MOUSEMOTION and hasattr(event, 'pos') and event.buttons[0]:
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
        
        elif self.page == PAGE_PREVIEW_GAME:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
                # Gestion du bouton cercle lyrique
                if hasattr(self, 'lyrique_circle'):
                    x, y, r = self.lyrique_circle
                    if (event.pos[0]-x)**2 + (event.pos[1]-y)**2 <= r**2:
                        self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
                        return
                # Gestion du sous-menu déconnexion
                if getattr(self, 'show_logout_menu', False) and getattr(self, 'logout_rect', None):
                    if self.logout_rect.collidepoint(event.pos):
                        self.page = PAGE_HOME
                        self.show_logout_menu = False
                        return
                    else:
                        self.show_logout_menu = False
                        return
                if getattr(self, 'show_logout_menu', False):
                    self.show_logout_menu = False
                    return
                # Bouton retour
                if hasattr(self, 'preview_btn_retour_rect') and self.preview_btn_retour_rect.collidepoint(event.pos):
                    self.page = PAGE_CONFIG_GAME
                    return
                # Volume et langues
                if self.flag_fr_rect.collidepoint(event.pos): set_language("fr"); pygame.time.wait(120)
                if self.flag_uk_rect.collidepoint(event.pos): set_language("en"); pygame.time.wait(120)
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
                if self.icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume(); pygame.mixer.music.set_volume(0.0); self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5); self.muted = False
            elif event.type == pygame.MOUSEMOTION and hasattr(event, 'pos') and event.buttons[0]:
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
        elif self.page == PAGE_CUSTOM_BOARD:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
                # Gestion du bouton cercle lyrique
                if hasattr(self, 'lyrique_circle'):
                    x, y, r = self.lyrique_circle
                    if (event.pos[0]-x)**2 + (event.pos[1]-y)**2 <= r**2:
                        self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
                        return
                # Gestion du sous-menu déconnexion (affiché uniquement si lyrique_hovered)
                # On ne traite le logout_rect que si show_logout_menu est actif, sinon on ne fait rien
                if getattr(self, 'show_logout_menu', False) and getattr(self, 'logout_rect', None):
                    if self.logout_rect.collidepoint(event.pos):
                        self.page = PAGE_HOME
                        self.show_logout_menu = False
                        return
                    else:
                        self.show_logout_menu = False
                        return
                # Palette couleurs
                for x, y, w, h, c in getattr(self, 'custom_palette_rects', []):
                    rect = pygame.Rect(x, y, w, h)
                    if rect.collidepoint(event.pos):
                        self.custom_board_state["current_color"] = c
                        return
                # Grille 4x4
                grid_x, grid_y, cell_size = self.custom_grid_rect
                for i in range(4):
                    for j in range(4):
                        rect = pygame.Rect(grid_x + j*cell_size, grid_y + i*cell_size, cell_size, cell_size)
                        if rect.collidepoint(event.pos):
                            self.custom_board_state["grille"][i][j] = self.custom_board_state["current_color"]
                            return
                # Boutons
                for key, rect in getattr(self, 'custom_btns', {}).items():
                    if rect.collidepoint(event.pos):
                        if key == "sauvegarder_quadrant":
                            if any(None in row for row in self.custom_board_state["grille"]):
                                self.custom_board_state["info_text"] = "Toutes les cases doivent être colorées."
                                return
                            self.custom_board_state["quadrants"].append({"recto": [row[:] for row in self.custom_board_state["grille"]]})
                            if len(self.custom_board_state["quadrants"]) == 4:
                                self.custom_board_state["info_text"] = "Les 4 quadrants sont prêts. Cliquez sur 'Jouer avec ces quadrants'."
                            else:
                                self.custom_board_state["grille"] = [[None for _ in range(4)] for _ in range(4)]
                                self.custom_board_state["info_text"] = f"Quadrant {len(self.custom_board_state['quadrants'])+1}/4"
                            return
                        elif key == "nouveau_quadrant":
                            self.custom_board_state["grille"] = [[None for _ in range(4)] for _ in range(4)]
                            return
                        elif key == "jouer_quadrants":
                            if len(self.custom_board_state["quadrants"]) != 4:
                                self.custom_board_state["info_text"] = "Il faut 4 quadrants pour jouer."
                                return
                            from core.plateau import Plateau
                            plateau = Plateau()
                            positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
                            for i, q in enumerate(self.custom_board_state["quadrants"]):
                                bloc = q["recto"]
                                for dx in range(4):
                                    for dy in range(4):
                                        plateau.cases[positions[i][0] + dx][positions[i][1] + dy] = bloc[dx][dy]
                            self.preview_plateau = plateau
                            self.preview_pions = None
                            self.page = PAGE_PREVIEW_GAME
                            return
                # Bouton retour
                if self.custom_retour_rect and self.custom_retour_rect.collidepoint(event.pos):
                    self.page = PAGE_CONFIG_GAME
                    return
                # Volume/langues
                if self.flag_fr_rect.collidepoint(event.pos): set_language("fr"); pygame.time.wait(120)
                if self.flag_uk_rect.collidepoint(event.pos): set_language("en"); pygame.time.wait(120)
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
                if self.icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume(); pygame.mixer.music.set_volume(0.0); self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5); self.muted = False
            elif event.type == pygame.MOUSEMOTION and hasattr(event, 'pos') and event.buttons[0]:
                if self.bar_rect.collidepoint(event.pos):
                    v = min(max((event.pos[0]-self.bar_rect.x)/self.bar_rect.width,0),1)
                    pygame.mixer.music.set_volume(v); self.last_volume = v; self.muted = False
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE: self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN and self.username.strip(): pass
            elif len(self.username)<20 and event.unicode.isprintable(): self.username += event.unicode
            return

    """ 
    Boucle principale
    """
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.handle_event(event)
            if self.page == PAGE_HOME:
                self.draw_accueil()
            elif self.page == PAGE_CHOICE_GAME:
                self.draw_choix_jeu()
            elif self.page == PAGE_CONFIG_GAME:
                self.draw_config_jeu(getattr(self, 'selected_mode', None))
            elif self.page == PAGE_PREVIEW_GAME:
                self.draw_preview_game()
            elif self.page == PAGE_CUSTOM_BOARD:
                self.draw_custom_board()
            pygame.display.flip(); self.clock.tick(30)


if __name__ == "__main__": 
    PortailGame()
