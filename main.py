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

PLAYER_SURFACE = pygame.transform.scale(pygame.image.load("player_img1.png"), (100, 100))
PLAYER_SURFACE_RIGHT = pygame.transform.scale(pygame.image.load("player_right.png"), (100, 100))
PLAYER_SURFACE_LEFT = pygame.transform.scale(pygame.image.load("player_left.png"), (100, 100))

PLAYER_VEL = 28
PLAYER_BULLET_WIDTH = 25
PLAYER_BULLET_HEIGHT = 20

ENEMY_BULLET_WIDTH = 21
ENEMY_BULLET_HEIGHT = 15

BOSS_WIDTH = 150
BOSS_HEIGHT = 150
BOSS_VEL_X = 15
BOSS_VEL_Y = 5
BOSS_BULLET_WIDTH = 20
BOSS_BULLET_HEIGHT = 30
BOSS_BULLET_VEL = 10
BOSS_BULLET_VEL = 10

boss_bullets = []

boss_bullet_cooldown = 0
boss_bullet_cooldown_time = 2000.0  # Adjust this value as needed

green_bullet_image = pygame.image.load("green_bullet.png").convert_alpha()
enemy_bullet_image = pygame.image.load("bullets.png").convert_alpha()
boss_surface = pygame.transform.scale(pygame.image.load("boss_baustin.png"), (BOSS_WIDTH, BOSS_HEIGHT))

BULLET_VEL = 17

FONT = pygame.font.SysFont("Lucida Console Bold", 45)
LOSE_FONT = pygame.font.SysFont("Lucida Console Bold", 110)
LEADERBOARD_FONT = pygame.font.SysFont("Lucida Console Bold", 30)
LEADERBOARD_FONT_COLOR = (75, 0, 130)  # dark purple
LABEL_FONT = pygame.font.SysFont("Lucida Console Bold", 50)
HEADERS_FONT = pygame.font.SysFont("Lucida Console Bold", 55)
HEADERS_FONT_COLOR = (0, 255, 191)  # turquoise
BUTTON_FONT = pygame.font.SysFont("Impact", 27)
BUTTON_FONT_COLOR = (0, 0, 0)

