import pygame
from core.langues import traduire, set_language
import os

class NetworkSelectorPygame:
    def __init__(self, on_result):
        pygame.init()
        self.screen = pygame.display.set_mode((350, 180))
        pygame.display.set_caption(traduire("choisir_mode"))
        self.font = pygame.font.SysFont("Helvetica", 18)
        self.on_result = on_result
        self.state = "main"  # 'main' or 'host_join'
        self.running = True
        # Prépare les drapeaux
        self.flag_size = 32
        self.flag_fr = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "france.png")).convert_alpha(),
            (self.flag_size, self.flag_size)
        )
        self.flag_uk = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "uk.png")).convert_alpha(),
            (self.flag_size, self.flag_size)
        )
        self.update_flag_rects()
        self.loop()

    def update_flag_rects(self):
        margin = 12
        x = self.screen.get_width() - self.flag_size - margin
        y_fr = self.screen.get_height() - 2*self.flag_size - margin - 8
        y_uk = self.screen.get_height() - self.flag_size - margin
        self.flag_fr_rect = pygame.Rect(x, y_fr, self.flag_size, self.flag_size)
        self.flag_uk_rect = pygame.Rect(x, y_uk, self.flag_size, self.flag_size)

    def draw_flags(self):
        # Affiche les drapeaux en bas à droite
        for flag, rect in [(self.flag_fr, self.flag_fr_rect), (self.flag_uk, self.flag_uk_rect)]:
            pygame.draw.circle(self.screen, (255,255,255), rect.center, self.flag_size//2+2)
            pygame.draw.circle(self.screen, (200,200,200), rect.center, self.flag_size//2+2, 2)
            self.screen.blit(flag, rect)

    def draw_main(self):
        self.screen.fill((240, 240, 240))
        label = self.font.render(traduire("jouer_local_ou_online"), True, (0,0,0))
        self.screen.blit(label, (30, 20))
        self.draw_button((30, 70, 120, 40), traduire("local"))
        self.draw_button((180, 70, 120, 40), traduire("reseau"))
        self.draw_flags()
        pygame.display.flip()

    def draw_host_join(self):
        self.screen.fill((240, 240, 240))
        label = self.font.render(traduire("host_or_join"), True, (0,0,0))
        self.screen.blit(label, (30, 20))
        self.draw_button((30, 70, 120, 40), traduire("host"))
        self.draw_button((180, 70, 120, 40), traduire("join"))
        self.draw_flags()
        pygame.display.flip()

    def draw_button(self, rect, text):
        pygame.draw.rect(self.screen, (76, 175, 80), rect)
        pygame.draw.rect(self.screen, (0,0,0), rect, 2)
        label = self.font.render(text, True, (255,255,255))
        self.screen.blit(label, (rect[0]+10, rect[1]+8))

    def loop(self):
        while self.running:
            if self.state == "main":
                self.draw_main()
            elif self.state == "host_join":
                self.draw_host_join()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # Gestion clic sur drapeaux
                    if self.flag_fr_rect.collidepoint(event.pos):
                        set_language("fr")
                        pygame.time.wait(120)
                        continue
                    if self.flag_uk_rect.collidepoint(event.pos):
                        set_language("en")
                        pygame.time.wait(120)
                        continue
                    if self.state == "main":
                        if 30 <= x < 150 and 70 <= y < 110:
                            self.running = False
                            self.on_result("local")
                        elif 180 <= x < 300 and 70 <= y < 110:
                            self.state = "host_join"
                    elif self.state == "host_join":
                        if 30 <= x < 150 and 70 <= y < 110:
                            self.running = False
                            self.on_result("host")
                        elif 180 <= x < 300 and 70 <= y < 110:
                            self.running = False
                            self.on_result("join")