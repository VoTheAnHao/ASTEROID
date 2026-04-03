import pygame
from BaseGame import BaseGame


class PhysicalGame(BaseGame):
    def run(self):

        while True:
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))

            self.common_events()

            # 🔥 PAUSE SYSTEM
            if self.paused:
                if self.pause_menu():
                    return  # quay về menu
                continue

            keys = pygame.key.get_pressed()

            if self.auto_mode:
                self.ai.control(self.ship, self.asteroids, self.bullets, "physical")

            else:
                # 🎮 DI CHUYỂN PHYSICAL
                self.ship.control_physical(keys)

                # 🎯 XOAY HƯỚNG BẮN
                self.ship.aim(keys)

            # 🔄 update timer
            self.ship.update()

            if not self.update_entities():
                return

            self.draw_status()
            pygame.display.flip()