player_rect = pygame.Rect(WIDTH / 2 - PLAYER_WIDTH / 2, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
boss_rect = pygame.Rect(WIDTH / 2 - BOSS_WIDTH / 2, 50, BOSS_WIDTH, BOSS_HEIGHT)  # Add this line to initialize boss_rect

player_health = 10000
max_player_health = 10000

boss_health = 10,000
max_boss_health = 10,000

moving_right = False

def draw_health_bar():
    # Draw the health bar on the screen - BOSS
    health_bar_width = int((boss_health / max_boss_health) * BOSS_WIDTH)
    pygame.draw.rect(WIN, (255, 0, 0), (20, 60, BOSS_WIDTH, 10))
    pygame.draw.rect(WIN, (0, 255, 0), (20, 60, health_bar_width, 10))
    
def draw_player_health_bar():
    health_bar_width = int((player_health / max_player_health) * PLAYER_WIDTH)
    health_bar_height = 20
    health_bar_x = WIDTH - health_bar_width - 20
    health_bar_y = 20
    pygame.draw.rect(WIN, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(WIN, (0, 255, 0), (health_bar_x, health_bar_y, int(player_health / max_player_health * health_bar_width), health_bar_height))

    health_text = FONT.render(f"Health: {player_health}/{max_player_health}", 1, (255, 255, 255))
    WIN.blit(health_text, (health_bar_x, health_bar_y - 30))

def draw(player_rect, elapsed_time, bullets, score, lives, hit):
    WIN.blit(BG, (0, 0))

    time_text = LABEL_FONT.render(f"TIME: {round(elapsed_time)}s", 1, "yellow")
    score_text = FONT.render(f"Score: {score:,}", 1, "lime")
    lives_text = FONT.render(f"LIVES: {lives}", 1, "red")

    WIN.blit(time_text, (30, 30))

    if score < 0:
        score_text = LABEL_FONT.render(f"SCORE | {score:,}", 1, "red")
        WIN.blit(score_text, (30, 90))
    else:
        score_text = LABEL_FONT.render(f"SCORE | {score:,}", 1, "green")
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
            
        draw_player_health_bar()  # Call the draw_player_health_bar() function here
            
            

    pygame.display.update()


def display_high_scores(scores, new_score=None):
    print(f"Displaying high scores: scores={scores}, new_score={new_score}")
    high_scores = load_scores()
    WIN.blit(BG, (0, 0))

    high_scores_text = HEADERS_FONT.render("HIGH SCORES", 1, HEADERS_FONT_COLOR)
    WIN.blit(high_scores_text, (615, 215))

    y_position = 150
    for i, (score, name) in enumerate(scores[:20], start=1):
        leaderboard_text = f"{i}. | {name}: "
        leaderboard_text_rendered = LEADERBOARD_FONT.render(leaderboard_text, 1, (255, 255, 255))
        WIN.blit(leaderboard_text_rendered, (615, y_position + 115))

        score_text = LEADERBOARD_FONT.render(f"{score:,}", 1, (0, 255, 191))
        WIN.blit(score_text, (615 + leaderboard_text_rendered.get_width(), y_position + 115))

        y_position += 30

    if new_score < 0:
        new_score_text = LABEL_FONT.render(f"SCORE | {new_score:,}", 1, "red")
        WIN.blit(new_score_text, (310, 145))
    else:
        new_score_text = LABEL_FONT.render(f"SCORE | {new_score:,}", 1, "green")
        WIN.blit(new_score_text, (310, 145))

    # Draw the "Play Again" button
    pygame.draw.rect(WIN, (0, 255, 0), (690, 135, 130, 60))
    play_again_text = BUTTON_FONT.render("Play Again", 1, BUTTON_FONT_COLOR)
    WIN.blit(play_again_text, (707, 155))

    game_over_text = pygame.image.load("gameover.png").convert_alpha()
    WIN.blit(game_over_text, (525, 35))

    while True:
        entering_name = True  # Define the entering_name variable before the while loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if the mouse click is within the "Play Again" button area
                    if 600 < event.pos[0] < 900 and 600 < event.pos[1] < 700:
                        return True  # Restart the game

        pygame.time.delay(50)
        pygame.display.update()


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

boss_alpha = 255  # Add this line to initialize the boss_alpha variable
boss_alpha_decrease_rate = 255 / (2 * 60)  # Add this line to set the decrease rate

def draw_boss():
    global boss_alpha  # Add this line to access the boss_alpha variable
    boss_surface.set_alpha(int(boss_alpha))  # Set the alpha value of the boss surface (convert to int)
    WIN.blit(boss_surface, (boss_rect.x, boss_rect.y))
    health_text = FONT.render(f"Boss Health: {boss_health}/{max_boss_health}", 1, (255, 255, 255))
    WIN.blit(health_text, (20, 60))
    pygame.display.update()
    
def boss_hit():
    global boss_health, boss_alpha, boss_disappear_frames  # Add boss_alpha to the global variables
    boss_health -= 1.5  # Adjust the damage value as needed
    if boss_health <= 0:
        boss_health = 0
        if boss_disappear_frames > 0:  # Check if boss is defeated and there are frames remaining
            boss_alpha -= boss_alpha_decrease_rate
            boss_disappear_frames -= 1

            if boss_alpha < 0:
                boss_alpha = 0

            if boss_alpha == 0:
                boss_fight = False  # Boss defeated, end the fight


def main():
    global keys, player_rect, moving_right, boss_health, player_health
    clock = pygame.time.Clock()
    entering_name = False
    boss_fight = False
    player_bullets = []
    boss_bullets = []
    global boss_disappear_frames 
    boss_disappear_frames = 2 * 260

    def boss_movement():
        global boss_rect, BOSS_VEL_X, BOSS_VEL_Y, WIDTH, HEIGHT

        boss_rect.x += BOSS_VEL_X
        boss_rect.y += BOSS_VEL_Y
        
        if boss_rect.left < 0 or boss_rect.right > WIDTH:
            BOSS_VEL_X = -BOSS_VEL_X

        if boss_rect.y <= 0 or boss_rect.y + BOSS_HEIGHT >= HEIGHT:
            BOSS_VEL_Y = -BOSS_VEL_Y

    def boss_shoot():
        global boss_bullets, boss_bullet_cooldown, boss_bullet_cooldown_time, boss_rect

        if boss_bullet_cooldown <= 0:
            bullet_x = boss_rect.x + BOSS_WIDTH // 2 - BOSS_BULLET_WIDTH // 2
            bullet_y = boss_rect.y + BOSS_HEIGHT
            boss_bullets.append((pygame.Rect(bullet_x, bullet_y, BOSS_BULLET_WIDTH, BOSS_BULLET_HEIGHT), True))
            boss_bullet_cooldown = boss_bullet_cooldown_time

        if boss_bullet_cooldown > 0:
            boss_bullet_cooldown -= clock.get_rawtime()


    def boss_hit():
        global boss_health
        boss_health -= 1.5  # Adjust the damage value as needed
        if boss_health <= 0:
            boss_health = 0
            boss_fight = False  # Boss defeated, end the fight

    # Inside the boss fight loop
    if boss_fight:  
        boss_movement()   
        boss_shoot()
        boss_hit()

    # Check for collisions between player's bullets and boss
    for index, player_bullet_info in enumerate(player_bullets[:]):
        player_bullet, _ = player_bullet_info  # Add this line to unpack the values
        player_bullet_rect = pygame.Rect(player_bullet.x, player_bullet.y, player_bullet.width, player_bullet.height)  # Update this line

        if boss_rect.colliderect(player_bullet_rect):  # Update this line
            # Boss takes damage
            print("Boss hit!")
            boss_hit()  # Decrease boss's health
            player_bullets.pop(index)  # Remove the bullet

    for index, bullet_info in enumerate(boss_bullets[:]):
        bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
        bullet.y += BOSS_BULLET_VEL

        if player_rect.colliderect(bullet) and is_enemy_bullet:
            print("I'm Hit!")
            hit = True
            lives -= 1
            boss_bullets.pop(index)

   
    while True:  # Run the game loop indefinitely
        run = True
        start_time = time.time()
        elapsed_time = 0
        score = 0
        lives = 3
        bullet_add_increment = 1000
        bullet_count = 0
        initial_delay = 1500

        bullets = []
        player_bullets = []
        boss_bullets = []
        player_bullet_cooldown = 0
        player_bullet_cooldown_time = 20.0
        hit = False
        boss_fight = False
        high_scores = load_scores()

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
                for _ in range(7):
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
                    score -= 180

                if player_rect.colliderect(bullet) and is_enemy_bullet:
                    print("I'm Hit!")
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
                        score += 115

            bullets = [bullet_info for index, bullet_info in enumerate(bullets) if index not in bullets_to_remove]
            player_bullets = [player_bullet_info for player_bullet_info in player_bullets if
                              player_bullet_info not in player_bullets_to_remove]

            # Boss Fight Logic
            if score >= 1500:
                boss_fight = True
                
            if boss_fight:
                boss_movement()
                boss_shoot()

                
                # Check for collisions between player's bullets and boss
                for player_bullet_info in player_bullets[:]:
                    player_bullet, _ = player_bullet_info
                    if boss_rect.colliderect(player_bullet):
                        # Boss takes damage
                        print("Boss hit!")
                        boss_hit()  # Decrease boss's health
                        player_bullets.remove(player_bullet_info)  # Remove the bullet info tuple
                     

                for index, bullet_info in enumerate(boss_bullets[:]):
                    bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
                    bullet.y += BOSS_BULLET_VEL

                    if player_rect.colliderect(bullet) and is_enemy_bullet:
                        print("I'm Hit!")
                        hit = True
                        lives -= 1
                        boss_bullets.pop(index)

                draw_boss()

            draw(player_rect, elapsed_time, bullets + player_bullets + boss_bullets, score, lives, hit)

            if lives <= 0:
                run = display_high_scores(high_scores, score)
                if not run:
                    pygame.quit()
                    sys.exit()
                entering_name = False  # Set entering_name to True to restart the name input loop
                player_name = ""
                
                while run and entering_name:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                entering_name = False
                            elif event.key == pygame.K_BACKSPACE:
                                player_name = player_name[:-1]
                            else:
                                player_name += event.unicode

                    pygame.display.update()
                    clock.tick(30)

                    name_input_text = LABEL_FONT.render(f"NAME | {player_name}", 1, "grey")
                    WIN.blit(name_input_text, (375, 145))

                    pygame.display.update()
                    clock.tick(30)

                high_scores.append((score, player_name))
                high_scores.sort(reverse=True)
                save_scores(high_scores)

                pygame.time.delay(2000)

                save_scores(high_scores)
        else:
            run = True
            pygame.display.update()


if __name__ == "__main__":
    main()