import pygame
import random
import math
import src
import ui

# todo: 
# include game state 
# levels
# fix minimap
# fix dash effect
# scoretracker
# enemy spawner
# healther spawner
# power-ups
# boss-enemies
# sound effects
# doors
# stealth
# enemy percept
# allies

pygame.init()

WIDTH, HEIGHT = 1400, 800
CAMERA_WIDTH, CAMERA_HEIGHT = WIDTH * 15, HEIGHT * 15
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hyperion Alpha")
clock = pygame.time.Clock()

player = src.Player(400, 300, 20)
enemies = [src.Enemy(100 + i * 200, 100, 20) for i in range(5)]
camera = ui.Camera(CAMERA_WIDTH, CAMERA_HEIGHT)

map_size = (WIDTH, HEIGHT)
wall_size = (32, 32)
prob = 0.2
wall_grid = src.createGrid((CAMERA_WIDTH, CAMERA_HEIGHT), (50, 50), player, enemies, prob)
walls = src.createWalls(wall_grid, (50, 50))
minimap = pygame.Surface((map_size[0]//16, map_size[1]//16))
ui.draw_wall_rects(wall_grid, wall_size, minimap, (250, 250, 250))
# src.drawMinimap(minimap, (800, 600), (200, 150), player, enemy, walls)

projectiles = pygame.sprite.Group()
enemy_projectiles = pygame.sprite.Group()

health_pickups = [
    src.HealthPickup(200, 200, 20),
    src.HealthPickup(400, 400, 20),
    src.HealthPickup(600, 200, 20)
]

game_world_rect = pygame.Rect(0, 0, CAMERA_WIDTH, CAMERA_HEIGHT)
viewport = pygame.Rect(0, 0, WIDTH, HEIGHT)

running = True
paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = not paused  # toggle pause on/off

    if paused:
        ui.pause_screen(screen)
        continue

    if player.health <= 0:
        def start_over():
            global player, enemies
            player = src.Player(400, 300, 20)
            enemies = [src.Enemy(100, 100, 20), src.Enemy(300, 100, 20), src.Enemy(500, 100, 20)]

        def exit_game():
            global running
            running = False

        ui.game_over_screen(screen, start_over, exit_game)
        continue

    keys = pygame.key.get_pressed()
    player.move(keys, game_world_rect, walls)
    player.dash(keys, game_world_rect)
    player.switch_weapon(keys)  # Check for weapon switching
    player.update_stamina()
    mouse_pos = pygame.mouse.get_pos()
    # Adjust mouse position with camera offset
    adj_mouse_pos = [mouse_pos[0] - camera.camera.x, mouse_pos[1] - camera.camera.y]
    player.aim(adj_mouse_pos, camera)
    player.shoot(keys, projectiles, adj_mouse_pos, camera)
    projectiles.update()

    for enemy in enemies:
        enemy.follow_player(player, enemies, game_world_rect)
        enemy.shoot(player, enemy_projectiles)
        enemy_projectiles.update()

    viewport.center = player.rect.center
    viewport.clamp_ip(game_world_rect)

    player.update_dash_effect()  # Update the dash effect
    screen.fill("#222222")  # Clear the screen

    for wall in walls:
        pygame.draw.rect(screen, "#555555", wall.move(-viewport.x, -viewport.y))

    # Draw game objects relative to the viewport
    screen.blit(player.image, player.rect.move(-viewport.x, -viewport.y))  # Draw the player
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect.move(-viewport.x, -viewport.y))  # Draw the enemy
    for proj in projectiles:
        screen.blit(proj.image, proj.rect.move(-viewport.x, -viewport.y))  # Draw player projectiles
    for proj in enemy_projectiles:
        screen.blit(proj.image, proj.rect.move(-viewport.x, -viewport.y))  # Draw enemy projectiles
    for pickup in health_pickups:
        screen.blit(pickup.image, pickup.rect.move(-viewport.x, -viewport.y))  # Draw health pickups
    for pickup in health_pickups:
        if player.rect.colliderect(pickup.rect):
            player.health += pickup.health_restore
            if player.health > 100:
                player.health = 100
            pickup.rect.x = -1000  # Move the health pickup off-screen to simulate pickup
            pickup.rect.y = -1000

    # Collision detection and damage handling
    for proj in projectiles:
        for enemy in enemies:
            if proj.rect.colliderect(enemy.rect):
                enemy.take_damage(10)
                proj.kill()  # Remove projectile from the game

    for proj in enemy_projectiles:
        if proj.rect.colliderect(player.rect):
            player.take_damage(5)
            proj.kill()  # Remove projectile from the game

    # Remove dead enemies from the list
    enemies = [enemy for enemy in enemies if enemy.health > 0]
    health_percentage = player.health / 100
    enemies = [enemy for enemy in enemies if enemy.health > 0]
    health_percentage = player.health / 100
    ui.draw_health_bar(screen, 20, 20, 200, 20, health_percentage)
    stamina_percentage = player.stamina / player.max_stamina
    ui.draw_stamina_bar(screen, 20, 50, 200, 20, stamina_percentage)
    # player.draw_dash_effect(screen, camera)  # Draw the dash effect
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
