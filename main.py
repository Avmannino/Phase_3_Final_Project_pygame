import pygame
import time
import random
import sys
import math

pygame.font.init()

WIDTH, HEIGHT = 1500, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FIRE ZE MISSILES!")

# Background Image Variable
BG = pygame.image.load("stars_bg.jpg")

# Player Variables
PLAYER_WIDTH = 125
PLAYER_HEIGHT = 75

# Load initial player image
PLAYER_SURFACE = pygame.transform.scale(pygame.image.load("player_img1.png"), (100, 100))
player_rect = pygame.Rect(WIDTH / 2 - PLAYER_WIDTH / 2, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

# Load right-facing player image
PLAYER_SURFACE_RIGHT = pygame.transform.scale(pygame.image.load("player_right.png"), (100, 100))

# Load left-facing player image
PLAYER_SURFACE_LEFT = pygame.transform.scale(pygame.image.load("player_left.png"), (100, 100))

PLAYER_VEL = 25
BULLET_WIDTH = 21
BULLET_HEIGHT = 15
BULLET_VEL = 15

# Load Bullets Sprite
green_bullet_image = pygame.image.load("green_bullet.png").convert_alpha()
enemy_bullet_image = pygame.image.load("bullets.png").convert_alpha()

FONT = pygame.font.SysFont("Lucida Console Bold", 45)
LOSE_FONT = pygame.font.SysFont("Lucida Console Bold", 65)

def draw(player_rect, elapsed_time, bullets, score, lives, hit, keys):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "yellow")
    score_text = FONT.render(f"Score: {score}", 1, "lime")
    lives_text = FONT.render(f"Lives: {lives}", 1, "red")

    WIN.blit(time_text, (1200, 30))
    WIN.blit(score_text, (1200, 90))
    WIN.blit(lives_text, (1200, 150))

    # Use the right-facing player image when moving to the right
    if keys[pygame.K_RIGHT]:
        WIN.blit(PLAYER_SURFACE_RIGHT, (player_rect.x, player_rect.y))
    # Use the left-facing player image when moving to the left
    elif keys[pygame.K_LEFT]:
        WIN.blit(PLAYER_SURFACE_LEFT, (player_rect.x, player_rect.y))
    else:
        WIN.blit(PLAYER_SURFACE, (player_rect.x, player_rect.y))

    for bullet_info in bullets:
        bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
        if is_enemy_bullet:
            WIN.blit(enemy_bullet_image, (bullet.x, bullet.y))
        else:
            WIN.blit(green_bullet_image, (bullet.x, bullet.y))

# Main Game Loop
def main():
    run = True
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    score = 0
    lives = 3
    bullet_add_increment = 1000
    bullet_count = 0
    initial_delay = 1500

    bullets = []
    player_bullets = []
    hit = False

    player_bullet_cooldown = 0
    player_bullet_cooldown_time = 5.0

    while run:
        bullet_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        player_rect.x -= keys[pygame.K_LEFT] * PLAYER_VEL if player_rect.x - PLAYER_VEL >= 0 else 0
        player_rect.x += keys[pygame.K_RIGHT] * PLAYER_VEL if player_rect.x + PLAYER_VEL + PLAYER_WIDTH <= WIDTH else 0
        player_rect.y -= keys[pygame.K_UP] * PLAYER_VEL if player_rect.y - PLAYER_VEL >= 0 else 0
        player_rect.y += keys[pygame.K_DOWN] * PLAYER_VEL if player_rect.y + PLAYER_VEL + PLAYER_HEIGHT <= HEIGHT else 0

        if keys[pygame.K_SPACE] and player_bullet_cooldown <= 0:
            bullet_x = player_rect.x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
            bullet_y = player_rect.y - BULLET_HEIGHT
            player_bullets.append((pygame.Rect(bullet_x, bullet_y, BULLET_WIDTH, BULLET_HEIGHT), False))
            diagonal_bullet_x = player_rect.x + PLAYER_WIDTH // 6 - BULLET_WIDTH // 6 - int(
                BULLET_VEL * round(math.cos(math.pi / 8)))
            diagonal_bullet_y = player_rect.y - BULLET_HEIGHT - int(BULLET_VEL * round(math.sin(math.pi / 8)))
            player_bullets.append(
                (pygame.Rect(diagonal_bullet_x, diagonal_bullet_y, BULLET_WIDTH, BULLET_HEIGHT), False))
            player_bullet_cooldown = player_bullet_cooldown_time

        if player_bullet_cooldown > 0:
            player_bullet_cooldown -= clock.get_rawtime()

        if bullet_count > bullet_add_increment:
            for _ in range(8):
                bullet_x = random.randint(0, WIDTH - BULLET_WIDTH)
                bullet_y = -BULLET_HEIGHT
                bullets.append((pygame.Rect(bullet_x, bullet_y, BULLET_WIDTH, BULLET_HEIGHT), True))

            bullet_add_increment = max(100, bullet_add_increment - 20)
            bullet_count = 0

        bullets_to_remove = []
        player_bullets_to_remove = []
        for index, bullet_info in enumerate(bullets[:]):
            bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
            bullet.y += BULLET_VEL
            if bullet.y > HEIGHT:
                bullets_to_remove.append(index)
                score -= 52.25

            if player_rect.colliderect(bullet) and is_enemy_bullet:
                hit = True
                lives -= 1
                bullets_to_remove.append(index)

        for player_bullet_info in player_bullets[:]:
            player_bullet, _ = player_bullet_info
            player_bullet.y -= BULLET_VEL

            for index, bullet_info in enumerate(bullets[:]):
                bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
                if player_bullet.colliderect(bullet):
                    bullets_to_remove.append(index)
                    player_bullets_to_remove.append(player_bullet_info)
                    score += 105.75

        bullets = [bullet_info for index, bullet_info in enumerate(bullets) if index not in bullets_to_remove]
        player_bullets = [player_bullet_info for player_bullet_info in player_bullets if
                           player_bullet_info not in player_bullets_to_remove]

        draw(player_rect, elapsed_time, bullets + player_bullets, score, lives, hit, keys)

        if lives <= 0:
            game_over_text = LOSE_FONT.render("GAME OVER", 1, "red")
            WIN.blit(game_over_text, (
            WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()
        else:
            run = True
            pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
