import pygame
import os
from core.langues import translate, draw_flags, draw_hover_shadow
from core.musique import draw_volume_bar

def draw_config_jeu(screen, font, font_small, font_title, mode_id, selected_plateau, show_help_menu, help_close_rect, show_logout_menu, logout_rect, muted, bar_rect, icon_rect, flag_fr_rect, flag_uk_rect, header_func=None):
    cx = screen.get_width()//2
    screen.fill((249,246,227))
    if header_func:
        header_func()
    # Titre de la page
    mode_label = translate(f"mode_{mode_id}") if mode_id else ""
    titre = font_title.render(f"{translate('configuration_du_jeu')} : {mode_label}", 1, (0,77,64))
    screen.blit(titre, titre.get_rect(center=(cx, 140)))
    # 1ère ZONE : Mode de jeu
    zone1_rect = pygame.Rect(cx-320, 210, 640, 120)
    pygame.draw.rect(screen, (255,255,255), zone1_rect, border_radius=18)
    pygame.draw.rect(screen, (0,77,64), zone1_rect, 2, border_radius=18)
    label1 = font.render(translate("mode_de_jeu"), 1, (0,51,102))
    screen.blit(label1, (zone1_rect.x+30, zone1_rect.y+30))
    # 2ème ZONE : Configuration du plateau
    zone2_rect = pygame.Rect(cx-320, 360, 640, 220)
    pygame.draw.rect(screen, (255,255,255), zone2_rect, border_radius=18)
    pygame.draw.rect(screen, (0,77,64), zone2_rect, 2, border_radius=18)
    label2 = font.render(translate("plateau"), 1, (0,51,102))
    screen.blit(label2, (zone2_rect.x+30, zone2_rect.y+30))
    # Choix plateau_auto ou plateau_perso (radio boutons)
    radio_y = zone2_rect.y+90
    radio_x1 = zone2_rect.x+60
    radio_radius = 16
    # Radio 1 : plateau_auto
    auto_rect = pygame.Rect(radio_x1-radio_radius, radio_y-radio_radius, 2*radio_radius, 2*radio_radius)
    pygame.draw.circle(screen, (0,77,64), (radio_x1, radio_y), radio_radius, 2)
    if selected_plateau == 'auto':
        pygame.draw.circle(screen, (66,155,70), (radio_x1, radio_y), radio_radius-5)
    label_auto = font_small.render(translate("plateau_auto"), 1, (0,0,0))
    screen.blit(label_auto, (radio_x1+28, radio_y-label_auto.get_height()//2))
    # Radio 2 : plateau_perso
    radio_y2 = radio_y + 48
    perso_rect = pygame.Rect(radio_x1-radio_radius, radio_y2-radio_radius, 2*radio_radius, 2*radio_radius)
    pygame.draw.circle(screen, (0,77,64), (radio_x1, radio_y2), radio_radius, 2)
    if selected_plateau == 'perso':
        pygame.draw.circle(screen, (66,155,70), (radio_x1, radio_y2), radio_radius-5)
    label_perso = font_small.render(translate("plateau_perso"), 1, (0,0,0))
    screen.blit(label_perso, (radio_x1+28, radio_y2-label_perso.get_height()//2))
    plateau_radio_rects = [(auto_rect, 'auto'), (perso_rect, 'perso')]
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
    btn_label_retour = font_small.render(translate("retour"), 1, (255,255,255))
    btn_label_jouer = font_small.render(translate("lancer_ce_mode"), 1, (255,255,255))
    screen.blit(btn_label_retour, btn_label_retour.get_rect(center=btn_retour_draw.center))
    screen.blit(btn_label_jouer, btn_label_jouer.get_rect(center=btn_jouer_draw.center))
    # Volume et langues
    draw_flags(screen, flag_fr_rect, flag_uk_rect)
    draw_volume_bar(screen, muted, pygame.mixer.music.get_volume(), bar_rect, icon_rect)
    # Affichage de l'icône d'aide (point d'interrogation)
    help_icon = pygame.image.load(os.path.join("assets", "point-dinterrogation.png")).convert_alpha()
    help_icon = pygame.transform.smoothscale(help_icon, (44, 44))
    help_icon_rect = pygame.Rect(cx+320-54, 210+10, 44, 44)
    screen.blit(help_icon, help_icon_rect)
    # Affichage du sous-menu d'aide si besoin
    help_close_rect_out = None
    if show_help_menu:
        from core.aide import get_regles
        regles_lines = get_regles(mode_id or "")
        max_width = 0
        total_height = 0
        for text, is_emoji in regles_lines:
            font_help = pygame.font.SysFont("Segoe UI Emoji", 28, bold=True) if is_emoji and text.strip() else font_small
            surf = font_help.render(text, True, (0,0,0))
            max_width = max(max_width, surf.get_width())
            total_height += surf.get_height() + 2
        popup_w = max(480, max_width + 48)
        popup_h = max(180, total_height + 90)
        popup_x = cx - popup_w//2
        popup_y = 210 + 120 + 24
        popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
        pygame.draw.rect(screen, (255,255,255), popup_rect, border_radius=18)
        pygame.draw.rect(screen, (0,77,64), popup_rect, 2, border_radius=18)
        titre_aide = font.render(translate("aide"), 1, (0,77,64))
        screen.blit(titre_aide, (popup_x+24, popup_y+18))
        y_text = popup_y+64
        for text, is_emoji in regles_lines:
            font_help = pygame.font.SysFont("Segoe UI Emoji", 28, bold=True) if is_emoji and text.strip() else font_small
            surf = font_help.render(text, True, (0,0,0))
            screen.blit(surf, (popup_x+24, y_text))
            y_text += surf.get_height() + 2
        close_rect = pygame.Rect(popup_x+popup_w-38, popup_y+10, 28, 28)
        pygame.draw.circle(screen, (220,60,60), close_rect.center, 14)
        pygame.draw.line(screen, (255,255,255), (close_rect.left+7, close_rect.top+7), (close_rect.right-7, close_rect.bottom-7), 3)
        pygame.draw.line(screen, (255,255,255), (close_rect.right-7, close_rect.top+7), (close_rect.left+7, close_rect.bottom-7), 3)
        help_close_rect_out = close_rect
    return {
        'btn_retour_rect': btn_retour,
        'btn_jouer_rect': btn_jouer,
        'plateau_radio_rects': plateau_radio_rects,
        'help_icon_rect': help_icon_rect,
        'help_close_rect': help_close_rect_out
    }
