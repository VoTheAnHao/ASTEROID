import pygame
from BaseGame import BaseGame

class ArcadeGame(BaseGame):
    def run(self):

        running = True

        while running:
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))

            self.common_events()

            # ===== PAUSE =====
            if self.paused:
                if self.pause_menu():
                    return  # về menu chính
                continue

            keys = pygame.key.get_pressed()

            if self.auto_mode:
                self.ai.control(self.ship, self.asteroids, self.bullets, "physical")
            else:
                self.ship.control_physical(keys)
                self.ship.aim(keys)

            self.ship.update()

            # 🔥 NHẬN KẾT QUẢ
            result = self.update_entities()

            if result is False:
                return   # EXIT / SAVE & EXIT

            self.draw_status()
            pygame.display.flip()