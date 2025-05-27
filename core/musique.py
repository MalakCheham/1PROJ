import os
import pygame

MUSIQUE_LANCEE = False

def jouer_musique():
    global MUSIQUE_LANCEE
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    if not MUSIQUE_LANCEE:
        chemin_musique = os.path.join("assets", "musique.mp3")
        pygame.mixer.music.load(chemin_musique)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        MUSIQUE_LANCEE = True

def init_audio():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    jouer_musique()
    return pygame.mixer.music.get_volume()

def regler_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

def pause():
    pygame.mixer.music.pause()

def reprendre():
    pygame.mixer.music.unpause()

def draw_volume_bar(screen, muted, volume, bar_rect, icon_rect):
    pygame.draw.rect(screen, (220,220,220), bar_rect, border_radius=9)
    fill = int(bar_rect.width * (0 if muted else volume))
    pygame.draw.rect(screen, (76,175,80), (bar_rect.x, bar_rect.y, fill, bar_rect.height), border_radius=9)
    pygame.draw.rect(screen, (0,0,0), bar_rect, 2, border_radius=9)
    icon = "cone-de-haut-parleur.png" if muted or volume==0 else "volume-reduit.png"
    img = pygame.transform.smoothscale(pygame.image.load(os.path.join("assets", icon)), (28,28))
    screen.blit(img, icon_rect)
