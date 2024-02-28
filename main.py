import pygame
import time
import random
import sys
import math
import pickle

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1500, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FIRE ZE MISSILES!")

BG = pygame.image.load("stars_bg.png")

PLAYER_WIDTH = 75
PLAYER_HEIGHT = 75

explosions_to_draw = []

PLAYER_SURFACE = pygame.transform.scale(pygame.image.load("player_img1.png"), (100, 100))
PLAYER_SURFACE_RIGHT = pygame.transform.scale(pygame.image.load("player_right.png"), (100, 100))
PLAYER_SURFACE_LEFT = pygame.transform.scale(pygame.image.load("player_left.png"), (100, 100))

PLAYER_VEL = 28
PLAYER_BULLET_WIDTH = 25
PLAYER_BULLET_HEIGHT = 20
ENEMY_BULLET_WIDTH = 21
ENEMY_BULLET_HEIGHT = 15
ENEMY2_SURFACE = pygame.transform.scale(pygame.image.load("enemy2.png"), (100, 100))
BULLET_VEL = 17

green_bullet_image = pygame.image.load("green_bullet.png").convert_alpha()
enemy_bullet_image = pygame.image.load("bullets.png").convert_alpha()

explosion_images = [pygame.image.load(f"explosion{i}.png").convert_alpha() for i in range(1, 8)]
explosion_frame = 0

FONT = pygame.font.SysFont("Lucida Console Bold", 45)
LOSE_FONT = pygame.font.SysFont("Lucida Console Bold", 65)

collisions = []
collisions_to_draw = []

FRAME_DELAY = 5

player_rect = pygame.Rect(WIDTH / 2 - PLAYER_WIDTH / 2, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)


class EnemyProjectile:
    def __init__(self, x, y, vel):
        self.x = x
        self.y = y
        self.vel = vel

    def update(self):
        self.y += self.vel


class Enemy:
    def __init__(self, x, y, vel):
        self.x = x
        self.y = y
        self.vel = vel
        self.projectiles = []
        self.fire_cooldown = 0
        self.health = 1000

    def draw(self):
        WIN.blit(ENEMY2_SURFACE, (self.x, self.y))

    def fire_projectile(self):
        projectile_x = self.x + PLAYER_WIDTH // 2 - ENEMY_BULLET_WIDTH // 2
        projectile_y = self.y + PLAYER_HEIGHT
        self.projectiles.append(pygame.Rect(projectile_x, projectile_y, ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT))

    def update_projectiles(self):
        for projectile in self.projectiles:
            projectile.y += BULLET_VEL

        self.projectiles = [projectile for projectile in self.projectiles if projectile.y < HEIGHT]


moving_right = False


def draw(player_rect, elapsed_time, bullets, enemy_projectiles, score, lives, hit):
    global explosion_frame
    if not hit:
        explosion_frame = 0

    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"TIME: {round(elapsed_time)}s", 1, "yellow")
    score_text = FONT.render(f"Score: {score:,}", 1, "lime")
    lives_text = FONT.render(f"LIVES: {lives}", 1, "red")

    WIN.blit(time_text, (30, 30))
    WIN.blit(score_text, (30, 90))
    WIN.blit(lives_text, (30, 150))


    if moving_right:
        WIN.blit(PLAYER_SURFACE_RIGHT, (player_rect.x, player_rect.y))
    else:
        WIN.blit(PLAYER_SURFACE_LEFT, (player_rect.x, player_rect.y))

    for bullet_info in bullets:
        bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
        if is_enemy_bullet:
            WIN.blit(enemy_bullet_image, (bullet.x, bullet.y))
        else:
            WIN.blit(green_bullet_image, (bullet.x, bullet.y))

    for projectile in enemy_projectiles:
        WIN.blit(enemy_bullet_image, (projectile.x, projectile.y))

    for explosion_coords in explosions_to_draw:
        x, y = explosion_coords
        if hit and explosion_frame < len(explosion_images) and pygame.time.get_ticks() % FRAME_DELAY == 0:
            WIN.blit(explosion_images[explosion_frame], (x, y))
            explosion_frame += 1
        else:
            explosions_to_draw.remove(explosion_coords)
            explosion_frame = 0
            hit = False

    pygame.display.update()


def display_high_scores(scores, new_score=None):
    print(f"Displaying high scores: scores={scores}, new_score={new_score}")
    high_scores = load_scores()
    WIN.blit(BG, (0, 0))
    high_scores_text = LOSE_FONT.render("HIGH SCORES", 1, "Gold")
    WIN.blit(high_scores_text, (550, 250))

    y_position = 350
    for i, (score, name) in enumerate(scores, start=1):
        score_text = LOSE_FONT.render(f"{i}. {name}: {score:,}", 1, "white")
        WIN.blit(score_text, (550, y_position))
        y_position += 70

    if new_score is not None:
        new_score_text = LOSE_FONT.render(f"Your Score: {new_score:,}", 1, "white")
        WIN.blit(new_score_text, (550, y_position + 70))

    pygame.display.update()
    pygame.time.delay(2000)


def save_scores(high_scores):
    print("Saving scores:", high_scores)
    with open('high_scores.pkl', 'wb') as file:
        pickle.dump(high_scores, file)


