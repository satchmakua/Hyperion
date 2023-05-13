import pygame as pg
import random as rd
import math

WIDTH, HEIGHT = 1400, 800
CAMERA_WIDTH, CAMERA_HEIGHT = WIDTH * 15, HEIGHT * 15
FPS = 60

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + WIDTH // 2
        y = -target.rect.y + HEIGHT // 2

        # Limit scrolling to map boundaries
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)

        self.camera = pg.Rect(x, y, self.width, self.height)

def draw_health_bar(screen, x, y, width, height, health_percentage):
    if health_percentage < 0:
        health_percentage = 0

    filled_width = int(width * health_percentage)

    outline_rect = pg.Rect(x, y, width, height)
    filled_rect = pg.Rect(x, y, filled_width, height)

    pg.draw.rect(screen, (255, 0, 0), filled_rect)  # Red color for the filled area
    pg.draw.rect(screen, (255, 255, 255), outline_rect, 2)  # White color for the outline

def draw_stamina_bar(screen, x, y, width, height, stamina_percentage):
    if stamina_percentage < 0:
        stamina_percentage = 0

    filled_width = int(width * stamina_percentage)

    outline_rect = pg.Rect(x, y, width, height)
    filled_rect = pg.Rect(x, y, filled_width, height)

    pg.draw.rect(screen, (0, 255, 255), filled_rect)  # Cyan color for the filled area
    pg.draw.rect(screen, (255, 255, 255), outline_rect, 2)

def draw_button(screen, x, y, width, height, text, font, color, text_color):
    button_rect = pg.Rect(x, y, width, height)
    pg.draw.rect(screen, color, button_rect)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

def game_over_screen(screen, start_over_action, exit_action):
    game_over = True
    font = pg.font.Font(None, 36)
    button_width, button_height = 200, 60

    while game_over:
        screen.fill((0, 0, 0))

        # Draw "Game Over" text
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(game_over_text, game_over_rect)

        # Draw "Start Over" button
        start_over_button_rect = pg.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - button_height, button_width, button_height)
        draw_button(screen, *start_over_button_rect, "Start Over", font, (0, 255, 0), (255, 255, 255))

        # Draw "Exit" button
        exit_button_rect = pg.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + button_height, button_width, button_height)
        draw_button(screen, *exit_button_rect, "Exit", font, (255, 0, 0), (255, 255, 255))

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = False
                exit_action()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if start_over_button_rect.collidepoint(pg.mouse.get_pos()):
                    game_over = False
                    start_over_action()
                elif exit_button_rect.collidepoint(pg.mouse.get_pos()):
                    game_over = False
                    exit_action()

def draw_wall_rects(wall_grid, wall_size, minimap, color_tuple):
    for i in range(len(wall_grid)):
        for j in range(len(wall_grid[i])):
            if wall_grid[i][j] == 1:
                wall_rect = pg.Rect(j*wall_size[0]//16, i*wall_size[1]//16, wall_size[0]//16, wall_size[1]//16)
                pg.draw.rect(minimap, color_tuple, wall_rect)

def drawMinimap(minimap, map_size, minimap_size, player, enemy, walls):
    minimap.fill((0, 0, 0))

    # Draw walls on minimap
    for wall in walls:
        wall_rect_minimap = pg.Rect(wall.x * minimap_size[0] // map_size[0], wall.y * minimap_size[1] // map_size[1],
                                     wall.width * minimap_size[0] // map_size[0], wall.height * minimap_size[1] // map_size[1])
        pg.draw.rect(minimap, (128, 128, 128), wall_rect_minimap)

    # Draw player on minimap
    player_rect_minimap = pg.Rect(player.pos[0] * minimap_size[0] // map_size[0], player.pos[1] * minimap_size[1] // map_size[1], 5, 5)
    pg.draw.rect(minimap, (255, 0, 0), player_rect_minimap)

    enemy_rect_minimap = pg.Rect(enemy.pos[0] * minimap_size[0] // map_size[0], enemy.pos[1] * minimap_size[1] // map_size[1], 5, 5)
    pg.draw.rect(minimap, (0, 0, 255), enemy_rect_minimap)

def pause_screen(screen):
    font = pg.font.SysFont(None, 60)
    text = font.render("Paused", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    font = pg.font.SysFont(None, 30)
    text = font.render("Press Enter to resume or Esc to exit", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + text.get_height() // 2))
