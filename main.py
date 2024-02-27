import pygame
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1500, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fighter Game 1")

# Background Image Variable
BG = pygame.image.load("fighting_bg.jpg")

# Player Variable
PLAYER_WIDTH = 150
PLAYER_HEIGHT = 150

player_pos = [WIDTH/2 - PLAYER_WIDTH/2, HEIGHT - PLAYER_HEIGHT]

player_image = pygame.image.load("player_img1.png")
player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

PLAYER_VEL = 10
BULLET_WIDTH = 10
BULLET_HEIGHT = 20
BULLET_VEL = 13

FONT = pygame.font.SysFont("comic sans", 60)

def draw(player, elapsed_time, bullets):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (650, 50))

    WIN.blit(player, player_rect)

    for bullet in bullets:
        pygame.draw.rect(WIN, "white", bullet)

    pygame.display.update()

# Main Game Loop
def main():
    run = True
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    bullet_add_increment = 1500
    bullet_count = 0

    bullets = []
    hit = False

    while run:
        bullet_count += clock.tick(60)      # Runs while loop 60 times/sec
        elapsed_time = time.time() - start_time

        if bullet_count > bullet_add_increment:
            for _ in range(3):
                bullet_x = random.randint(0, WIDTH - BULLET_WIDTH)
                bullet = pygame.Rect(bullet_x, -BULLET_HEIGHT, BULLET_WIDTH, BULLET_HEIGHT)
                bullets.append(bullet)

            bullet_add_increment = max(200, bullet_add_increment - 50)
            bullet_count = 0

        # Code in order to close window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.x - PLAYER_VEL >= 0:
            player_rect.x -= PLAYER_VEL

        if keys[pygame.K_RIGHT] and player_rect.x + PLAYER_VEL + PLAYER_WIDTH <= WIDTH:
            player_rect.x += PLAYER_VEL

        # Moving Bullets
        for bullet in bullets[:]:
            bullet.y += BULLET_VEL
            if bullet.y > HEIGHT:
                bullets.remove(bullet)
            elif bullet.y + bullet.height >= player_rect.y and bullet.colliderect(player_rect):
                bullets.remove(bullet)
                hit = True
                break

        if hit:
            lost_text = FONT.render("YOU SUCK!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(2000)
            break

        draw(player_image, elapsed_time, bullets)

    pygame.quit()

if __name__ == "__main__":
    main()