import pygame
import sys
import random
import math
import os
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE

pygame.init()

win_width, win_height = 1000, 1000
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("STARBLITZ")

background_images = [pygame.image.load(f'./backgrounds/space{i}.png') for i in range(1, 13)]
landing_background = pygame.image.load('assets/starblitz_header.png')
start_button = pygame.image.load('assets/start_button.png')
exit_button = pygame.image.load('assets/exit_button.png')
health_bar_image = pygame.image.load('assets/health_bar.png').convert_alpha()
game_over_bg = pygame.image.load('assets/gameover.png')
restart_button = pygame.image.load('assets/restart_button.png')  # Adjust path as needed


player_width = 75
player_health = 100
max_player_health = 100
health_bar_height = 20

FONT = pygame.font.SysFont(None, 45)
game_over_font = pygame.font.SysFont(None, 95)
leaderboard_font = pygame.font.SysFont(None, 50)
stats_font = pygame.font.SysFont(None, 65)



char = pygame.image.load('assets/player_img1.png')
bullet_sides = pygame.image.load('assets/purple_sides.png')
bullet_middle = pygame.image.load('assets/orange_middle.png')
bullet_missile = pygame.image.load('assets/enemy_bullet_red.png')

enemy_ship = pygame.image.load('assets/enemy_ship1.png')
boss_image = pygame.image.load('assets/boss_one.png') 
boss_bullet = pygame.image.load('assets/boss_bullet.png') 




clock = pygame.time.Clock()

# Class definition for HighScores
class HighScores:
    def __init__(self):
        self.scores = []
        self.load_scores()

    def load_scores(self):
        if os.path.exists('hi_scores.txt'):
            with open('hi_scores.txt', 'r') as file:
                for line in file:
                    name, score, time_duration = line.strip().split(',')
                    self.scores.append({'name': name, 'score': int(score), 'time_duration': time_duration})

    def save_scores(self):
        with open('hi_scores.txt', 'w') as file:
            for score in self.scores:
                file.write(f"{score['name']},{score['score']},{score['time_duration']}\n")

    def add_score(self, name, score, time_duration):
        if not self.scores or score > self.scores[0]['score']:
            self.scores = [{'name': name, 'score': score, 'time_duration': time_duration}]
            self.save_scores()  # Save the new highest score

    def get_highest_score(self):
        if self.scores:
            return max(score['score'] for score in self.scores)
        else:
            return 0

    def display_scores(self):
        print("\nHIGH SCORES:")
        for idx, score in enumerate(self.scores, start=1):
            print(f"{idx}., {score['name']}- Name: {score['name']} - Score: {score['score']}, Time: {score['time_duration']}")

            
high_score_instance = HighScores()

class ScrollingBackground:
    def __init__(self, images):
        self.images = images
        self.current_index = 0
        self.scroll_speed = 1.8
        self.y = 0

    def scroll(self):
        self.y += self.scroll_speed
        if self.y >= win_height:
            self.y = 0
            self.current_index = (self.current_index + 1) % len(self.images)

    def draw(self, win):
        win.blit(self.images[self.current_index], (0, self.y))
        win.blit(self.images[(self.current_index + 1) % len(self.images)], (0, self.y - win_height))

