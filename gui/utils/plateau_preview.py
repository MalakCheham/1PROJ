import pygame
import os
from core.langues import translate, draw_flags
from core.musique import draw_volume_bar

def draw_plateau_preview(screen, font_title, font_small, preview_plateau, muted, bar_rect=None, icon_rect=None, flag_fr_rect=None, flag_uk_rect=None, header_func=None):
    # --- Fond général ---
    screen.fill((255, 248, 225))
    # --- Header (optionnel) ---
    if header_func:
        header_func()
    # --- Recalcul rectangles volume/langues ---
    screen_w, screen_h = screen.get_width(), screen.get_height()
    bar_rect = pygame.Rect(40, screen_h-60, 180, 18)
    icon_rect = pygame.Rect(4, screen_h-65, 28, 28)
    flag_size, margin = 44, 24
    flag_fr_rect = pygame.Rect(screen_w-flag_size-margin, screen_h-2*flag_size-margin-8, flag_size, flag_size)
    flag_uk_rect = pygame.Rect(screen_w-flag_size-margin, screen_h-flag_size-margin, flag_size, flag_size)
    # --- Zone plateau ---
    header_height = 90
    footer_height = 80
    zone_top = header_height
    zone_bottom = screen_h - footer_height
    zone_height = zone_bottom - zone_top
    zone_width = screen_w
    # --- Textures ---
    TEXTURE_DIR = os.path.join("assets", "textures")
    TEXTURE_FILES = {
        'R': "case-rouge.png",
        'B': "case-bleu.png",
        'V': "case-vert.png",
        'J': "case-jaune.png",
    }
    tile_textures = {}
    cadre_margin = 72
    cadre_w = min(zone_width, zone_height) - 2*cadre_margin
    cadre_h = cadre_w
    cell_size = cadre_w // 12
    for k, fname in TEXTURE_FILES.items():
        surf = pygame.image.load(os.path.join(TEXTURE_DIR, fname)).convert_alpha()
        tile_textures[k] = pygame.transform.smoothscale(surf, (cell_size, cell_size))
    # --- Cadre ---
    try:
        cadre_img = pygame.image.load(os.path.join(TEXTURE_DIR, "cadre.png")).convert_alpha()
        cadre_img = pygame.transform.smoothscale(cadre_img, (cadre_w, cadre_h))
        cadre_ok = True
    except Exception as e:
        cadre_img = None
        cadre_ok = False
    offset_x = (zone_width - cadre_w) // 2
    offset_y = zone_top + (zone_height - cadre_h) // 2
    # --- Titre centré AU HAUT DU CADRE ---
    titre = font_title.render(translate("plateau_genere"), True, (0, 102, 68))
    titre_y = offset_y - titre.get_height() - 18
    screen.blit(titre, (screen_w//2 - titre.get_width()//2, titre_y))
    # --- Bouton retour icône à gauche, centré verticalement par rapport à la zone plateau ---
    icon_img = pygame.image.load(os.path.join("assets", "en-arriere.png")).convert_alpha()
    icon_size = 48
    icon_img = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
    icon_x = offset_x - icon_size - 24
    icon_y = offset_y + cadre_h//2 - icon_size//2
    retour_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
    screen.blit(icon_img, retour_rect)
    # --- Cadre et plateau centrés ---
    if cadre_ok and cadre_img:
        screen.blit(cadre_img, (offset_x, offset_y))
    else:
        pygame.draw.rect(screen, (62, 30, 11), (offset_x, offset_y, cadre_w, cadre_h), 6)
    # Plateau (cases texturées)
    plateau_w = 8 * cell_size
    plateau_h = 8 * cell_size
    px = offset_x + (cadre_w - plateau_w)//2
    py = offset_y + (cadre_h - plateau_h)//2
    for i in range(8):
        for j in range(8):
            val = preview_plateau.cases[i][j]
            tex = tile_textures.get(val)
            if tex:
                screen.blit(tex, (px + j*cell_size, py + i*cell_size))
            pygame.draw.rect(screen, (62, 30, 11), (px + j*cell_size, py + i*cell_size, cell_size, cell_size), 1)
    # --- Volume et langues (direct) ---
    draw_volume_bar(screen, muted, pygame.mixer.music.get_volume(), bar_rect, icon_rect)
    draw_flags(screen, flag_fr_rect, flag_uk_rect)
    # --- Bouton Jouer en bas ---
    play_w, play_h = 180, 64
    play_x = screen_w//2 - play_w//2
    play_y = screen_h - 60 - play_h//2
    play_rect = pygame.Rect(play_x, play_y, play_w, play_h)
    mouse_pos = pygame.mouse.get_pos()
    play_hovered = play_rect.collidepoint(mouse_pos)
    play_color = (66,155,70) if play_hovered else (76,175,80)
    pygame.draw.rect(screen, play_color, play_rect, border_radius=22)
    pygame.draw.rect(screen, (0,0,0), play_rect, 2, border_radius=22)
    # Icon (optionnel)
    play_icon_path = os.path.join("assets", "play-button.png")
    label_x = play_x+30
    if os.path.exists(play_icon_path):
        try:
            play_icon = pygame.image.load(play_icon_path).convert_alpha()
            play_icon = pygame.transform.smoothscale(play_icon, (38, 38))
            screen.blit(play_icon, (play_x+18, play_y+play_h//2-19))
            label_x = play_x+70
        except Exception:
            label_x = play_x+30
    play_label = font_title.render(translate("jouer") if hasattr(translate, '__call__') else "Jouer", True, (255,255,255))
    screen.blit(play_label, (label_x, play_y+play_h//2-play_label.get_height()//2))
    return {"retour_rect": retour_rect, "play_rect": play_rect}
