import pygame as pg
import random as rd
import math

# Constants
WIDTH, HEIGHT = 1400, 800
CAMERA_WIDTH, CAMERA_HEIGHT = WIDTH * 15, HEIGHT * 15
FPS = 60

# Player class
class Player(pg.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.original_image = pg.Surface((size, size))
        self.original_image.fill((0, 0, 255))  # Blue color
        self.rect = self.original_image.get_rect()
        self.rect.topleft = (x, y)
        self.pos = (self.rect.x, self.rect.y)
        self.speed = 5
        self.weapon1 = Pistol(10, 1, 0)  # Pistol
        self.weapon2 = Shotgun(30, 1, 0, 5, math.radians(45))  # Shotgun
        self.weapon3 = MachinGun(5, 0, 0)
        self.weapon = self.weapon1  # Set the default weapon
        self.dash_speed = 50
        self.shooting = False
        self.angle = 0
        self.health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.dash_cost = 25
        self.dash_cooldown = 30  # In frames (0.5 seconds at 60 FPS)
        self.dash_timer = 0
        self.dash_effect = None
        self.dash_effect_alpha = 255
        
    def rotate_image(self, angle):
        old_center = self.rect.center
        self.image = pg.transform.rotate(self.original_image.copy(), math.degrees(angle))
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def aim(self, mouse_pos, camera):
        dx = mouse_pos[0] - (self.rect.centerx - camera.camera.x)
        dy = mouse_pos[1] - (self.rect.centery - camera.camera.y)
        self.angle = math.atan2(dy, dx)
        self.rotate_image(self.angle)

    def switch_weapon(self, keys):
        if keys[pg.K_1]:
            self.weapon = self.weapon1
        elif keys[pg.K_2]:
            self.weapon = self.weapon2
        elif keys[pg.K_3]:
            self.weapon = self.weapon3

    def take_damage(self, amount):
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.rect.x = -1000  # Move the player off-screen to simulate despawning
                self.rect.y = -1000

    def dash(self, keys, game_world_rect):
        if keys[pg.K_SPACE] and self.stamina >= self.dash_cost and self.dash_timer == 0:
            self.stamina -= self.dash_cost
            self.dash_timer = self.dash_cooldown
            if keys[pg.K_w]:
                self.rect.y -= self.dash_speed
            if keys[pg.K_s]:
                self.rect.y += self.dash_speed
            if keys[pg.K_a]:
                self.rect.x -= self.dash_speed
            if keys[pg.K_d]:
                self.rect.x += self.dash_speed

            # Create the dash effect surface
            self.dash_effect = pg.Surface((self.rect.width, self.rect.height))
            self.dash_effect.fill((255, 255, 255))  # White color
            self.dash_effect.set_alpha(self.dash_effect_alpha)

        elif self.dash_timer > 0:
            self.dash_timer -= 1

    def update_dash_effect(self):
        if self.dash_timer > 0:
            self.dash_timer -= 1
            self.dash_effect_alpha = 128  # Set dash_effect_alpha to 128 for fade-out effect
            self.dash_effect = self.create_dash_effect()  # Create dash effect
        else:
            self.dash_effect_alpha = 0  # Set dash_effect_alpha to 0 when dash is not active
            self.dash_effect = None

    def create_dash_effect(self):
        effect_surface = pg.Surface((self.rect.width, self.rect.height))
        effect_surface.set_alpha(self.dash_effect_alpha)  # Set transparency
        effect_surface.fill((255, 255, 255))  # White color
        effect_rect = effect_surface.get_rect(center=self.rect.center)
        return effect_surface, effect_rect

    def draw_dash_effect(self, screen, camera):
        if self.dash_effect:
            effect_surface, effect_rect = self.dash_effect
            screen.blit(effect_surface, effect_rect.move(-camera.camera.x, -camera.camera.y))

    def update_stamina(self):
        if self.stamina < self.max_stamina and self.dash_timer == 0:
            self.stamina += 1

    def move(self, keys, game_world_rect, walls):
        prev_x = self.rect.x
        prev_y = self.rect.y

        if keys[pg.K_w]:  # W key
            self.rect.y -= self.speed
        if keys[pg.K_s]:  # S key
            self.rect.y += self.speed
        if keys[pg.K_a]:  # A key
            self.rect.x -= self.speed
        if keys[pg.K_d]:  # D key
            self.rect.x += self.speed

        # Keep player within the larger map boundaries
        self.rect.x = max(0, min(self.rect.x, CAMERA_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, CAMERA_HEIGHT - self.rect.height))

        # Check for collisions with walls
        if self.collide_with_walls(walls):
            self.rect.x = prev_x
            self.rect.y = prev_y

    def collide_with_walls(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

    def shoot(self, keys, projectiles, mouse_pos, camera, walls):
        if pg.mouse.get_pressed()[0]:  # Left mouse button
            self.shooting = True
            self.weapon.shoot(self, projectiles, mouse_pos, camera, walls)
        else:
            self.shooting = False
            self.weapon.update_shoot_timer()

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pg.Surface((size, size))
        self.image.fill((255, 0, 0))  # Red color
        self.rect = self.image.get_rect()
        self.pos = (self.rect.x, self.rect.y)
        self.rect.topleft = (x, y)
        self.health = 50
        self.speed = 3
        self.shoot_timer = 0
        self.prev_x = x
        self.prev_y = y
        self.shoot_cooldown = 60  # In frames (1 second at 60 FPS)

    def follow_player(self, player, enemies, game_world_rect, walls):
            self.prev_x = self.rect.x
            self.prev_y = self.rect.y

            dx = player.rect.x - self.rect.x
            dy = player.rect.y - self.rect.y
            dist = math.sqrt(dx * dx + dy * dy)
            stop_distance = 50  # Distance to stop before reaching the player

            if dist > stop_distance:
                self.rect.x += self.speed * dx / dist
                self.rect.y += self.speed * dy / dist

            # Keep enemy within the larger map boundaries
            self.rect.x = max(0, min(self.rect.x, CAMERA_WIDTH - self.rect.width))
            self.rect.y = max(0, min(self.rect.y, CAMERA_HEIGHT - self.rect.height))

            # Check for collisions with other enemies
            for other_enemy in enemies:
                if other_enemy is not self and self.rect.colliderect(other_enemy.rect):
                    self.rect.x = self.prev_x
                    self.rect.y = self.prev_y

            # Check for collisions with walls
            if self.collide_with_walls(walls):
                self.rect.x = self.prev_x
                self.rect.y = self.prev_y

    def collide_with_walls(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.rect.x = -1000  # Move the enemy off-screen to simulate despawning
            self.rect.y = -1000

    def shoot(self, player, projectiles, walls):
        if self.shoot_timer == 0:
            dx = player.rect.x - self.rect.x
            dy = player.rect.y - self.rect.y
            angle = math.atan2(dy, dx)
            proj = Projectile(self.rect.centerx, self.rect.centery, 5, angle, 10)
            projectiles.add(proj)
            proj.update(walls)  # Ensure the projectile gets the walls list
            self.shoot_timer = self.shoot_cooldown
        else:
            self.shoot_timer -= 1

class Projectile(pg.sprite.Sprite):
    def __init__(self, x, y, size, angle, speed):
        super().__init__()
        self.image = pg.Surface((size, size))
        self.image.fill("#ffcc00")  # Light blue color
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = speed
        self.angle = angle

    def update(self, walls):
        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)
        self.rect.x += dx
        self.rect.y += dy

        # Check for collisions with walls
        if self.collide_with_walls(walls):
            self.kill()  # Remove the projectile if it collides with a wall

    def collide_with_walls(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

class Weapon:
    def __init__(self, rate_of_fire, stability, recharge):
        self.rate_of_fire = rate_of_fire
        self.stability = stability
        self.recharge = recharge
        self.shoot_timer = 0

    def update_shoot_timer(self):
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def shoot(self, shooter, projectiles, mouse_pos, camera):
        pass

class Pistol(Weapon):
    def __init__(self, rate_of_fire, stability, recharge):
        super().__init__(rate_of_fire, stability, recharge)

    def shoot(self, shooter, projectiles, mouse_pos, camera, walls):
        if self.shoot_timer == 0:
            proj = Projectile(shooter.rect.centerx, shooter.rect.centery, 5, shooter.angle, 10)
            projectiles.add(proj)
            proj.update(walls)  # Ensure the projectile gets the walls list
            self.shoot_timer = self.rate_of_fire

class Shotgun(Weapon):
    def __init__(self, rate_of_fire, stability, recharge, num_pellets, spread_angle):
        super().__init__(rate_of_fire, stability, recharge)
        self.num_pellets = num_pellets
        self.spread_angle = spread_angle

    def shoot(self, shooter, projectiles, mouse_pos, camera, walls):
        if self.shoot_timer == 0:
            for i in range(self.num_pellets):
                angle = shooter.angle - (self.spread_angle / 2) + (i * self.spread_angle / (self.num_pellets - 1))
                proj = Projectile(shooter.rect.centerx, shooter.rect.centery, 5, angle, 10)
                projectiles.add(proj)
                proj.update(walls)  # Ensure the projectile gets the walls list
            self.shoot_timer = self.rate_of_fire
        else:
            self.update_shoot_timer()

class MachinGun(Weapon):
    def __init__(self, rate_of_fire, stability, recharge):
        super().__init__(rate_of_fire, stability, recharge)

    def shoot(self, shooter, projectiles, mouse_pos, camera, walls):
        dx = mouse_pos[0] - (shooter.rect.centerx - camera.camera.x)
        dy = mouse_pos[1] - (shooter.rect.centery - camera.camera.y)
        angle = math.atan2(dy, dx)
        proj = Projectile(shooter.rect.centerx, shooter.rect.centery, 5, angle, 10)
        projectiles.add(proj)
        proj.update(walls)  # Ensure the projectile gets the walls list


class HealthPickup(pg.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pg.Surface((size, size))
        self.image.fill((0, 255, 0))  # Green color
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health_restore = 25

class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pg.Surface((size, size))
        self.image.fill((128, 128, 128))  # Gray color
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

def createGrid(map_size, wall_size, player, enemies, prob):
    wall_grid = [[0 for _ in range(map_size[0] // wall_size[0])] for _ in range(map_size[1] // wall_size[1])]
    for i in range(map_size[1] // wall_size[1]):
        for j in range(map_size[0] // wall_size[0]):
            if (i, j) == (player.pos[1] // wall_size[1], player.pos[0] // wall_size[0]):
                wall_grid[i][j] = 0
            elif any((i, j) == (enemy.pos[1] // wall_size[1], enemy.pos[0] // wall_size[0]) for enemy in enemies):
                wall_grid[i][j] = 0
            elif i % 2 == 0 and j % 2 == 0 and rd.random() < prob and \
                any(((i - 1, j) == (player.pos[1] // wall_size[1], player.pos[0] // wall_size[0])) or \
                    ((i, j + 1) == (player.pos[1] // wall_size[1], player.pos[0] // wall_size[0])) or \
                    ((i - 1, j) == (enemy.pos[1] // wall_size[1], enemy.pos[0] // wall_size[0])) or \
                    ((i, j + 1) == (enemy.pos[1] // wall_size[1], enemy.pos[0] // wall_size[0])) for enemy in enemies):
                wall_grid[i][j] = 0
            elif i % 2 == 0 and j % 2 == 0 and rd.random() < prob:
                if rd.randint(1, 2) == 1:
                    wall_grid[i][j] = 1
                    if i - 1 >= 0:
                        wall_grid[i - 1][j] = 1
                else:
                    wall_grid[i][j] = 1
                    if j + 1 < len(wall_grid[0]):
                        wall_grid[i][j + 1] = 1
            elif i % 4 == 0 and j % 2 == 0 and rd.random() < prob:  # Create longer and thinner walls
                if j + 2 < len(wall_grid[0]):
                    wall_grid[i][j] = 1
                    wall_grid[i][j + 1] = 1
                    wall_grid[i][j + 2] = 1
                    if i + 1 < len(wall_grid):
                        wall_grid[i + 1][j] = 0
                        wall_grid[i + 1][j + 1] = 0
                        wall_grid[i + 1][j + 2] = 0
    return wall_grid

def createWalls(wall_grid, wall_size):
    walls = []
    for i in range(len(wall_grid)):
        for j in range(len(wall_grid[i])):
            if wall_grid[i][j] == 1:
                wall = pg.Rect(j*wall_size[0], i*wall_size[1], wall_size[0], wall_size[1])
                walls.append(wall)
    return walls

