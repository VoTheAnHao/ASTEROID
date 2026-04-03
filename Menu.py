import pygame
import sys

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


class Menu:
    def __init__(self, screen, clock, width, height, saved_game=None):
        self.screen = screen
        self.clock = clock
        self.width = width
        self.height = height

        self.saved_game = saved_game    
        from sound_manager import SoundManager
        self.sound = SoundManager()
        self.volume = 0.5
        self.dragging = False
        self.sound.set_volume(self.volume)
        self.sound.stop_all()
        self.sound.play_music(self.sound.menu_music)

        self.font_big = pygame.font.SysFont("arial", 50)
        self.font_small = pygame.font.SysFont("arial", 30)

        self.state = "main"

    def draw_button(self, text, y):
        rect = pygame.Rect(self.width//2 - 100, y, 200, 50)

        pygame.draw.rect(self.screen, GRAY, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 2)

        txt = self.font_small.render(text, True, WHITE)
        self.screen.blit(
            txt,
            (rect.centerx - txt.get_width()//2,
             rect.centery - txt.get_height()//2)
        )

        return rect

    def run(self):
        from leaderboard import Leaderboard
        lb = Leaderboard()

        while True:
            self.screen.fill(BLACK)

            b_continue = b_start = b_lb = b_quit = None
            b1 = b2 = b3 = None
            slider = None

            # ================= MAIN MENU =================
            if self.state == "main":
                title = self.font_big.render("ASTEROIDS", True, WHITE)
                self.screen.blit(title, (self.width//2 - 150, 100))

                y = 220

                # 🔥 CONTINUE (chỉ khi có game)
                if self.saved_game:
                    b_continue = self.draw_button("CONTINUE", y)
                    y += 70

                b_start = self.draw_button("START", y)
                y += 70

                b_lb = self.draw_button("LEADERBOARD", y)
                y += 70

                b_quit = self.draw_button("QUIT", y)

                slider = self.draw_volume(450)

            # ================= MODE =================
            elif self.state == "mode":
                title = self.font_big.render("SELECT MODE", True, WHITE)
                self.screen.blit(title, (self.width//2 - 200, 100))

                b1 = self.draw_button("PHYSICAL", 250)
                b2 = self.draw_button("ARCADE", 320)
                b3 = self.draw_button("BACK", 390)

            # ================= LEADERBOARD =================
            elif self.state == "leaderboard":
                title = self.font_big.render("LEADERBOARD", True, WHITE)
                self.screen.blit(title, (self.width//2 - 200, 50))

                data = lb.get_top()

                for i, entry in enumerate(data[:5]):
                    txt = self.font_small.render(
                        f"{i+1}. {entry.get('name','???')} | Score: {entry['score']} | Time: {entry['time']}",
                        True, WHITE
                    )
                    self.screen.blit(txt, (100, 150 + i*40))

                b3 = self.draw_button("BACK", 450)

                slider = self.draw_volume(450)

            pygame.display.flip()
            self.clock.tick(60)

            # ================= EVENT =================
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # ===== CLICK =====
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:

                    # 🎚 slider
                    if slider and slider.collidepoint(e.pos):
                        self.dragging = True

                    # ===== MAIN =====
                    elif self.state == "main":

                        if b_continue and b_continue.collidepoint(e.pos):
                            return "continue"

                        elif b_start and b_start.collidepoint(e.pos):
                            self.state = "mode"

                        elif b_lb and b_lb.collidepoint(e.pos):
                            self.state = "leaderboard"

                        elif b_quit and b_quit.collidepoint(e.pos):
                            pygame.quit()
                            sys.exit()

                    # ===== MODE =====
                    elif self.state == "mode":

                        if b1 and b1.collidepoint(e.pos):
                            return "physical"

                        elif b2 and b2.collidepoint(e.pos):
                            return "arcade"

                        elif b3 and b3.collidepoint(e.pos):
                            self.state = "main"

                    # ===== LEADERBOARD =====
                    elif self.state == "leaderboard":

                        if b3 and b3.collidepoint(e.pos):
                            self.state = "main"

                    # ===== RELEASE =====
                    if e.type == pygame.MOUSEBUTTONUP:
                        self.dragging = False

                    # ===== DRAG =====
                    if e.type == pygame.MOUSEMOTION and self.dragging:
                        if slider:
                            x = e.pos[0]
                            rel = x - slider.x
                            self.volume = max(0, min(1, rel / slider.width))
                            self.sound.set_volume(self.volume)

    def draw_volume(self, y):

        bar_x = self.width//2 - 100
        bar_width = 200

        # thanh nền
        pygame.draw.rect(self.screen, GRAY, (bar_x, y, bar_width, 10))

        # nút kéo
        knob_x = bar_x + int(self.volume * bar_width)
        pygame.draw.circle(self.screen, WHITE, (knob_x, y + 5), 8)

        # text
        txt = self.font_small.render(f"VOLUME {int(self.volume*100)}%", True, WHITE)
        self.screen.blit(txt, (bar_x, y - 30))

        return pygame.Rect(bar_x, y, bar_width, 10)