import pygame
from core.langues import translate, draw_flags, draw_hover_shadow
from core.musique import draw_volume_bar

def draw_choice_game(screen, font, font_small, font_title, MODES_JEU, muted, bar_rect, icon_rect, flag_fr_rect, flag_uk_rect, header_func=None):
    screen.fill((249,246,227))
    if header_func:
        header_func()
    cx = screen.get_width()//2
    # Titre principal et sous-titre (depuis traductions)
    titre_modes = translate("sous_titre_modes")
    sous_titre = translate("choisissez_mode_jeu")
    titre_font = pygame.font.SysFont("Helvetica", 28, bold=True)
    titre_render = titre_font.render(titre_modes, 1, (0,77,64))
    sous_titre_render = font_small.render(sous_titre, 1, (0,0,0))
    screen.blit(titre_render, titre_render.get_rect(center=(cx, 150)))
    screen.blit(sous_titre_render, sous_titre_render.get_rect(center=(cx, 190)))
    # Modes de jeu
    card_w, card_h = 300, 340
    spacing = 40
    total_w = len(MODES_JEU)*card_w + (len(MODES_JEU)-1)*spacing
    start_x = (screen.get_width()-total_w)//2
    y = 230  # Décalage sous header + titres
    mode_btn_rects = []
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
        screen.blit(font.render(titre_mod, 1, (0,51,102)), (x+20, y+150))
        # Desc (depuis traductions)
        desc_mod = translate(f"desc_{mode['id']}")
        desc_lines = wrap_text(desc_mod, font_small, card_w-40)
        for j, line in enumerate(desc_lines):
            screen.blit(font_small.render(line, 1, (0,0,0)), (x+20, y+190+j*24))
        # Bouton jouer
        btn_rect = pygame.Rect(x+card_w//2-60, y+card_h-70, 120, 44)
        btn_hovered = btn_rect.collidepoint(mouse_pos)
        color = (66,155,70) if btn_hovered else (76,175,80)
        btn_draw_rect = btn_rect.copy(); btn_draw_rect.y -= 2 if btn_hovered else 0
        if btn_hovered:
            draw_hover_shadow(screen, btn_rect, color=(76,175,80,38), offset=6, border_radius=14)
        pygame.draw.rect(screen, color, btn_draw_rect, border_radius=14)
        pygame.draw.rect(screen, (0,0,0), btn_draw_rect, 2, border_radius=14)
        btn_label = font_small.render(translate("lancer_ce_mode"), 1, (255,255,255))
        screen.blit(btn_label, btn_label.get_rect(center=btn_draw_rect.center))
        mode_btn_rects.append((btn_rect, mode["id"]))
    draw_flags(screen, flag_fr_rect, flag_uk_rect)
    draw_volume_bar(screen, muted, pygame.mixer.music.get_volume(), bar_rect, icon_rect)
    return mode_btn_rects

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
