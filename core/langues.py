from core.parametres import get_language
from core.traductions import TRADUCTIONS
import pygame
import os


def translate(key):
    current_lang = get_language()
    return TRADUCTIONS.get(key, {}).get(current_lang, key)


def draw_hover_shadow(surface, rect, color=(76,175,80,38), offset=6, border_radius=0):
    shadow = pygame.Surface((rect.width+offset*2, rect.height+offset*2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, color, shadow.get_rect())
    surface.blit(shadow, (rect.x-offset, rect.y-offset))


def draw_flags(screen, flag_fr_rect, flag_uk_rect):
    mouse_pos = pygame.mouse.get_pos()
    flag_size = flag_fr_rect.width
    for img, rect in zip(["france.png", "uk.png"], [flag_fr_rect, flag_uk_rect]):
        hovered = rect.collidepoint(mouse_pos)
        if hovered:
            draw_hover_shadow(screen, rect, color=(76,175,80,38), offset=6)
        flag = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets", img)).convert_alpha(), (flag_size, flag_size))
        mask = pygame.Surface((flag_size, flag_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255,255,255,255), (flag_size//2, flag_size//2), flag_size//2)
        flag.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.circle(screen, (255,255,255), rect.center, flag_size//2+2)
        pygame.draw.circle(screen, (200,200,200), rect.center, flag_size//2+2, 2)
        screen.blit(flag, rect)
