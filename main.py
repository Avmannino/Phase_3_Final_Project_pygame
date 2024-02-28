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

# Background Image Variable
BG = pygame.image.load("stars_bg.png")

# Player Variables
PLAYER_WIDTH = 75
PLAYER_HEIGHT = 75

# Load initial player image
PLAYER_SURFACE = pygame.transform.scale(pygame.image.load("player_img1.png"), (100, 100))
player_rect = pygame.Rect(WIDTH / 2 - PLAYER_WIDTH / 2, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

# Load right-facing player image
PLAYER_SURFACE_RIGHT = pygame.transform.scale(pygame.image.load("player_right.png"), (100, 100))

# Load left-facing player image
PLAYER_SURFACE_LEFT = pygame.transform.scale(pygame.image.load("player_left.png"), (100, 100))

PLAYER_VEL = 28
PLAYER_BULLET_WIDTH = 25  # Player bullet width
PLAYER_BULLET_HEIGHT = 20  # Player bullet height
ENEMY_BULLET_WIDTH = 21  # Enemy bullet width
ENEMY_BULLET_HEIGHT = 15  # Enemy bullet height
BULLET_VEL = 15

# Load Bullets Sprite
green_bullet_image = pygame.image.load("green_bullet.png").convert_alpha()
enemy_bullet_image = pygame.image.load("bullets.png").convert_alpha()

# Load Explosion Sprite
explosion_images = [pygame.image.load(f"explosion{i}.png").convert_alpha() for i in range(1, 6)]
explosion_frame = 0

FONT = pygame.font.SysFont("Lucida Console Bold", 45)
LOSE_FONT = pygame.font.SysFont("Lucida Console Bold", 65)

# List to store collision points
collisions = []

FRAME_DELAY = 5  # You can adjust this value to control the animation speed

def draw(player_rect, elapsed_time, bullets, score, lives, hit):
    global explosion_frame  # Ensure 'explosion_frame' is treated as a global variable
    if not hit:
        explosion_frame = 0  # Initialize explosion_frame if there is no hit

    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"TIME: {round(elapsed_time)}s", 1, "yellow")
    score_text = FONT.render(f"Score: {score:,}", 1, "lime")
    lives_text = FONT.render(f"LIVES: {lives}", 1, "red")

    WIN.blit(time_text, (30, 30))
    WIN.blit(score_text, (30, 90))
    WIN.blit(lives_text, (30, 150))

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

    for collision_point in collisions:
        x, y = collision_point
        if hit and explosion_frame < len(explosion_images) and pygame.time.get_ticks() % FRAME_DELAY == 0:
            WIN.blit(explosion_images[explosion_frame], (x, y))
            explosion_frame += 1
        else:
            explosion_frame = 0
            hit = False  # Reset the hit flag after the animation completes

    pygame.display.update()

# Function to display high scores
def display_high_scores(scores, new_score=None):
    print(f"Displaying high scores: scores={scores}, new_score={new_score}")
    high_scores = load_scores()  # Load high scores from file
    WIN.blit(BG, (0, 0))  # Display background to clear the screen
    high_scores_text = LOSE_FONT.render("HIGH SCORES", 1, "Gold")
    WIN.blit(high_scores_text, (550, 250))

    y_position = 350
    for i, (score, name) in enumerate(scores, start=1):
        score_text = LOSE_FONT.render(f"{i}. {name}: {score:,}", 1, "white")
        WIN.blit(score_text, (550, y_position))
        y_position += 70

    if new_score is not None:
        # Display the player's new score
        new_score_text = LOSE_FONT.render(f"Your Score: {new_score:,}", 1, "white")
        WIN.blit(new_score_text, (550, y_position + 70))

    pygame.display.update()  # <-- Add this line
    pygame.time.delay(2000)  # Display for 2 seconds

def save_scores(high_scores):
    print("Saving scores:", high_scores)
    with open('high_scores.pkl', 'wb') as file:
        pickle.dump(high_scores, file)

def load_scores():
    try:
        with open('high_scores.pkl', 'rb') as file:
            high_scores = pickle.load(file)
    except FileNotFoundError:
        high_scores = []  # File not found, initialize with an empty list

    return high_scores