def load_scores():
    try:
        with open('high_scores.pkl', 'rb') as file:
            high_scores = pickle.load(file)
    except FileNotFoundError:
        high_scores = []

    return high_scores

def main():
    global keys, player_rect, moving_right, explosion_frame
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
    enemy_projectiles = []
    hit = False
    firing = False

    player_bullet_cooldown = 0
    player_bullet_cooldown_time = 20.0
    high_scores = load_scores()

    # Create an instance of the Enemy class
    enemy2 = Enemy(x=random.randint(0, WIDTH - PLAYER_WIDTH), y=random.randint(0, HEIGHT // 2), vel=5)

    while run:
        bullet_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEMOTION:
                rel_x, _ = pygame.mouse.get_rel()
                moving_right = rel_x > 0
                player_rect.x, player_rect.y = event.pos
                player_rect.x = max(0, min(WIDTH - PLAYER_WIDTH, player_rect.x))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    firing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    firing = False

                    bullet_x = player_rect.x + PLAYER_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2
                    bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT
                    player_bullets.append((pygame.Rect(bullet_x, bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT),
                                           False))
                    diagonal_bullet_x = player_rect.x + PLAYER_WIDTH // 6 - PLAYER_BULLET_WIDTH // 6 - int(
                        BULLET_VEL * round(math.cos(math.pi / 8)))
                    diagonal_bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT - int(
                        BULLET_VEL * round(math.sin(math.pi / 8)))
                    player_bullets.append(
                        (pygame.Rect(diagonal_bullet_x, diagonal_bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT),
                         False))
                    player_bullet_cooldown = player_bullet_cooldown_time
        firing = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]

        if firing and player_bullet_cooldown <= 0:
            bullet_x = player_rect.x + PLAYER_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2
            bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT
            player_bullets.append((pygame.Rect(bullet_x, bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT),
                                   False))
            diagonal_bullet_x = player_rect.x + PLAYER_WIDTH // 6 - PLAYER_BULLET_WIDTH // 6 - int(
                BULLET_VEL * round(math.cos(math.pi / 8)))
            diagonal_bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT - int(
                BULLET_VEL * round(math.sin(math.pi / 8)))
            player_bullets.append(
                (pygame.Rect(diagonal_bullet_x, diagonal_bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT),
                 False))
            player_bullet_cooldown = player_bullet_cooldown_time

        if player_bullet_cooldown > 0:
            player_bullet_cooldown -= clock.get_rawtime()

        if bullet_count > bullet_add_increment:
            for _ in range(8):
                bullet_x = random.randint(0, WIDTH - ENEMY_BULLET_WIDTH)
                bullet_y = -ENEMY_BULLET_HEIGHT
                bullets.append((pygame.Rect(bullet_x, bullet_y, ENEMY_BULLET_WIDTH, ENEMY_BULLET_HEIGHT), True))

            bullet_add_increment = max(100, bullet_add_increment - 20)
            bullet_count = 0

        bullets_to_remove = []
        player_bullets_to_remove = []
        for index, bullet_info in enumerate(bullets[:]):
            bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
            bullet.y += BULLET_VEL
            if bullet.y > HEIGHT:
                bullets_to_remove.append(index)
                score -= 50.00

            if player_rect.colliderect(bullet) and is_enemy_bullet:
                print("I'm Hit!")
                hit = True
                lives -= 1
                bullets_to_remove.append(index)
                explosions_to_draw.append((bullet.x, bullet.y))

        for player_bullet_info in player_bullets[:]:
            player_bullet, _ = player_bullet_info
            player_bullet.y -= BULLET_VEL

            for index, bullet_info in enumerate(bullets[:]):
                bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
                if player_bullet.colliderect(bullet):
                    bullets_to_remove.append(index)
                    player_bullets_to_remove.append(player_bullet_info)
                    score += 125.00
                    explosions_to_draw.append((bullet.x, bullet.y))

        bullets = [bullet_info for index, bullet_info in enumerate(bullets) if index not in bullets_to_remove]
        player_bullets = [player_bullet_info for player_bullet_info in player_bullets if
                          player_bullet_info not in player_bullets_to_remove]

        enemy2.update_projectiles()

        if random.randint(0, 100) < 2 and enemy2.fire_cooldown <= 0:
            enemy2.fire_projectile()
            enemy2.fire_cooldown = 1000  # Adjust the cooldown time as needed

        enemy2.fire_cooldown -= clock.get_rawtime()

        draw(player_rect, elapsed_time, bullets + player_bullets, enemy2.projectiles, score, lives, hit)

        if lives <= 0:
            display_high_scores(high_scores, score)
            entering_name = True
            player_name = ""
            while entering_name:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            entering_name = False
                        elif event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        else:
                            player_name += event.unicode

                name_input_text = LOSE_FONT.render(f"Enter your name: {player_name}", 1, "white")
                WIN.blit(name_input_text, (650, 400))

                pygame.display.update()
                clock.tick(30)

            high_scores.append((score, player_name))
            high_scores.sort(reverse=True)

            display_high_scores(high_scores, new_score=score)
            print("Displayed high scores")

            save_scores(high_scores)

            game_over_text = LOSE_FONT.render("GAME OVER", 1, "red")
            WIN.blit(game_over_text, (550, 150))
            WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2
            pygame.display.update()
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()
        else:
            run = True
            pygame.display.update()


if __name__ == "__main__":
    main()