import pygame, sys, os
import math
from core.parametres import set_language
from core.langues import translate, draw_flags, draw_hover_shadow
from core.musique import jouer_musique, init_audio, draw_volume_bar

PAGE_ACCUEIL = "accueil"
PAGE_CHOIX_JEU = "choix_jeu"
PAGE_CONFIG_JEU = "config_game"

# --- Données des modes de jeu ---
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
        self.page = PAGE_ACCUEIL
        self.clock = pygame.time.Clock()
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
        screen = self.screen
        screen.fill((249,246,227))
        self.draw_header()
        cx = screen.get_width()//2
        # Titre principal et sous-titre (depuis traductions)
        titre_modes = translate("sous_titre_modes")
        sous_titre = translate("choisissez_mode_jeu")
        titre_font = pygame.font.SysFont("Helvetica", 28, bold=True)
        titre_render = titre_font.render(titre_modes, 1, (0,77,64))
        sous_titre_render = self.font_small.render(sous_titre, 1, (0,0,0))
        screen.blit(titre_render, titre_render.get_rect(center=(cx, 150)))
        screen.blit(sous_titre_render, sous_titre_render.get_rect(center=(cx, 190)))
        # Modes de jeu
        card_w, card_h = 300, 340
        spacing = 40
        total_w = len(MODES_JEU)*card_w + (len(MODES_JEU)-1)*spacing
        start_x = (screen.get_width()-total_w)//2
        y = 230  # Décalage sous header + titres
        self.mode_btn_rects = []
        mouse_pos = pygame.mouse.get_pos()
        for i, mode in enumerate(MODES_JEU):
            x = start_x + i*(card_w+spacing)
            # Carte
            card_rect = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(screen, (255,255,255), card_rect, border_radius=18)
            pygame.draw.rect(screen, (0,77,64), card_rect, 2, border_radius=18)
            # Image
            try:
                img = pygame.transform.smoothscale(pygame.image.load(mode["image"]), (card_w-40, 120))
                screen.blit(img, (x+20, y+20))
            except:
                pass
            # Titre (depuis traductions)
            titre_mod = translate(f"mode_{mode['id']}")
            screen.blit(self.font.render(titre_mod, 1, (0,51,102)), (x+20, y+150))
            # Desc (depuis traductions)
            desc_mod = translate(f"desc_{mode['id']}")
            # Découpage intelligent pour ne pas dépasser la largeur de la carte
            def wrap_text(text, font, max_width):
                words = text.split()
                lines = []
                current = ""
                for word in words:
                    test = current + (" " if current else "") + word
                    if font.size(test)[0] <= card_w-40:
                        current = test
                    else:
                        if current:
                            lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                return lines
            desc_lines = wrap_text(desc_mod, self.font_small, card_w-40)
            for j, line in enumerate(desc_lines):
                screen.blit(self.font_small.render(line, 1, (0,0,0)), (x+20, y+190+j*24))
            # Bouton jouer
            btn_rect = pygame.Rect(x+card_w//2-60, y+card_h-70, 120, 44)
            btn_hovered = btn_rect.collidepoint(mouse_pos)
            color = (66,155,70) if btn_hovered else (76,175,80)
            btn_draw_rect = btn_rect.copy(); btn_draw_rect.y -= 2 if btn_hovered else 0
            if btn_hovered:
                draw_hover_shadow(screen, btn_rect, color=(76,175,80,38), offset=6, border_radius=14)
            pygame.draw.rect(screen, color, btn_draw_rect, border_radius=14)
            pygame.draw.rect(screen, (0,0,0), btn_draw_rect, 2, border_radius=14)
            btn_label = self.font_small.render(translate("lancer_ce_mode"), 1, (255,255,255))
            screen.blit(btn_label, btn_label.get_rect(center=btn_draw_rect.center))
            self.mode_btn_rects.append((btn_rect, mode["id"]))
        
        self.bar_rect = pygame.Rect(40, screen.get_height()-60, 180, 18)
        self.icon_rect = pygame.Rect(4, screen.get_height()-65, 28, 28)
        flag_size, margin = 44, 24
        self.flag_fr_rect = pygame.Rect(screen.get_width()-flag_size-margin, screen.get_height()-2*flag_size-margin-8, flag_size, flag_size)
        self.flag_uk_rect = pygame.Rect(screen.get_width()-flag_size-margin, screen.get_height()-flag_size-margin, flag_size, flag_size)
        draw_flags(screen, self.flag_fr_rect, self.flag_uk_rect)
        draw_volume_bar(screen, self.muted, pygame.mixer.music.get_volume(), self.bar_rect, self.icon_rect)
    
    """
    Affiche la page de configuration du jeu
    """
    def draw_config_jeu(self, mode_id):
        screen = self.screen
        screen.fill((249,246,227))
        self.draw_header()
        cx = screen.get_width()//2
        # Titre de la page
        mode_label = translate(f"mode_{mode_id}") if mode_id else ""
        titre = self.font_title.render(f"{translate('configuration_du_jeu')} : {mode_label}", 1, (0,77,64))
        screen.blit(titre, titre.get_rect(center=(cx, 140)))
        # 1ère ZONE : Mode de jeu
        zone1_rect = pygame.Rect(cx-320, 210, 640, 120)
        pygame.draw.rect(screen, (255,255,255), zone1_rect, border_radius=18)
        pygame.draw.rect(screen, (0,77,64), zone1_rect, 2, border_radius=18)
        label1 = self.font.render(translate("mode_de_jeu"), 1, (0,51,102))
        screen.blit(label1, (zone1_rect.x+30, zone1_rect.y+30))
        # 2ème ZONE : Configuration du plateau
        zone2_rect = pygame.Rect(cx-320, 360, 640, 220)
        pygame.draw.rect(screen, (255,255,255), zone2_rect, border_radius=18)
        pygame.draw.rect(screen, (0,77,64), zone2_rect, 2, border_radius=18)
        label2 = self.font.render(translate("plateau"), 1, (0,51,102))
        screen.blit(label2, (zone2_rect.x+30, zone2_rect.y+30))
        # Bouton retour centré en bas + bouton jouer à droite
        btn_retour = pygame.Rect(cx-130, zone2_rect.y+zone2_rect.height+40, 120, 44)
        btn_jouer = pygame.Rect(cx+10, zone2_rect.y+zone2_rect.height+40, 120, 44)
        mouse_pos = pygame.mouse.get_pos()
        retour_hovered = btn_retour.collidepoint(mouse_pos)
        jouer_hovered = btn_jouer.collidepoint(mouse_pos)
        color_retour = (66,155,70) if retour_hovered else (76,175,80)
        color_jouer = (66,155,70) if jouer_hovered else (76,175,80)
        btn_retour_draw = btn_retour.copy(); btn_retour_draw.y -= 2 if retour_hovered else 0
        btn_jouer_draw = btn_jouer.copy(); btn_jouer_draw.y -= 2 if jouer_hovered else 0
        if retour_hovered:
            draw_hover_shadow(screen, btn_retour, color=(76,175,80,38), offset=6, border_radius=14)
        if jouer_hovered:
            draw_hover_shadow(screen, btn_jouer, color=(76,175,80,38), offset=6, border_radius=14)
        pygame.draw.rect(screen, color_retour, btn_retour_draw, border_radius=14)
        pygame.draw.rect(screen, (0,0,0), btn_retour_draw, 2, border_radius=14)
        pygame.draw.rect(screen, color_jouer, btn_jouer_draw, border_radius=14)
        pygame.draw.rect(screen, (0,0,0), btn_jouer_draw, 2, border_radius=14)
        btn_label_retour = self.font_small.render(translate("retour"), 1, (255,255,255))
        btn_label_jouer = self.font_small.render(translate("lancer_ce_mode"), 1, (255,255,255))
        screen.blit(btn_label_retour, btn_label_retour.get_rect(center=btn_retour_draw.center))
        screen.blit(btn_label_jouer, btn_label_jouer.get_rect(center=btn_jouer_draw.center))
        self.btn_retour_rect = btn_retour
        self.btn_jouer_rect = btn_jouer
        # Volume et langues
        self.bar_rect = pygame.Rect(40, screen.get_height()-60, 180, 18)
        self.icon_rect = pygame.Rect(4, screen.get_height()-65, 28, 28)
        flag_size, margin = 44, 24
        self.flag_fr_rect = pygame.Rect(screen.get_width()-flag_size-margin, screen.get_height()-2*flag_size-margin-8, flag_size, flag_size)
        self.flag_uk_rect = pygame.Rect(screen.get_width()-flag_size-margin, screen.get_height()-flag_size-margin, flag_size, flag_size)
        draw_flags(screen, self.flag_fr_rect, self.flag_uk_rect)
        draw_volume_bar(screen, self.muted, pygame.mixer.music.get_volume(), self.bar_rect, self.icon_rect)

    """
    Gestion des événements
    """
    def handle_event(self, event):
        if self.page == PAGE_ACCUEIL:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):
                if self.flag_fr_rect.collidepoint(event.pos): set_language("fr"); pygame.time.wait(120)
                if self.flag_uk_rect.collidepoint(event.pos): set_language("en"); pygame.time.wait(120)
                if self.input_rect.collidepoint(event.pos): self.input_active = True
                else: self.input_active = False
                if self.btn_rect.collidepoint(event.pos) and self.username.strip():
                    self.page = PAGE_CHOIX_JEU
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
        elif self.page == PAGE_CHOIX_JEU:
            if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'pos'):

                if hasattr(self, 'lyrique_circle'):
                    x, y, r = self.lyrique_circle
                    if (event.pos[0]-x)**2 + (event.pos[1]-y)**2 <= r**2:
                        self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
                        return

                if getattr(self, 'show_logout_menu', False) and getattr(self, 'logout_rect', None):
                    if self.logout_rect.collidepoint(event.pos):
                        self.page = PAGE_ACCUEIL
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
                        self.page = PAGE_CONFIG_JEU
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
        
        elif self.page == PAGE_CONFIG_JEU:
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
                        self.page = PAGE_ACCUEIL
                        self.show_logout_menu = False
                        return
                    else:
                        self.show_logout_menu = False
                        return
                if getattr(self, 'show_logout_menu', False):
                    self.show_logout_menu = False
                    return
                # Bouton retour
                if hasattr(self, 'btn_retour_rect') and self.btn_retour_rect.collidepoint(event.pos):
                    self.page = PAGE_CHOIX_JEU
                    return
                # Bouton jouer
                if hasattr(self, 'btn_jouer_rect') and self.btn_jouer_rect.collidepoint(event.pos):
                    self.page = "PAGE_JEU"  # À remplacer par la page de jeu réelle
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
            if self.page == PAGE_ACCUEIL:
                self.draw_accueil()
            elif self.page == PAGE_CHOIX_JEU:
                self.draw_choix_jeu()
            elif self.page == PAGE_CONFIG_JEU:
                self.draw_config_jeu(getattr(self, 'selected_mode', None))
            pygame.display.flip(); self.clock.tick(30)


if __name__ == "__main__": 
    PortailGame()
