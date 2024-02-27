import pygame
import time
import random
import sys

pygame.font.init()

WIDTH, HEIGHT = 1500, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FIRE ZE MISSILES!")

# Background Image Variable
BG = pygame.image.load("stars_bg.jpg")

# Player Variable
PLAYER_WIDTH = 85
PLAYER_HEIGHT = 85

player_pos = [WIDTH / 2 - PLAYER_WIDTH / 2, HEIGHT - PLAYER_HEIGHT]

PLAYER_SURFACE = pygame.transform.scale(pygame.image.load("player_img1.png"), (100, 100))
player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

PLAYER_VEL = 18
BULLET_WIDTH = 10
BULLET_HEIGHT = 15
BULLET_VEL = 13

# Load Bullets Sprite
green_bullet_image = pygame.image.load("green_bullet.png").convert_alpha()
enemy_bullet_image = pygame.image.load("bullets.png").convert_alpha()  # New image for enemy bullets

FONT = pygame.font.SysFont("comic sans", 60)

def draw(player_rect, elapsed_time, bullets, score, player_pos):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    score_text = FONT.render(f"Score: {score}", 1, "white")

    WIN.blit(time_text, (650, 50))
    WIN.blit(score_text, (650, 110))

    WIN.blit(PLAYER_SURFACE, (player_rect.x, player_rect.y))

    for bullet_info in bullets:
        bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
        if is_enemy_bullet:
            WIN.blit(enemy_bullet_image, (bullet.x, bullet.y))
        else:
            WIN.blit(green_bullet_image, (bullet.x, bullet.y))

    pygame.display.update()

# Main Game Loop
def main():
    run = True
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    score = 0

    bullet_add_increment = 2000
    bullet_count = 0

    bullets = []
    player_bullets = []  # Added a list for player bullets
    hit = False

    while run:
        bullet_count += clock.tick(60)  # Runs while loop 60 times/sec
        elapsed_time = time.time() - start_time

        # Random Bullet Code
        if bullet_count > bullet_add_increment:
            for _ in range(9):
                bullet_x = random.randint(0, WIDTH - BULLET_WIDTH)
                bullet_y = -BULLET_HEIGHT
                # Append a tuple with the bullet rectangle and a flag indicating it's an enemy bullet
                bullets.append((pygame.Rect(bullet_x, bullet_y, BULLET_WIDTH, BULLET_HEIGHT), True))

            bullet_add_increment = max(200, bullet_add_increment - 50)
            bullet_count = 0

        # Code in order to close window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Character Movements
        keys = pygame.key.get_pressed()
        player_rect.x -= keys[pygame.K_LEFT] * PLAYER_VEL if player_rect.x - PLAYER_VEL >= 0 else 0
        player_rect.x += keys[pygame.K_RIGHT] * PLAYER_VEL if player_rect.x + PLAYER_VEL + PLAYER_WIDTH <= WIDTH else 0
        player_rect.y -= keys[pygame.K_UP] * PLAYER_VEL if player_rect.y - PLAYER_VEL >= 0 else 0
        player_rect.y += keys[pygame.K_DOWN] * PLAYER_VEL if player_rect.y + PLAYER_VEL + PLAYER_HEIGHT <= HEIGHT else 0

        # Shooting Player Bullets
        if keys[pygame.K_SPACE]:
            bullet_x = player_rect.x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
            bullet_y = player_rect.y - BULLET_HEIGHT
            # Append a tuple with the bullet rectangle and a flag indicating it's a player bullet
            player_bullets.append((pygame.Rect(bullet_x, bullet_y, BULLET_WIDTH, BULLET_HEIGHT), False))

        # Moving Bullets
        bullets_to_remove = []
        for index, bullet_info in enumerate(bullets[:]):
            bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
            bullet.y += BULLET_VEL  # Bullets move downward
            if bullet.y > HEIGHT:
                bullets_to_remove.append(index)
                score -= 50.00  # Decrease score for each missed bullet

            # Check for collisions between player rectangle and enemy bullets
            if player_rect.colliderect(bullet) and is_enemy_bullet:
                hit = True

        # Moving Player Bullets
        player_bullets_to_remove = []
        for player_bullet_info in player_bullets[:]:
            player_bullet, _ = player_bullet_info
            player_bullet.y -= BULLET_VEL  # Player bullets move upward

            # Check for collisions between player bullets and falling bullets
            for index, bullet_info in enumerate(bullets[:]):
                bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
                if player_bullet.colliderect(bullet):
                    bullets_to_remove.append(index)
                    player_bullets_to_remove.append(player_bullet_info)
                    score += 105.00  # Increase score for each hit

        # Remove collided bullets
        bullets = [bullet_info for index, bullet_info in enumerate(bullets) if index not in bullets_to_remove]
        player_bullets = [player_bullet_info for player_bullet_info in player_bullets if player_bullet_info not in player_bullets_to_remove]

        draw(player_rect, elapsed_time, bullets + player_bullets, score, player_pos)

        if hit:
            lost_text = FONT.render("YOU LOSE!", 1, "white")
            WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()

    pygame.quit()

if __name__ == "__main__":
    main()
