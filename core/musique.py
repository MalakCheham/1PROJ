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

def regler_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

def pause():
    pygame.mixer.music.pause()

def reprendre():
    pygame.mixer.music.unpause()