def redraw_game_window(player, enemies, background):
    background.draw(win)
    player.draw(win)
    for enemy in enemies:
        enemy.draw(win)

    # Display the stats bar image at the top center
    stats_bar_image = pygame.image.load('assets/stats_bar.png') 
    stats_bar_rect = stats_bar_image.get_rect(center=(win_width // 2, 40))
    win.blit(stats_bar_image, stats_bar_rect)

class Bullet:
    def __init__(self, x, y, image, angle, damage):
        self.x = x
        self.y = y
        self.vel = 18
        if isinstance(image, str):
            self.image = pygame.image.load(image).convert_alpha()
        elif isinstance(image, pygame.Surface):
            self.image = image
        else:
            raise TypeError("Image must be a file path or pygame.Surface")
        self.angle = angle
        self.damage = damage

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def move(self):
        radian_angle = math.radians(self.angle)
        self.x += self.vel * math.cos(radian_angle)
        self.y += self.vel * math.sin(radian_angle)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def collide(self, target):
        bullet_rect = self.get_rect()
        target_rect = pygame.Rect(target.x, target.y, target.width, target.height)
        return bullet_rect.colliderect(target_rect)



class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 15
        self.bullets = []
        self.shooting = False
        self.shoot_counter = 0
        self.shoot_cooldown = 6
        self.score = 0
        self.total_damage_to_enemies = 0
        self.health = 100
        self.max_health = 100
        self.direction = "standing"
        self.game_over = False  # New variable to track game over state
        
        
    def draw(self, win):
        if self.direction == "left":
            char = pygame.image.load('assets/player_img_left.png')
        elif self.direction == "right":
            char = pygame.image.load('assets/player_img_right.png')
        elif self.direction == "forward":
            char = pygame.image.load('assets/player_img_forward.png')
        elif self.direction == "backward":
            char = pygame.image.load('assets/player_img_reverse.png')
        else:
            char = pygame.image.load('assets/player_img1.png')
            
        win.blit(char, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(win)
            
    def update_direction(self, keys):
        if keys[pygame.K_w] and self.y > 0:
            self.direction = "forward"
        elif keys[pygame.K_a] and self.x > 0:
            self.direction = "left"
        elif keys[pygame.K_s] and self.y < win_height - self.height:
            self.direction = "backward"
        elif keys[pygame.K_d] and self.x < win_width - self.width:
            self.direction = "right"
        else:
            self.direction = "standing"

    def shoot(self, bullet_img):
        if self.shoot_counter == 0:
            bullet1 = Bullet(self.x + .29 * self.width, self.y + 40, bullet_sides, -90, 0.7)
            bullet2 = Bullet(self.x + .45 * self.width, self.y + 58, bullet_middle, -90, 1.5)
            bullet3 = Bullet(self.x + .62 * self.width, self.y + 58, bullet_middle, -90, 1.5)
            bullet4 = Bullet(self.x + .69 * self.width, self.y + 40, bullet_sides, -90, 0.7)

            self.bullets.extend([bullet1, bullet2, bullet3, bullet4])
            self.shoot_counter = self.shoot_cooldown

    def move_bullets(self):
        for bullet in self.bullets:
            bullet.move()
            if bullet.y < 0 or bullet.x < 0 or bullet.x > win_width or bullet.y > win_height:
                self.bullets.remove(bullet)

    def cooldown(self):
        if self.shoot_counter > 0:
            self.shoot_counter -= 1

    def update_score(self, total_damage_to_enemies):
        self.score += total_damage_to_enemies
        self.total_damage_to_enemies = 0
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.display_game_over()
            self.game_over = True  # Ensuring game over is set to True
            # Ensure high score is recorded when health drops to zero
            current_time = pygame.time.get_ticks() - start_time
            minutes = current_time // 60000
            seconds = (current_time // 1000) % 60
            milliseconds = current_time % 1000
            high_score_instance.add_score("PlayerName", self.score, f"{minutes:02}:{seconds:02}:{milliseconds:03}")
            

    def display_game_over(self):
            
            # Draw the background image
            win.blit(game_over_bg, (0, 0))

            # Adjust the position and size of the restart button
            restart_button_rect = pygame.Rect(win_width // 2 - 135, win_height // 2 + 280, 320, 80)

            # Adjust the color and style of the restart button
            restart_button_color = (204, 204, 0, 80)  # Red color
            border_radius = 40  # Adjust the border radius as needed
            pygame.draw.rect(win, restart_button_color, restart_button_rect, border_radius=border_radius)

            # Render text
            font = pygame.font.Font(None, 36) 
            text_surface = font.render("Try Again?", True, (0, 0, 0))  
            text_rect = text_surface.get_rect(center=restart_button_rect.center)

            # Blit text onto the button surface
            win.blit(text_surface, text_rect)

            pygame.display.flip()


            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_button_rect.collidepoint(event.pos):
                            # Restart the whole program
                            python = sys.executable
                            os.execl(python, python, *sys.argv)


def restart_game(player):
    player.game_over = False
    player.health = 100
    player.score = 0
    player.vel = 17
    player.bullets = []
    player.shooting = False
    player.shoot_counter = 0
    player.shoot_cooldown = 4
    player.score = 0
    player.total_damage_to_enemies = 0
    player.health = 100
    player.max_health = 100
    player.direction = "standing"

    # Add the player's score to the high scores only when health reaches 0
    if player.health <= 0:
        current_time = pygame.time.get_ticks() - start_time
        minutes = current_time // 60000
        seconds = (current_time // 1000) % 60
        milliseconds = current_time % 1000
        high_score_instance.add_score(player_name, player.score, f"{minutes:02}:{seconds:02}:{milliseconds:02}")

    # Clear the input area with a solid color
    pygame.draw.rect(win, (0, 0, 0), (win_width // 2 - input_text.get_width() // 2, win_height // 4 - 50, input_text.get_width(), input_text.get_height()))

    input_text = FONT.render(player_name, True, (255, 255, 255))
    win.blit(input_text, (win_width // 2 - input_text.get_width() // 2, win_height // 4 - 20))

    clock.tick(60)
    pygame.display.update()

    # Define a starting x-coordinate for the leftmost column
    start_x = win_width // 2 - 100  # Adjust this value as needed
    start_y = 50  # Adjust this value as needed

    for idx, score in enumerate(high_score_instance.score[:1], start=1):
        score_text = leaderboard_font.render(f"{idx}. {score['name']}", True, (255, 255, 255))
        score_value_text = leaderboard_font.render(f"Score: {score['score']}", True, (255, 255, 255))
        time_value_text = leaderboard_font.render(f"Time: {score['time_duration']}", True, (255, 255, 255))
        
        # Calculate the y-coordinate for the current row
        row_y = start_y + (idx - 1) * 70  # Adjust the vertical spacing between rows
        
        win.blit(score_text, (start_x, row_y))
        win.blit(score_value_text, (start_x + 50, row_y)) 
        win.blit(time_value_text, (start_x + 300, row_y))
    


    clock.tick(60)     

    pygame.quit()
    sys.exit()
    
class HealthItem:
    def __init__(self, x, y, image):
        self.x = 0
        self.y = 0
        self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel = 2
        self.active = True

    def spawn(self):
        self.x = random.randint(50, 1000 - self.width - 50)
        self.y = random.randint(50, 1000 - self.height - 50)
        self.active = True

    def draw(self, win):
        if self.active:
            win.blit(self.image, (self.x, self.y))

    def check_collision(self, player_rect):
        return player_rect.colliderect(pygame.Rect(self.x, self.y, self.width, self.height))


class Enemy:
    def __init__(self, x, y, width, height, bullet_image, player):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 3
        self.bullets = []
        self.bullet_image = bullet_image
        self.shoot_counter = 0
        self.shoot_cooldown = 10
        self.player = player
        self.health = 25
        self.max_health = 25
        self.reverse_timer = 0
        self.reverse_delay = 800000
        self.reverse_direction = False

    def draw(self, win):
        rotated_enemy = pygame.transform.rotate(enemy_ship, 180)
        win.blit(rotated_enemy, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(win)

    def move(self):
        if not self.reverse_direction:
            if self.y < win_height:
                self.y += self.vel
            else:
                self.y = 0
                self.x = random.randint(0, win_width - 100)
                self.reverse_timer = pygame.time.get_ticks()  # Reset the timer when reappearing
        else:
            # Move in reverse after the first 5 seconds
            self.y -= self.vel
            
    def shoot(self):
        if self.shoot_counter == 0:
            angle = math.atan2(player_1.y - self.y, player_1.x - self.x)
            bullet = Bullet(self.x + self.width // 4, self.y + self.height // 3, self.bullet_image, math.degrees(angle),
                            0.1)
            self.bullets.append(bullet)
            self.shoot_counter = self.shoot_cooldown

    def update(self):
        # Check if 5 seconds have passed and set the reverse_direction flag
        current_time = pygame.time.get_ticks()
        if current_time - self.reverse_timer > self.reverse_delay:
            self.reverse_direction = True

    def move_bullets(self):
        for bullet in self.bullets:
            bullet.move()
            if bullet.y < 0 or bullet.x < 0 or bullet.x > win_width or bullet.y > win_height:
                self.bullets.remove(bullet)

    def cooldown(self):
        if self.shoot_counter > 0:
            self.shoot_counter -= 1

    def take_damage(self, damage,  game_over_bg = None):
        actual_damage = min(self.health, damage)
        self.health -= actual_damage
        if self.health <= 0:
            self.health = 0
            return True
        return False

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return True
        return False
    
class Boss:
    def __init__(self, x, y, boss_bullet, target):
        self.x = x
        self.y = y
        self.width = 115  # Set width to 125
        self.height = 115  # Set height to 125
        self.boss_image = pygame.transform.scale(pygame.image.load('assets/boss_one.png'), (self.width, self.height))
        self.vel = 5
        self.health = 250
        self.max_health = 250
        self.bullet_img = boss_bullet
        self.target = target
        self.bullet_vel = 5
        self.shoot_cooldown = 200
        self.shoot_timer = pygame.time.get_ticks()
        self.bullets = []
        self.moving_right = True

    def draw_health_bar(self, win):
        # Calculate health bar width based on current health
        health_bar_width = int((self.health / self.max_health) * self.width)
        health_bar_height = 20
        # Draw the health bar just above the boss
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y - 20, self.width, health_bar_height))
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 20, health_bar_width, health_bar_height))
        
    def move(self):
        if self.moving_right:
            self.x += self.vel
            if self.x + self.width > win_width:  # Boss reaches right edge
                self.moving_right = False
        else:
            self.x -= self.vel
            if self.x < 0:  # Boss reaches left edge
                self.moving_right = True

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.shoot_timer > self.shoot_cooldown:
            # Calculate bullet trajectory towards the player
            vel_x = (self.target.x + self.target.width / 2) - (self.x + self.width / 2)
            vel_y = (self.target.y + self.target.height / 2) - (self.y + self.height / 2)
            magnitude = math.sqrt(vel_x**2 + vel_y**2)
            if magnitude != 0:
                vel_x = (vel_x / magnitude) * self.bullet_vel
                vel_y = (vel_y / magnitude) * self.bullet_vel
            
            # Calculate angle for the bullet
            angle = math.degrees(math.atan2(vel_y, vel_x))
            
            # Create a new bullet
            new_bullet = Bullet(self.x + self.width / 2, self.y + self.height / 2, self.bullet_img, angle, self.bullet_vel)
            self.bullets.append(new_bullet)
            self.shoot_timer = current_time
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)



    def move_bullets(self):
        for bullet in list(self.bullets):  # Use list to safely remove items while iterating
            bullet.move()
            if bullet.collide(self.target):
                self.target.take_damage(bullet.damage)
                self.bullets.remove(bullet)

    def update(self):
        self.move_bullets()
        self.move()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            # Boss defeated, implement defeat logic here
            pass

    def draw(self, win):
        win.blit(self.boss_image, (self.x, self.y))
        self.draw_health_bar(win)

        
        

class EnemySpawner:
    def __init__(self, cooldown):
        self.cooldown = cooldown
        self.counter = 0
        self.boss_defeated = False

    def spawn_enemy(self):
        if self.boss_defeated:
            return False

        self.counter += 1
        if self.counter >= self.cooldown:
            self.counter = 0
            return True
        return False

    def boss_is_defeated(self):
        self.boss_defeated = True



class ExplosionAnimation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images = [pygame.image.load(f'backgrounds/Effect_BloodImpact_{i} (Custom).png') for i in range(1, 61)]
        self.current_frame = 0
        self.animation_speed = 1  # Adjust the speed of the animation
        self.loop_count = 0  # Number of loops completed

    def animate(self, win):
        if self.current_frame < len(self.images):
            win.blit(self.images[self.current_frame], (self.x, self.y))
            self.current_frame += 1
        else:
            self.current_frame = 0
            self.loop_count += 1

            # Check if two loops have been completed
            if self.loop_count == 20:
                self.current_frame = len(self.images)  # Set to a frame beyond the last frame to mark completion
    

def draw_player_health_bar(player_width):
    health_percentage = player_1.health / player_1.max_health
    health_bar_width = int(2.48 * health_percentage * player_width)
    health_bar_height = 28
    health_bar_x = 158  # Set health bar x-position to a fixed value (left side)
    health_bar_y = win_height - 946 - health_bar_height

    # Choose color based on health percentage
    if health_percentage > 0.7:
        health_color = (0, 255, 0)  # Green when health is above 70%
    elif health_percentage > 0.3:
        health_color = (255, 255, 0)  # Yellow when health is between 30% and 70%
    else:
        health_color = (255, 0, 0)  # Red when health is below 30%   

    pygame.draw.rect(win, health_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    

    # Display the rounded health text
    health_text = FONT.render(f"{round(player_1.health, 1)} / {player_1.max_health}", 1, (0, 0, 255))
    text_x = 185  # Adjust the position of the health text
    text_y = win_height - 973  # Adjust the position of the health text
    win.blit(health_text, (text_x, text_y))

    if player_1.health <= 0 and not player_1.game_over:  # Check if the player is not already in game over state
        player_1.display_game_over()
        player_1.game_over = True  # Set game over state to True

        # Add the player's score to the high scores only when health reaches 0
        current_time = pygame.time.get_ticks() - start_time
        minutes = current_time // 60000
        seconds = (current_time // 1000) % 60
        milliseconds = current_time % 1000
        high_score_instance.add_score(player_name, player_1.score, f"{minutes:02}:{seconds:02}:{milliseconds:02}")


def update_and_display_stats(player):
    # Update and display the health bar
    draw_player_health_bar(player_width)

    # Timer (Numbers) Font & Size
    small_font = pygame.font.Font(None, 45)

    # Display the timer 
    current_time = pygame.time.get_ticks() - start_time
    minutes = current_time // 60000
    seconds = (current_time // 1000) % 60
    milliseconds = current_time % 1000

    timer_text = small_font.render(f"{minutes:02}:{seconds:02}:{milliseconds:02}", True, (255, 255, 255))
    win.blit(timer_text, (win_width - 315, win_height - 973))  # Adjust the position as needed

    # Display the score 
    score_text = FONT.render(f"{player.score:,}", True, (255, 255, 255))
    win.blit(score_text, (459, 34))

    pygame.display.update()

def welcome_screen():
    global start_time
    start_button_img = pygame.image.load('assets/start_button.png')
    start_button_rect = start_button_img.get_rect(center=(win_width // 2, win_height // 1.8))

    # Load animated background images
    background_animation = [pygame.image.load(f'backgrounds/landing/{i}.png') for i in range(1, 134)]
    current_frame = 0
    animation_speed = 80  # Adjust the speed of the animation

    background_animation2 = [pygame.image.load(f'backgrounds/title_header/{i}.png') for i in range(1, 31)]
    current_frame_bg2 = 0
    loop_counter_bg2 = 0
    first_loop_completed = False  # Variable to track the first loop of background_animation2
    

    while True:
        entering_name = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):  # Check if the mouse is over the start button
                    start_time = pygame.time.get_ticks()  # Set the start time when the game starts
                    return True  # Return True to indicate that the game should start
             
        # # Display the animated background
        win.blit(background_animation[current_frame], (0, 0))

        # Check if one loop is completed for background_animation2
        if first_loop_completed:
            win.blit(background_animation2[29], (200, 350))  # Render the picture titled "30" after the first loop
        else:
            win.blit(background_animation2[current_frame_bg2], (200, 350))

        # Update the frame for animation
        current_frame = (current_frame + 1) % len(background_animation)

        # Update the frame for background_animation2
        current_frame_bg2 = (current_frame_bg2 + 1) % len(background_animation2)
        loop_counter_bg2 += 1

        # Check if one loop is completed
        if loop_counter_bg2 >= len(background_animation2):
            loop_counter_bg2 = 0  # Reset the loop counter
            first_loop_completed = True  # Set the flag to indicate the first loop is completed

        # Draw the start button
        button_rect = start_button.get_rect(center=(win_width // 2, win_height // 1.9))
        win.blit(start_button, button_rect)
        
        # button_rect = exit_button.get_rect(center=(win_width // 2, win_height // 1.85))
        # win.blit(exit_button, button_rect)
        
        pygame.display.flip()
        pygame.time.Clock().tick(30)

# Instantiate an EnemySpawner with a specific cooldown value
enemy_spawner = EnemySpawner(cooldown=150)

health_item_image = pygame.image.load('assets/health_item.png')
health_item = HealthItem(win_width / 2, win_height / 2, health_item_image)





explosion_animations = []  # List to store explosion animations

# Call the welcome_screen function before entering the main game loop
if welcome_screen():
    # Main loop
    player_1 = Player(win_width // 2 - player_width // 2, win_height - player_width - 150, 100, 100)
    background = ScrollingBackground(background_images)
    enemies = []
    enemy_spawner = EnemySpawner(cooldown=150)
    start_time = pygame.time.get_ticks()  # Set the start time when the game starts
    spawn_timer = 0
    spawn_interval = 15000  # Time in milliseconds between spawns
    
    # Initialize boss_spawned
    boss_spawned = False

    run = True
    while run:
        entering_name = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player_1.shooting = True
                    player_1.shoot(bullet_sides)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    player_1.shooting = False

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w] and player_1.y > 0:
            player_1.y -= player_1.vel
            player_1.direction = "backward"
        if keys[pygame.K_a] and player_1.x > 0:
            player_1.x -= player_1.vel
            player_1.direction = "left"
        if keys[pygame.K_s] and player_1.y < win_height - player_1.height:
            player_1.y += player_1.vel
            player_1.direction = "forward"
        if keys[pygame.K_d] and player_1.x < win_width - player_1.width:
            player_1.x += player_1.vel
            player_1.direction = "right"

        player_1.update_direction(keys)
        
        if player_1.shooting:
            player_1.shoot(bullet_sides)

        player_1.move_bullets()
        player_1.cooldown()

        background.scroll()

        # Handle enemy spawning
        if enemy_spawner.spawn_enemy() and player_1.score < 10000:  # Keep spawning regular enemies until score reaches 10,000
            enemy_x = random.randint(0, win_width - 100)
            enemy_y = 0
            new_enemy = Enemy(enemy_x, enemy_y, 100, 100, bullet_missile, player_1)
            enemies.append(new_enemy)

        # Handle boss spawning
        if player_1.score >= 10000 and not boss_spawned and not enemy_spawner.boss_defeated:
            # Calculate the boss's starting position so it appears centered
            # Calculate the initial x-coordinate to center the boss
            boss_x = win_width // 2 - 62.5  # Half of the boss width
            boss_y = 50  # Arbitrary y-coordinate for spawning

            # Create the boss instance
            boss = Boss(boss_x, boss_y, boss_bullet, player_1)
            boss_spawned = True
            
        if boss_spawned:
            boss_rect = pygame.Rect(boss.x, boss.y, boss.width, boss.height)  # Create a rectangle for the boss
            
            for bullet in list(player_1.bullets):  # Use a list copy to safely modify the bullets list
                if bullet.get_rect().colliderect(boss.get_rect()):
                    boss.take_damage(bullet.damage)  # Assume this method deducts health from the boss
                    player_1.bullets.remove(bullet)  # Remove the bullet on collision
                        
            boss.move()
            boss.shoot()
            boss.move_bullets()
            boss.draw(win)
            
            if boss.health <= 0:  # Moved the condition inside the boss_spawned block
                print("Boss defeated!")
                boss_spawned = False
                boss = None  # Cleanup the boss object
                enemy_spawner.boss_is_defeated()  # Set boss as defeated, preventing it from respawning

        for enemy in enemies:
            enemy.move()
            enemy.shoot()
            enemy.move_bullets()
            enemy.cooldown()
            
        # Move health items
        health_item.y += health_item.vel

        # Check collision
        player_rect = pygame.Rect(player_1.x, player_1.y, player_1.width, player_1.height)
        if health_item.check_collision(player_rect):
            player_1.health = min(player_1.max_health, player_1.health + 20)
            health_item.active = False  # Disable the health item after collision
        
        health_item.draw(win)
        
        enemies_to_remove = []
        bullets_to_remove = []


        destroyed_enemy_ids = set()  # Set to store the IDs of destroyed enemies
    
        
        for explosion_animation in explosion_animations:
            explosion_animation.animate(win)
            
        player_1.draw(win)
            
            
        
        # Inside the main loop
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)

            # Create a player_rect for collision detection
            player_rect = pygame.Rect(player_1.x, player_1.y, player_1.width, player_1.height)

            # Check for collision between bullets and player using colliderect
            for bullet in enemy.bullets:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.image.get_width(), bullet.image.get_height())

                if player_rect.colliderect(bullet_rect):
                    player_1.take_damage(bullet.damage)
                    bullets_to_remove.append(bullet)

            # Check for collision between player bullets and enemy using colliderect
            for bullet in player_1.bullets:
                for enemy in enemies:
                    if enemy_rect.colliderect(pygame.Rect(bullet.x, bullet.y, bullet.image.get_width(), bullet.image.get_height())):
                        actual_damage = enemy.take_damage(bullet.damage)
                        bullets_to_remove.append(bullet)
                        print(f"Enemy Health: {enemy.health}")

                        # Handle the case where the enemy health goes below 0
                        if enemy.health <= 0 and enemy not in destroyed_enemy_ids:
                            destroyed_enemy_ids.add(enemy)
                            enemies_to_remove.append(enemy)
                                
                            # Create an explosion animation at the enemy's coordinates
                            explosion_animations.append(ExplosionAnimation(enemy.x, enemy.y))
                            
        # Inside the main game loop
        explosion_animations = [explosion for explosion in explosion_animations if explosion.current_frame < len(explosion.images)]

     
        player_rect = pygame.Rect(player_1.x, player_1.y, player_1.width, player_1.height)
        if health_item.check_collision(player_rect):
            player_1.health = min(player_1.max_health, player_1.health + 20)
            health_item.x = -100  # Move it offscreen or respawn as needed


        player_1.score += 5000 * len(destroyed_enemy_ids)

        draw_player_health_bar(player_width)
        


        player_1.bullets = [bullet for bullet in player_1.bullets if bullet not in bullets_to_remove]
        enemies = [enemy for enemy in enemies if enemy not in enemies_to_remove]
        enemies = [enemy for enemy in enemies if enemy.health > 0]
        
        if not run and entering_name:
            # Display the score and time only on the game over screen
            current_time = pygame.time.get_ticks() - start_time
            minutes = current_time // 60000
            seconds = (current_time // 1000) % 60
            milliseconds = current_time % 1000
            score_time_text = FONT.render(f"Score: {player_1.score:,}    Time: {minutes:02}:{seconds:02}:{milliseconds:03}", True, (255, 255, 255))
            text_x = win_width // 2 - score_time_text.get_width() // 2
            text_y = win_height // 3
            win.blit(score_time_text, (text_x, text_y))
        
        while run and entering_name:
            entering_name = True
            player_name = ""
            
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
            
           
            clock.tick(60)
            
        
        update_and_display_stats(player_1)
        pygame.display.update()
        redraw_game_window(player_1, enemies, background)
        
pygame.quit()
sys.exit()
