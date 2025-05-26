import pygame
import sys
import os
from core.parametres import set_language
from core.langues import translate
from core.musique import jouer_musique
from gui.menus.choix_jeu_page import draw_choix_jeu

# --- Etats du menu ---
PAGE_ACCUEIL = "accueil"
PAGE_CHOIX_JEU = "choix_jeu"

# --- Données des modes de jeu ---
MODES_JEU = [
    {
        "id": "katarenga",
        "titre": "Katarenga",
        "image": os.path.join("assets", "etoile.png"),
        "desc": "Un mode de jeu inspiré du shogi et des échecs.",
    },
    {
        "id": "congress",
        "titre": "Congress",
        "image": os.path.join("assets", "etoile.png"),
        "desc": "Un mode de réflexion où chaque coup compte.",
    },
    {
        "id": "isolation",
        "titre": "Isolation",
        "image": os.path.join("assets", "etoile.png"),
        "desc": "Un mode duel tactique pour isoler l'adversaire.",
    },
]

class PortailGame:
    def __init__(self):
        pygame.init()
        # Initialisation du mixer avant la musique
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        jouer_musique()

        # État audio
        self.muted = False
        try:
            self.last_volume = pygame.mixer.music.get_volume()
        except Exception:
            self.last_volume = 0.5

        self.screen = pygame.display.set_mode((1100, 850))
        pygame.display.set_caption("Portail d'accueil du jeu")
        icon_img = pygame.image.load(os.path.join("assets", "logo.png"))
        pygame.display.set_icon(icon_img)

        self.font = pygame.font.SysFont("Helvetica", 28)
        self.font_small = pygame.font.SysFont("Helvetica", 20)
        self.font_title = pygame.font.SysFont("Helvetica", 36, bold=True)

        logo_img = pygame.image.load(os.path.join("assets", "logo.png"))
        self.logo = pygame.transform.smoothscale(logo_img, (300, 300))
        self.help_icon = pygame.image.load(os.path.join("assets", "help_icon.png"))

        self.username = ""
        self.input_active = False
        self.page = PAGE_ACCUEIL
        self.clock = pygame.time.Clock()
        self.modes = MODES_JEU.copy()

        self.run()

    def draw_accueil(self):
        self.screen.fill((249, 246, 227))
        center_x = self.screen.get_width() // 2
        mouse_pos = pygame.mouse.get_pos()

        # Logo
        logo_rect = self.logo.get_rect(center=(center_x, 220))
        self.screen.blit(self.logo, logo_rect)

        # Sélecteur de langue (drapeaux en bas à droite)
        flag_size = 44
        margin = 24
        flag_fr = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "france.png")).convert_alpha(),
            (flag_size, flag_size)
        )
        flag_uk = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "uk.png")).convert_alpha(),
            (flag_size, flag_size)
        )
        def circle_mask(surf):
            mask = pygame.Surface((flag_size, flag_size), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255,255,255,255), (flag_size//2, flag_size//2), flag_size//2)
            surf = surf.copy()
            surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            return surf
        flag_fr = circle_mask(flag_fr)
        flag_uk = circle_mask(flag_uk)
        flags_x = self.screen.get_width() - flag_size - margin
        flag_fr_y = self.screen.get_height() - 2*flag_size - margin - 8
        flag_uk_y = self.screen.get_height() - flag_size - margin
        self.flag_fr_rect = pygame.Rect(flags_x, flag_fr_y, flag_size, flag_size)
        self.flag_uk_rect = pygame.Rect(flags_x, flag_uk_y, flag_size, flag_size)
        for flag, rect in [(flag_fr, self.flag_fr_rect), (flag_uk, self.flag_uk_rect)]:
            pygame.draw.circle(self.screen, (255,255,255), rect.center, flag_size//2+2)
            pygame.draw.circle(self.screen, (200,200,200), rect.center, flag_size//2+2, 2)
            hovered = rect.collidepoint(mouse_pos)
            draw_rect = rect.copy()
            if hovered:
                halo = pygame.Surface((flag_size+12, flag_size+12), pygame.SRCALPHA)
                pygame.draw.circle(halo, (76,175,80,38), (halo.get_width()//2, halo.get_height()//2), (flag_size+6)//2+2)
                self.screen.blit(halo, (rect.x-6, rect.y-6))
                draw_rect.y -= 2
            self.screen.blit(flag, draw_rect)

        # Titre
        titre = translate("bienvenue_portail")
        titre_render = self.font_title.render(titre, True, (0,77,64))
        titre_rect = titre_render.get_rect(center=(center_x, 370))
        self.screen.blit(titre_render, titre_rect)

        # Champ de saisie
        saisie = self.font.render(translate("entrez_nom_utilisateur"), True, (0,0,0))
        saisie_rect = saisie.get_rect(center=(center_x, 430))
        self.screen.blit(saisie, saisie_rect)
        self.input_rect = pygame.Rect(center_x - 150, 480, 300, 45)
        pygame.draw.rect(self.screen, (255,255,255), self.input_rect, border_radius=16)
        pygame.draw.rect(self.screen, (0,0,0), self.input_rect, 2, border_radius=16)
        user_text = self.font_small.render(self.username, True, (0,0,0))
        user_text_rect = user_text.get_rect(x=self.input_rect.x+10, centery=self.input_rect.centery)
        self.screen.blit(user_text, user_text_rect)
        if self.input_active:
            cursor_x = user_text_rect.x + user_text.get_width() + 2
            cursor_y = user_text_rect.y
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.rect(self.screen, (0,77,64), (cursor_x, cursor_y, 3, user_text.get_height()-2), border_radius=2)

        # Bouton d'entrée
        btn_rect = pygame.Rect(center_x - 175, 560, 350, 65)
        btn_hovered = btn_rect.collidepoint(mouse_pos)
        color = (66, 155, 70) if btn_hovered else (76, 175, 80)
        btn_draw_rect = btn_rect.copy()
        if btn_hovered:
            btn_draw_rect.y -= 2
        pygame.draw.rect(self.screen, color, btn_draw_rect, border_radius=22)
        pygame.draw.rect(self.screen, (0,0,0), btn_draw_rect, 2, border_radius=22)
        try:
            play_logo = pygame.image.load(os.path.join("assets", "play-button.png"))
            play_logo = pygame.transform.smoothscale(play_logo, (40, 40))
            self.screen.blit(play_logo, (btn_draw_rect.x+15, btn_draw_rect.y+12))
        except:
            pass
        btn_label = self.font.render(translate("entrez_portail"), True, (255,255,255))
        btn_label_rect = btn_label.get_rect(centery=btn_draw_rect.centery, x=btn_draw_rect.x + (btn_draw_rect.width - btn_label.get_width())//2 + 20)
        self.screen.blit(btn_label, btn_label_rect)
        self.btn_rect = btn_draw_rect

        # Barre de volume
        self.draw_volume_bar()
        pygame.display.update()

    def draw_volume_bar(self):
        bar_x, bar_y = 40, self.screen.get_height() - 60
        bar_width, bar_height = 180, 18
        pygame.draw.rect(self.screen, (220,220,220), (bar_x, bar_y, bar_width, bar_height), border_radius=9)
        volume = 0.0 if self.muted else pygame.mixer.music.get_volume()
        fill_width = int(bar_width * volume)
        pygame.draw.rect(self.screen, (76,175,80), (bar_x, bar_y, fill_width, bar_height), border_radius=9)
        pygame.draw.rect(self.screen, (0,0,0), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=9)
        icon_file = "cone-de-haut-parleur.png" if self.muted or volume == 0.0 else "volume-reduit.png"
        try:
            icon = pygame.image.load(os.path.join("assets", icon_file))
            icon = pygame.transform.smoothscale(icon, (28, 28))
            self.screen.blit(icon, (bar_x-36, bar_y-5))
        except:
            pass
        self.volume_bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        self.volume_icon_rect = pygame.Rect(bar_x-36, bar_y-5, 28, 28)

    def draw_choix_jeu(self):
        draw_choix_jeu(self)

    def wrap_text(self, text, max_chars):
        words = text.split()
        lines, line = [], ""
        for w in words:
            if len(line + w) < max_chars:
                line += w + " "
            else:
                lines.append(line)
                line = w + " "
        lines.append(line)
        return lines

    def handle_event(self, event):
        # Accueil
        if self.page == PAGE_ACCUEIL:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, 'flag_fr_rect') and self.flag_fr_rect.collidepoint(event.pos):
                    set_language("fr"); pygame.time.wait(150); return
                if hasattr(self, 'flag_uk_rect') and self.flag_uk_rect.collidepoint(event.pos):
                    set_language("en"); pygame.time.wait(150); return
                if self.input_rect.collidepoint(event.pos):
                    self.input_active = True
                else:
                    self.input_active = False
                if self.btn_rect.collidepoint(event.pos) and self.username.strip():
                    self.page = PAGE_CHOIX_JEU; return
                # Clic sur barre de volume
                if self.volume_bar_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - self.volume_bar_rect.x
                    v = min(max(rel_x / self.volume_bar_rect.width, 0), 1)
                    pygame.mixer.music.set_volume(v)
                    self.last_volume = v
                    self.muted = False
                    return
                # Clic sur icône mute
                if self.volume_icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume()
                        pygame.mixer.music.set_volume(0.0)
                        self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5)
                        self.muted = False
                    return
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if self.volume_bar_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - self.volume_bar_rect.x
                    v = min(max(rel_x / self.volume_bar_rect.width, 0), 1)
                    pygame.mixer.music.set_volume(v)
                    self.last_volume = v
                    self.muted = False
                    return
            elif event.type == pygame.KEYDOWN and self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.key == pygame.K_RETURN and self.username.strip():
                    self.page = PAGE_CHOIX_JEU
                elif len(self.username) < 20 and event.unicode.isprintable():
                    self.username += event.unicode
            return

        # Choix de jeu
        if self.page == PAGE_CHOIX_JEU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Gestion du clic sur les drapeaux (en bas à droite)
                if hasattr(self, 'flag_fr_rect') and self.flag_fr_rect.collidepoint(event.pos):
                    set_language("fr"); pygame.time.wait(120); return
                if hasattr(self, 'flag_uk_rect') and self.flag_uk_rect.collidepoint(event.pos):
                    set_language("en"); pygame.time.wait(120); return
                cx, cy, cr = self.lyrique_circle
                dx, dy = event.pos[0] - cx, event.pos[1] - cy
                if dx*dx + dy*dy <= cr*cr:
                    self.show_logout_menu = True; return
                if getattr(self, 'show_logout_menu', False) and self.logout_rect and self.logout_rect.collidepoint(event.pos):
                    self.page = PAGE_ACCUEIL; self.username = ""; self.input_active = False; self.show_logout_menu = False; return
                if getattr(self, 'show_logout_menu', False):
                    in_circle = (event.pos[0]-cx)**2 + (event.pos[1]-cy)**2 <= cr**2
                    if not (self.logout_rect and self.logout_rect.collidepoint(event.pos)) and not in_circle:
                        self.show_logout_menu = False; return
                for mode in self.modes:
                    if mode.get("btn_rect") and mode["btn_rect"].collidepoint(event.pos):
                        print(f"Lancer le mode: {mode['titre']}")
                if self.volume_bar_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - self.volume_bar_rect.x
                    v = min(max(rel_x / self.volume_bar_rect.width, 0), 1)
                    pygame.mixer.music.set_volume(v)
                    self.last_volume = v
                    self.muted = False
                    return
                if self.volume_icon_rect.collidepoint(event.pos):
                    if not self.muted:
                        self.last_volume = pygame.mixer.music.get_volume()
                        pygame.mixer.music.set_volume(0.0)
                        self.muted = True
                    else:
                        pygame.mixer.music.set_volume(self.last_volume or 0.5)
                        self.muted = False
                    return
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if self.volume_bar_rect.collidepoint(event.pos):
                    rel_x = event.pos[0] - self.volume_bar_rect.x
                    v = min(max(rel_x / self.volume_bar_rect.width, 0), 1)
                    pygame.mixer.music.set_volume(v)
                    self.last_volume = v
                    self.muted = False
                    return

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.handle_event(event)
            if self.page == PAGE_ACCUEIL:
                self.draw_accueil()
            else:
                self.draw_choix_jeu()
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    PortailGame()