# Main Game Loop
def main():
    global keys  # Declare keys as global
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
    firing = False

    player_bullet_cooldown = 0
    player_bullet_cooldown_time = 20.0
    high_scores = load_scores()  # Load high scores from file

    explosion_frame = 0  # Initialize explosion_frame at the beginning

    while run:
        bullet_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEMOTION:
                # Move the player based on mouse movement
                player_rect.x, player_rect.y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    firing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    firing = False

                    bullet_x = player_rect.x + PLAYER_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2
                    bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT
                    player_bullets.append((pygame.Rect(bullet_x, bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT), False))
                    diagonal_bullet_x = player_rect.x + PLAYER_WIDTH // 6 - PLAYER_BULLET_WIDTH // 6 - int(
                        BULLET_VEL * round(math.cos(math.pi / 8)))
                    diagonal_bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT - int(BULLET_VEL * round(math.sin(math.pi / 8)))
                    player_bullets.append(
                        (pygame.Rect(diagonal_bullet_x, diagonal_bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT), False))
                    player_bullet_cooldown = player_bullet_cooldown_time

        firing = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]  # Using SPACE key or left mouse button for continuous firing

        if firing and player_bullet_cooldown <= 0:
            bullet_x = player_rect.x + PLAYER_WIDTH // 2 - PLAYER_BULLET_WIDTH // 2
            bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT
            player_bullets.append((pygame.Rect(bullet_x, bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT), False))
            diagonal_bullet_x = player_rect.x + PLAYER_WIDTH // 6 - PLAYER_BULLET_WIDTH // 6 - int(
                BULLET_VEL * round(math.cos(math.pi / 8)))
            diagonal_bullet_y = player_rect.y - PLAYER_BULLET_HEIGHT - int(BULLET_VEL * round(math.sin(math.pi / 8)))
            player_bullets.append(
                (pygame.Rect(diagonal_bullet_x, diagonal_bullet_y, PLAYER_BULLET_WIDTH, PLAYER_BULLET_HEIGHT), False))
            player_bullet_cooldown = player_bullet_cooldown_time

        if player_bullet_cooldown > 0:
            player_bullet_cooldown -= clock.get_rawtime()

        if player_bullet_cooldown > 0:
            player_bullet_cooldown -= clock.get_rawtime()

        if bullet_count > bullet_add_increment:
            for _ in range(8):
                bullet_x = random.randint(0, WIDTH - ENEMY_BULLET_WIDTH)
                bullet_y = -ENEMY_BULLET_HEIGHT  # Use the enemy bullet dimensions
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
                score -= 52.25

            if player_rect.colliderect(bullet) and is_enemy_bullet:
                print("I'm Hit!")
                hit = True
                lives -= 1
                bullets_to_remove.append(index)
                collisions.append((bullet.x, bullet.y))  # Store collision point

        for player_bullet_info in player_bullets[:]:
            player_bullet, _ = player_bullet_info
            player_bullet.y -= BULLET_VEL

            for index, bullet_info in enumerate(bullets[:]):
                bullet, is_enemy_bullet = bullet_info[0], bullet_info[1]
                if player_bullet.colliderect(bullet):
                    bullets_to_remove.append(index)
                    player_bullets_to_remove.append(player_bullet_info)
                    score += 105.75
                    collisions.append((bullet.x, bullet.y))  # Store collision point

        bullets = [bullet_info for index, bullet_info in enumerate(bullets) if index not in bullets_to_remove]
        player_bullets = [player_bullet_info for player_bullet_info in player_bullets if
                           player_bullet_info not in player_bullets_to_remove]

        draw(player_rect, elapsed_time, bullets + player_bullets, score, lives, hit)

        if lives <= 0:
            # Assuming you have a list of high scores (replace this with your actual high scores list)
            display_high_scores(high_scores, score)  # Display high scores
            
            save_scores(high_scores)  # Save high scores to file

            # Get player's name for the new score
            entering_name = True
            player_name = ""
            while entering_name:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:  # Enter key
                            entering_name = False
                        elif event.key == pygame.K_BACKSPACE:  # Backspace key
                            player_name = player_name[:-1]
                        else:
                            player_name += event.unicode

                # Display the name input
                name_input_text = LOSE_FONT.render(f"Enter your name: {player_name}", 1, "white")
                WIN.blit(name_input_text, (650, 400))

                pygame.display.update()
                clock.tick(30)

            # Append the player's score and name to the high scores list
            high_scores.append((score, player_name))

            # Sort the high scores in descending order
            high_scores.sort(reverse=True)

            # Display high scores
            display_high_scores(high_scores, new_score=score)
            print("Displayed high scores")

            game_over_text = LOSE_FONT.render("GAME OVER", 1, "red")
            WIN.blit(game_over_text, (550, 150))
            WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2
            pygame.display.update()
            pygame.time.delay(2000)  # Display for 2 seconds
            pygame.quit()
            sys.exit()
        else:
            run = True
            pygame.display.update()

if __name__ == "__main__":
    main()