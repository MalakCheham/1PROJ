import os
import pygame
from core.langues import translate, draw_flags
from core.musique import draw_volume_bar


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_text_fit(text, font_name, color, max_width, min_size=18, max_size=48, bold=True):
    size = max_size
    while size >= min_size:
        font = pygame.font.SysFont(font_name, size, bold=bold)
        surf = font.render(text, True, color)
        if surf.get_width() <= max_width:
            return surf, font
        size -= 2
    font = pygame.font.SysFont(font_name, min_size, bold=bold)
    return font.render(text, True, color), font


def draw_custom_board(screen, font, font_small, font_title, muted, bar_rect, icon_rect, flag_fr_rect, flag_uk_rect, header_func=None, editor_state=None, show_logout_menu=False, logout_rect=None):
    screen.fill((255, 248, 225))
    if header_func:
        header_func()
    cx = screen.get_width() // 2
    cy = screen.get_height() // 2
    # Titre principal (traduction)
    titre = translate("creer_quadrant_4x4") if hasattr(translate, '__call__') else "Créer un Quadrant 4x4"
    titre_render, _ = render_text_fit(titre, "Helvetica", (0,102,68), screen.get_width()-80)
    titre_y = cy - 220  # Décalé plus bas
    screen.blit(titre_render, titre_render.get_rect(center=(cx, titre_y)))
    # Grille 4x4 centrée plus haut (remontée de 40px)
    grid_size = 4
    cell_size = 60
    grid_w = grid_size * cell_size
    grid_h = grid_size * cell_size
    grid_x = cx - grid_w//2
    grid_y = cy - 140  # -100 -> -140 (remontée de 40px)
    COULEURS = ["R", "J", "B", "V"]
    COULEURS_HEX = {"R": (255, 153, 153), "J": (255, 255, 179), "B": (153, 204, 255), "V": (179, 255, 179)}
    TEXTURE_DIR = os.path.join("assets", "textures")
    TEXTURE_FILES = {
        'R': "case-rouge.png",
        'B': "case-bleu.png",
        'V': "case-vert.png",
        'J': "case-jaune.png",
    }
    tile_textures = {}
    for k, fname in TEXTURE_FILES.items():
        try:
            surf = pygame.image.load(os.path.join(TEXTURE_DIR, fname)).convert_alpha()
            tile_textures[k] = pygame.transform.smoothscale(surf, (cell_size, cell_size))
        except Exception:
            tile_textures[k] = None
    grille = editor_state["grille"] if editor_state and "grille" in editor_state else [[None for _ in range(4)] for _ in range(4)]
    # Gestion de la rotation effective du quadrant (4 orientations possibles, 0/90/180/270°)
    if editor_state:
        orientation = editor_state.get("orientation", 0)
        if editor_state.get("rotate_now"):
            orientation = (orientation + 1) % 4
            editor_state["orientation"] = orientation
            editor_state["rotate_now"] = False
        # Toujours partir de la grille de base (non tournée)
        grille_base = editor_state.get("grille_base")
        if grille_base is None:
            grille_base = [row[:] for row in editor_state["grille"]]
            editor_state["grille_base"] = grille_base
        # Synchroniser la grille de base si l'utilisateur édite la grille (hors rotation)
        if editor_state["grille"] != grille_base and not editor_state.get("rotate_now", False):
            grille_base = [row[:] for row in editor_state["grille"]]
            editor_state["grille_base"] = grille_base
        grille = grille_base
        for _ in range(orientation):
            grille = [list(row) for row in zip(*grille[::-1])]
        
        if editor_state.get("last_orientation_sync") != orientation and not editor_state.get("rotate_now", False):
            editor_state["grille"] = [row[:] for row in grille]
            editor_state["last_orientation_sync"] = orientation
    else:
        grille = [[None for _ in range(4)] for _ in range(4)]
    for i in range(grid_size):
        for j in range(grid_size):
            val = grille[i][j]
            rect = pygame.Rect(grid_x + j*cell_size, grid_y + i*cell_size, cell_size, cell_size)
            if val and tile_textures.get(val) is not None:
                try:
                    screen.blit(tile_textures[val], rect)
                except Exception:
                    pygame.draw.rect(screen, COULEURS_HEX[val], rect)
            else:
                color = COULEURS_HEX[val] if val else (220, 220, 220)
                pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0,0,0), rect, 2)
    # Palette couleurs centrée sous la grille (tailles réduites)
    palette_y = grid_y + grid_h + 24
    palette_rects = []
    palette_w = len(COULEURS)*44 + (len(COULEURS)-1)*18
    palette_x = cx - palette_w//2
    palette_h = 36
    for idx, c in enumerate(COULEURS):
        px = palette_x + idx*(44+18)
        rect = pygame.Rect(px, palette_y, 44, palette_h)
        if tile_textures.get(c):
            try:
                screen.blit(pygame.transform.smoothscale(tile_textures[c], (44, palette_h)), rect)
            except Exception:
                pygame.draw.rect(screen, COULEURS_HEX[c], rect)
        else:
            pygame.draw.rect(screen, COULEURS_HEX[c], rect)
        if editor_state and editor_state.get("current_color") == c:
            pygame.draw.rect(screen, (0,0,0), rect, 3)
        palette_rects.append((px, palette_y, 44, palette_h, c))
    # Info Quadrant X/4 entre palette et boutons
    info_text = editor_state.get("info_text") if editor_state else "Quadrant 1/4"
    info_render = font_small.render(info_text, True, (0,0,0))
    info_y = palette_y + palette_h + 18
    screen.blit(info_render, info_render.get_rect(center=(cx, info_y)))
    # Icône retour à gauche, centrée verticalement par rapport à la nouvelle grille
    icon_img = pygame.image.load(os.path.join("assets", "en-arriere.png")).convert_alpha()
    icon_size = 48
    icon_img = pygame.transform.smoothscale(icon_img, (icon_size, icon_size))
    icon_x = 32
    icon_y = grid_y + grid_h//2 - icon_size//2
    retour_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
    screen.blit(icon_img, retour_rect)
    # Boutons Sauvegarder/Nouveau centrés sous l'info
    mouse_pos = pygame.mouse.get_pos()
    btns = [
        ("sauvegarder_quadrant", (translate("sauvegarder_quadrant") if hasattr(translate, '__call__') else "Sauvegarder Quadrant")),
        ("nouveau_quadrant", (translate("nouveau_quadrant") if hasattr(translate, '__call__') else "Nouveau Quadrant")),
    ]
    btn_rects = {}
    btn_w, btn_h = 320, 60
    btn_spacing = 48
    total_btn_w = 2*btn_w + btn_spacing
    start_x = cx - total_btn_w//2
    btn_y = info_y + 30
    for i, (key, label) in enumerate(btns):
        bx = start_x + i*(btn_w+btn_spacing)
        rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
        hovered = rect.collidepoint(mouse_pos)
        color = (66,155,70) if hovered else (76,175,80)
        btn_draw_rect = rect.copy(); btn_draw_rect.y -= 2 if hovered else 0
        # Suppression de l'ombre : draw_hover_shadow n'est plus appelé
        pygame.draw.rect(screen, color, btn_draw_rect, border_radius=18)
        pygame.draw.rect(screen, (0,0,0), btn_draw_rect, 2, border_radius=18)
        label_render = font_small.render(label, True, (255,255,255))
        screen.blit(label_render, label_render.get_rect(center=btn_draw_rect.center))
        btn_rects[key] = rect
    # Bouton Jouer avec ces Quadrants en bas centré
    jouer_key = "jouer_quadrants"
    jouer_label = (translate("jouer_avec_quadrants") if hasattr(translate, '__call__') else "Jouer avec ces Quadrants")
    jouer_enabled = (editor_state and len(editor_state.get("quadrants", [])) == 4)
    screen_h = screen.get_height()
    jouer_w, jouer_h = 380, 68
    jouer_x = cx - jouer_w//2
    jouer_y = screen_h - 60 - jouer_h
    jouer_rect = pygame.Rect(jouer_x, jouer_y, jouer_w, jouer_h)
    jouer_hovered = jouer_rect.collidepoint(mouse_pos)
    jouer_color = (66,155,70) if (jouer_hovered and jouer_enabled) else (180, 180, 180) if not jouer_enabled else (76,175,80)
    jouer_draw_rect = jouer_rect.copy(); jouer_draw_rect.y -= 2 if (jouer_hovered and jouer_enabled) else 0
    # Suppression de l'ombre : draw_hover_shadow n'est plus appelé
    pygame.draw.rect(screen, jouer_color, jouer_draw_rect, border_radius=22)
    pygame.draw.rect(screen, (0,0,0), jouer_draw_rect, 2, border_radius=22)
    jouer_label_render = font.render(jouer_label, True, (255,255,255) if jouer_enabled else (100,100,100))
    screen.blit(jouer_label_render, jouer_label_render.get_rect(center=jouer_draw_rect.center))
    btn_rects[jouer_key] = jouer_rect
    # Volume et langues
    draw_flags(screen, flag_fr_rect, flag_uk_rect)
    draw_volume_bar(screen, muted, pygame.mixer.music.get_volume(), bar_rect, icon_rect)
    # Affichage du sous-menu déconnexion si besoin (comme dans draw_header)
    # Correction : n'afficher le sous-menu que si le header n'est pas passé (on suppose que le header gère déjà l'affichage)
    if show_logout_menu and logout_rect and not header_func:
        logout_label = font_small.render(translate("se_deconnecter"), True, (0,77,64))
        w, h = logout_label.get_size()
        menu_rect = pygame.Rect(logout_rect.centerx - w//2 - 16, logout_rect.bottom + 10, w + 32, h + 16)
        pygame.draw.rect(screen, (255,255,255), menu_rect, border_radius=8)
        pygame.draw.rect(screen, (0,77,64), menu_rect, 2, border_radius=8)
        screen.blit(logout_label, logout_label.get_rect(center=menu_rect.center))
    return {"retour_rect": retour_rect, "btn_rects": btn_rects, "palette_rects": palette_rects, "grid_rect": (grid_x, grid_y, cell_size)}
