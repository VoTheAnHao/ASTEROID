
import math
from turtle import mode
from bullet import Bullet

class AIController:
    def __init__(self):
        self.shoot_cooldown = 0

    def control(self, ship, asteroids, bullets, mode):
        if not asteroids:
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        target = min(
            asteroids,
            key=lambda a: math.hypot(a.x - ship.x, a.y - ship.y)
        )

        dx = target.x - ship.x
        dy = target.y - ship.y
        dist = math.hypot(dx, dy)

        target_angle = math.degrees(math.atan2(dy, dx))
        diff = (target_angle - ship.angle + 180) % 360 - 180

        if diff > 5:
            ship.rotate(1)
        elif diff < -5:
            ship.rotate(-1)

        if mode == "arcade":
            if dist > 120:
                ship.forward()
            else:
                ship.stop()
        else:
            if dist > 150:
                ship.thrust()

        if abs(diff) < 8 and dist < 350 and self.shoot_cooldown == 0:
            
            gun_x, gun_y = ship.get_gun_position()

            if ship.power_mode:
                for offset in [-15, 0, 15]:
                    bullets.append(
                        Bullet(
                            gun_x,
                            gun_y,
                            ship.angle + offset,
                            ship.vel_x,
                            ship.vel_y
                        )
                    )
            else:
                bullets.append(
                    Bullet(
                    gun_x,
                    gun_y,
                    ship.angle,
                    ship.vel_x,
                    ship.vel_y
                )
                )    

            self.shoot_cooldown = 20
