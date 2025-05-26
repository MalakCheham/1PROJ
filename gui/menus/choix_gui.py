import pygame
import os
from core.langues import translate
from core.parametres import set_language

# Cette fonction est externalisée pour être utilisée dans PortailGame

def draw_choix_jeu(self):
    # Affichage page titre du mode si sous_menu_mode défini et pas un mode à sous-menu
    if getattr(self, 'sous_menu_mode', None) and getattr(self, 'sous_menu_mode', None) not in ('katarenga', 'isolation', 'congress'):
        self.screen.fill((254, 251, 233))
        header_height = 90
        # Header
        pygame.draw.rect(self.screen, (240, 238, 220), (0, 0, self.screen.get_width(), header_height))
        pygame.draw.line(self.screen, (200, 200, 180), (0, header_height), (self.screen.get_width(), header_height), 2)
        logo_size = self.font_title.get_height() + 10
        logo_img = pygame.transform.smoothscale(self.logo, (logo_size, logo_size))
        self.screen.blit(logo_img, (30, header_height//2 - logo_size//2))
        titre = self.font_title.render(f"{translate('bienvenue') if hasattr(self, 'username') and self.username else translate('bienvenue_portail')} {self.username + ' !' if self.username else ''}", True, (0,77,64))
        titre_rect = titre.get_rect()
        titre_rect.centery = header_height//2
        titre_rect.x = 50 + logo_size
        self.screen.blit(titre, titre_rect)
        circle_radius = logo_size // 2
        circle_x = self.screen.get_width() - 40 - circle_radius
        circle_y = header_height//2
        pygame.draw.circle(self.screen, (220, 230, 240), (circle_x, circle_y), circle_radius)
        pygame.draw.circle(self.screen, (0, 77, 64), (circle_x, circle_y), circle_radius, 2)
        try:
            lyrique_img = pygame.image.load(os.path.join("assets", "lyrique.png"))
            lyrique_img = pygame.transform.smoothscale(lyrique_img, (logo_size-8, logo_size-8))
            self.screen.blit(lyrique_img, (circle_x - (logo_size-8)//2, circle_y - (logo_size-8)//2))
        except:
            pass
        # Affichage du header (affiche le menu déconnexion si show_logout_menu est True)
        mouse_pos = pygame.mouse.get_pos()
        lyrique_hovered = (circle_x - mouse_pos[0])**2 + (circle_y - mouse_pos[1])**2 <= circle_radius**2
        if lyrique_hovered and pygame.mouse.get_pressed()[0]:
            self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
        if getattr(self, 'show_logout_menu', False):
            logout_label = self.font_small.render(translate("se_deconnecter"), True, (0,77,64))
            w, h = logout_label.get_size()
            menu_rect = pygame.Rect(circle_x - w - 16, circle_y + circle_radius + 10, w + 32, h + 16)
            pygame.draw.rect(self.screen, (255,255,255), menu_rect, border_radius=8)
            pygame.draw.rect(self.screen, (0,77,64), menu_rect, 2, border_radius=8)
            self.screen.blit(logout_label, logout_label.get_rect(center=menu_rect.center))
            self.logout_rect = menu_rect
        else:
            self.logout_rect = None
        self.lyrique_circle = (circle_x, circle_y, circle_radius)
        # Titre du mode centré
        titre_mode = self.font_title.render(str(self.sous_menu_mode).capitalize(), True, (0,77,64))
        titre_mode_rect = titre_mode.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(titre_mode, titre_mode_rect)
        # Barre de volume
        self.draw_volume_bar()
        # Sélecteur de langue (drapeaux)
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
        mouse_pos = pygame.mouse.get_pos()
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
        return
    self.screen.fill((254, 251, 233))
    header_height = 90
    pygame.draw.rect(self.screen, (240, 238, 220), (0, 0, self.screen.get_width(), header_height))
    pygame.draw.line(self.screen, (200, 200, 180), (0, header_height), (self.screen.get_width(), header_height), 2)
    logo_size = self.font_title.get_height() + 10
    logo_img = pygame.transform.smoothscale(self.logo, (logo_size, logo_size))
    self.screen.blit(logo_img, (30, header_height//2 - logo_size//2))
    titre = self.font_title.render(f"{translate('bienvenue') if hasattr(self, 'username') and self.username else translate('bienvenue_portail')} {self.username + ' !' if self.username else ''}", True, (0,77,64))
    titre_rect = titre.get_rect()
    titre_rect.centery = header_height//2
    titre_rect.x = 50 + logo_size
    self.screen.blit(titre, titre_rect)
    circle_radius = logo_size // 2
    circle_x = self.screen.get_width() - 40 - circle_radius
    circle_y = header_height//2
    pygame.draw.circle(self.screen, (220, 230, 240), (circle_x, circle_y), circle_radius)
    pygame.draw.circle(self.screen, (0, 77, 64), (circle_x, circle_y), circle_radius, 2)
    try:
        lyrique_img = pygame.image.load(os.path.join("assets", "lyrique.png"))
        lyrique_img = pygame.transform.smoothscale(lyrique_img, (logo_size-8, logo_size-8))
        self.screen.blit(lyrique_img, (circle_x - (logo_size-8)//2, circle_y - (logo_size-8)//2))
    except:
        pass
    # Affichage du header (affiche le menu déconnexion si show_logout_menu est True)
    mouse_pos = pygame.mouse.get_pos()
    lyrique_hovered = (circle_x - mouse_pos[0])**2 + (circle_y - mouse_pos[1])**2 <= circle_radius**2
    if lyrique_hovered and pygame.mouse.get_pressed()[0]:
        self.show_logout_menu = not getattr(self, 'show_logout_menu', False)
    if getattr(self, 'show_logout_menu', False):
        logout_label = self.font_small.render(translate("se_deconnecter"), True, (0,77,64))
        w, h = logout_label.get_size()
        menu_rect = pygame.Rect(circle_x - w - 16, circle_y + circle_radius + 10, w + 32, h + 16)
        pygame.draw.rect(self.screen, (255,255,255), menu_rect, border_radius=8)
        pygame.draw.rect(self.screen, (0,77,64), menu_rect, 2, border_radius=8)
        self.screen.blit(logout_label, logout_label.get_rect(center=menu_rect.center))
        self.logout_rect = menu_rect
    else:
        self.logout_rect = None
    self.lyrique_circle = (circle_x, circle_y, circle_radius)
    # Modes
    if getattr(self, 'sous_menu_mode', None) in ('katarenga', 'isolation', 'congress'):
        # Affiche UNIQUEMENT le sous-menu (type de partie + plateau), header, volume, drapeaux
        return
    # Sinon, page normale avec la liste des modes
    modes_width = len(self.modes)*260 + (len(self.modes)-1)*60
    start_x = (self.screen.get_width() - modes_width)//2
    y = header_height + 130
    for idx, mode in enumerate(self.modes):
        x = start_x + idx*(260+60)
        pygame.draw.rect(self.screen, (220, 230, 240), (x, y, 260, 500), border_radius=18)
        try:
            img = pygame.transform.scale(pygame.image.load(mode["image"]), (240, 160))
            self.screen.blit(img, (x+10, y+10))
        except:
            pygame.draw.rect(self.screen, (200,200,200), (x+10, y+10, 240, 160))
        titre_mod = translate(f"mode_{mode['id']}") if f"mode_{mode['id']}" in dir(self) or f"mode_{mode['id']}" in globals() or f"mode_{mode['id']}" in locals() or True else mode["titre"]
        self.screen.blit(self.font.render(titre_mod, True, (0,51,102)), (x+20, y+190))
        desc_mod = translate(f"desc_{mode['id']}") if f"desc_{mode['id']}" in dir(self) or f"desc_{mode['id']}" in globals() or f"desc_{mode['id']}" in locals() or True else mode["desc"]
        for i, line in enumerate(self.wrap_text(desc_mod, 32)):
            self.screen.blit(self.font_small.render(line, True, (0,0,0)), (x+20, y+230+i*25))
        btn = pygame.Rect(x+30, y+400, 200, 50)
        pygame.draw.rect(self.screen, (76, 175, 80), btn)
        pygame.draw.rect(self.screen, (0,0,0), btn, 2)
        self.screen.blit(self.help_icon, (btn.x+8, btn.y+8))
        self.screen.blit(self.font_small.render(translate("lancer_ce_mode"), True, (255,255,255)), (btn.x+50, btn.y+13))
        mode["btn_rect"] = btn
    # Barre de volume
    self.draw_volume_bar()
    # Sélecteur de langue (drapeaux en bas à droite, dessin uniquement)
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
    mouse_pos = pygame.mouse.get_pos()
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
    # Titres centrés et traduits
    choix_titre = translate("choisissez_mode_jeu")
    choix_titre_render = self.font_title.render(choix_titre, True, (0,77,64))
    choix_titre_rect = choix_titre_render.get_rect(center=(self.screen.get_width()//2, header_height+50))
    self.screen.blit(choix_titre_render, choix_titre_rect)
    sous_titre = translate("sous_titre_modes")
    sous_titre_render = self.font.render(sous_titre, True, (0,0,0))
    sous_titre_rect = sous_titre_render.get_rect(center=(self.screen.get_width()//2, header_height+95))
    self.screen.blit(sous_titre_render, sous_titre_rect)
    # Affiche une page simple avec le titre du mode sélectionné pour TOUS les modes
    if getattr(self, 'sous_menu_mode', None):
        self.screen.fill((254, 251, 233))
        titre = self.font_title.render(str(self.sous_menu_mode).capitalize(), True, (0,77,64))
        titre_rect = titre.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(titre, titre_rect)
        # Header, volume, drapeaux
        self.draw_volume_bar()
        # Sélecteur de langue (drapeaux)
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
        mouse_pos = pygame.mouse.get_pos()
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
        return

