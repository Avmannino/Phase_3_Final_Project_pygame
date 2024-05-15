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
victory_bg = pygame.image.load('assets/victory_bg.png')
restart_button = pygame.image.load('assets/restart_button.png')  # Adjust path as needed

player_width = 75
player_health = 100
max_player_health = 100
health_bar_height = 20

FONT = pygame.font.SysFont(None, 45)
game_over_font = pygame.font.SysFont(None, 95)
leaderboard_font = pygame.font.SysFont(None, 50)
stats_font = pygame.font.SysFont(None, 65)

# Specify the path to your font file and load the custom font
font_path = "fonts/Incompleeta.ttf"
font_size = 24
custom_font = pygame.font.Font(font_path, font_size)

char = pygame.image.load('assets/player_img1.png')
bullet_sides = pygame.image.load('assets/purple_sides.png')
bullet_middle = pygame.image.load('assets/orange_middle.png')
bullet_missile = pygame.image.load('assets/enemy_bullet_red.png')

enemy_ship = pygame.image.load('assets/enemy_ship1.png')
boss_image = pygame.image.load('assets/boss_one.png') 
boss_bullet = pygame.image.load('assets/boss_bullet.png') 

clock = pygame.time.Clock()

class ScrollingBackground:
    def __init__(self, images):
        self.images = images
        self.current_index = 0
        self.scroll_speed = 2
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
            bullet1 = Bullet(self.x + .29 * self.width, self.y + 40, bullet_sides, -90, 1.75)
            bullet2 = Bullet(self.x + .45 * self.width, self.y + 58, bullet_middle, -90, 1.5)
            bullet3 = Bullet(self.x + .62 * self.width, self.y + 58, bullet_middle, -90, 1.5)
            bullet4 = Bullet(self.x + .69 * self.width, self.y + 40, bullet_sides, -90, 1.75)

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

    def display_game_over(self):
        
            win.blit(game_over_bg, (0, 0))

            # Adjust the position and size of the restart button
            restart_button_rect = pygame.Rect(win_width // 2 - 135, win_height // 2 + 280, 320, 80)
            
            restart_button_color = (204, 204, 0, 80)  
            border_radius = 40  
            pygame.draw.rect(win, restart_button_color, restart_button_rect, border_radius=border_radius)

            font = pygame.font.Font(None, 36) 
            text_surface = font.render("Try Again?", True, (0, 0, 0))  
            text_rect = text_surface.get_rect(center=restart_button_rect.center)

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

    clock.tick(60)
    pygame.display.update()   

    pygame.quit()
    sys.exit()
    
def display_victory_screen(final_score, final_time):
    win.blit(victory_bg, (0, 0))  # Assuming you have a victory background image
    
    # Display the final score
    score_font = pygame.font.SysFont(None, 75)
    score_text = custom_font.render(f"Final Score: {final_score:,}", True, (255, 255, 0))
    score_rect = score_text.get_rect(center=(win_width // 2, win_height // 2 - 370))
    win.blit(score_text, score_rect)
    
    # Display the final time
    time_font = pygame.font.Font(None, 75)
    time_text = custom_font.render(f"Final Time: {final_time}", True, (255, 255, 0))
    time_rect = time_text.get_rect(center=(win_width // 2, win_height // 2 - 300))
    win.blit(time_text, time_rect)
    
    # Adjust the position and size of the restart button
    restart_button_rect = pygame.Rect(win_width // 2 - 135, win_height // 2 + 280, 320, 80)
    restart_button_color = (204, 204, 0, 80)
    border_radius = 40
    pygame.draw.rect(win, restart_button_color, restart_button_rect, border_radius=border_radius)

    font = pygame.font.Font(None, 36)
    text_surface = custom_font.render("Play Again?", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=restart_button_rect.center)

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


    
class HealthItem:
    def __init__(self, x, y, image):
        self.x = x  # Initial x position
        self.y = y  # Initial y position
        self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel = 3
        self.active = False  # Start as inactive and activate on spawn

    def spawn(self):
        # Randomly place the health item within the bounds, considering its size
        self.x = random.randint(50, win_width - self.width - 50)
        self.y = random.randint(50, win_height - self.height - 50)
        self.active = True  # Activate the health item

    def draw(self, win):
        if self.active:  # Only draw if active
            win.blit(self.image, (self.x, self.y))

    def check_collision(self, player_rect):
        # Only check for collision if the item is active
        if self.active and player_rect.colliderect(pygame.Rect(self.x, self.y, self.width, self.height)):
            self.active = False  # Deactivate after collision
            return True
        return False


class Enemy:
    def __init__(self, x, y, width, height, bullet_image, player):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 3.5
        self.bullets = []
        self.bullet_image = bullet_image
        self.shoot_counter = 0
        self.shoot_cooldown = 10
        self.player = player
        self.health = 30
        self.max_health = 30
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
                self.reverse_timer = pygame.time.get_ticks() 
        else:
            self.y -= self.vel
            
    def shoot(self):
        if self.shoot_counter == 0:
            angle = math.atan2(player_1.y - self.y, player_1.x - self.x)
            bullet = Bullet(self.x + self.width // 4, self.y + self.height // 3, self.bullet_image, math.degrees(angle),
                            0.1)
            self.bullets.append(bullet)
            self.shoot_counter = self.shoot_cooldown

    def update(self):
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
        self.width = 115  
        self.height = 115  
        self.boss_image = pygame.transform.scale(pygame.image.load('assets/boss_one.png'), (self.width, self.height))
        self.vel = 4.5
        self.health = 300
        self.max_health = 300
        self.bullet_img = boss_bullet
        self.target = target
        self.bullet_vel = 4
        self.shoot_cooldown = 1000  
        self.shoot_timer = pygame.time.get_ticks()
        self.bullets = []
        self.moving_right = True
        self.font = pygame.font.SysFont(None, 25)  # Initialize font for health text
        self.explosion_animations = []  # List to store explosion animations


    def draw_health_bar(self, win):
        health_bar_width = int((self.health / self.max_health) * self.width)
        health_bar_height = 20
        
        # Draw the health bar just above the boss
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y - 20, self.width, health_bar_height))
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y - 20, health_bar_width, health_bar_height))
        health_text = self.font.render(f"{int(self.health)}/{int(self.max_health)}", True, (0, 0, 0))
        health_text_rect = health_text.get_rect(center=(self.x + self.width // 2, self.y - 10))
        
        # Draw the health text
        win.blit(health_text, health_text_rect)
        
    def move(self):
        if self.moving_right:
            self.x += self.vel
            if self.x + self.width > win_width: 
                self.moving_right = False
        else:
            self.x -= self.vel
            if self.x < 0:
                self.moving_right = True

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.shoot_timer > self.shoot_cooldown:
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            new_bullet = Bullet(self.x + self.width // 2, self.y + self.height, self.bullet_img, math.degrees(angle), 10)
            self.bullets.append(new_bullet)
            self.shoot_timer = current_time
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move_bullets(self):
        for bullet in list(self.bullets):  
            bullet.move()
            if bullet.collide(self.target):
                self.target.take_damage(bullet.damage)
                self.bullets.remove(bullet)
            elif bullet.y < 0 or bullet.x < 0 or bullet.x > win_width or bullet.y > win_height:
                self.bullets.remove(bullet)

    def update(self):
        self.move_bullets()
        self.move()
        self.shoot()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.explosion_animations.append(ExplosionAnimation(self.x, self.y))
            return True  # Boss is defeated
        return False

    def draw(self, win):
        win.blit(self.boss_image, (self.x, self.y))
        self.draw_health_bar(win)
        for bullet in self.bullets:
            bullet.draw(win)
        for explosion in self.explosion_animations:
            explosion.animate(win)

class EnemySpawner:
    def __init__(self, cooldown):
        self.cooldown = cooldown
        self.counter = 0
        self.boss_active = False  

    def spawn_enemy(self):
        if self.boss_active:
            return False 
        self.counter += 1
        if self.counter >= self.cooldown:
            self.counter = 0
            return True
        return False

    def set_boss_active(self, is_active):
        self.boss_active = is_active  

class ExplosionAnimation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.images = [pygame.image.load(f'backgrounds/Effect_BloodImpact_{i} (Custom).png') for i in range(1, 61)]
        self.current_frame = 0
        self.animation_speed = 1 
        self.loop_count = 0  

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

    # Color based on health percentage
    if health_percentage > 0.7:
        health_color = (0, 255, 0)  # Green when health is above 70%
    elif health_percentage > 0.3:
        health_color = (255, 255, 0)  # Yellow when health is between 30% and 70%
    else:
        health_color = (255, 0, 0)  # Red when health is below 30%   

    pygame.draw.rect(win, health_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    
    # Display the rounded health text
    health_text = FONT.render(f"{round(player_1.health, 1)} / {player_1.max_health}", 1, (0, 0, 255))
    text_x = 185  
    text_y = win_height - 973  
    win.blit(health_text, (text_x, text_y))

    if player_1.health <= 0 and not player_1.game_over:  # Check if the player is not already in game over state
        player_1.display_game_over()
        player_1.game_over = True  # Set game over state to True

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
    animation_speed = 80  

    background_animation2 = [pygame.image.load(f'backgrounds/title_header/{i}.png') for i in range(1, 31)]
    current_frame_bg2 = 0
    loop_counter_bg2 = 0
    first_loop_completed = False  
    
    while True:
        entering_name = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):  
                    start_time = pygame.time.get_ticks()  
                    return True 
             
        win.blit(background_animation[current_frame], (0, 0))

        if first_loop_completed:
            win.blit(background_animation2[29], (200, 350))  
        else:
            win.blit(background_animation2[current_frame_bg2], (200, 350))

     
        current_frame = (current_frame + 1) % len(background_animation)

     
        current_frame_bg2 = (current_frame_bg2 + 1) % len(background_animation2)
        loop_counter_bg2 += 1


        if loop_counter_bg2 >= len(background_animation2):
            loop_counter_bg2 = 0  
            first_loop_completed = True  

     
        button_rect = start_button.get_rect(center=(win_width // 2, win_height // 1.9))
        win.blit(start_button, button_rect)
        
        # Add the text for controls
        controls_text = custom_font.render("CONTROLS:", True, (255, 255, 0))
        controls_text_rect = controls_text.get_rect(center=(win_width // 2, win_height // 1.6))
        win.blit(controls_text, controls_text_rect)
        
        controls_text = custom_font.render("MOVE: WASD", True, (255, 255, 0))
        controls_text_rect = controls_text.get_rect(center=(win_width // 2, win_height // 1.5))
        win.blit(controls_text, controls_text_rect)
        
        controls_text = custom_font.render("SHOOT: LEFT CLICK", True, (255, 255, 0))
        controls_text_rect = controls_text.get_rect(center=(win_width // 2, win_height // 1.4))
        win.blit(controls_text, controls_text_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

# Instantiate an EnemySpawner with a cooldown value
enemy_spawner = EnemySpawner(cooldown=150)

health_item_image = pygame.image.load('assets/health_item.png')
health_item = HealthItem(win_width / 2, win_height / 2, health_item_image)

explosion_animations = [] 

# Main game loop
if welcome_screen():
    player_1 = Player(win_width // 2 - player_width // 2, win_height - player_width - 150, 100, 100)
    background = ScrollingBackground(background_images)
    enemies = []
    enemy_spawner = EnemySpawner(cooldown=80)
    start_time = pygame.time.get_ticks()
    spawn_timer = 0
    spawn_interval = 3000
    health_item_spawn_timer = 0
    health_item_spawn_interval = 15000

    boss_spawned = False
    boss_defeated_time = None
    clock = pygame.time.Clock()
    fps = 60
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
        if enemy_spawner.spawn_enemy():
            enemy_x = random.randint(0, win_width - 100)
            enemy_y = 0
            new_enemy = Enemy(enemy_x, enemy_y, 100, 100, bullet_missile, player_1)
            enemies.append(new_enemy)

        current_time = pygame.time.get_ticks()

        # Draw and check collision if the health item is active
        current_time = pygame.time.get_ticks()

        # Handle HealthItem spawning
        if not health_item.active and current_time - health_item_spawn_timer > health_item_spawn_interval:
            health_item.spawn()
            health_item_spawn_timer = current_time  # Reset the timer after spawning

        if health_item.active:
            health_item.draw(win)
            player_rect = pygame.Rect(player_1.x, player_1.y, player_1.width, player_1.height)
            if health_item.check_collision(player_rect):
                player_1.health = min(player_1.max_health, player_1.health + 20)  # Increase health

        # Handle boss spawning
        if player_1.score >= 100000 and not boss_spawned and not enemy_spawner.boss_active:
            boss_x = win_width // 2 - 62.5  # Half of the boss width
            boss_y = 250  # Starting y-coordinate for the boss
            boss = Boss(boss_x, boss_y, boss_bullet, player_1)
            boss_spawned = True
            enemy_spawner.set_boss_active(True)  # Mark the boss as active

        # Boss logic
        if boss_spawned:
            boss.update()
            boss.draw(win)

            for bullet in list(boss.bullets):  # Iterate over the boss's bullets
                bullet.move()
                if bullet.collide(player_1):
                    player_1.take_damage(bullet.damage)
                    boss.bullets.remove(bullet)
                elif bullet.y < 0 or bullet.x < 0 or bullet.x > win_width or bullet.y > win_height:
                    boss.bullets.remove(bullet)

            # Boss defeat handling
            if boss.health <= 0:
                if boss_defeated_time is None:
                    boss_defeated_time = pygame.time.get_ticks()
                    player_1.score += 50000  # Add 50,000 points to the score
                else:
                    current_time = pygame.time.get_ticks()
                    if current_time - boss_defeated_time >= 2000:  # 2 seconds delay
                        boss_spawned = False
                        enemy_spawner.set_boss_active(False)  # Mark the boss as not active
                        # Calculate final time
                        final_time = current_time - start_time
                        minutes = final_time // 60000
                        seconds = (final_time // 1000) % 60
                        milliseconds = final_time % 1000
                        formatted_time = f"{minutes:02}:{seconds:02}:{milliseconds:03}"
                        display_victory_screen(player_1.score, formatted_time)  # Call the function to display the victory screen with the final score and time
                        boss = None  # Cleanup the boss object

            for bullet in list(player_1.bullets):  # Use a list copy to safely modify the bullets list
                if bullet.get_rect().colliderect(boss.get_rect()):
                    if boss.take_damage(bullet.damage):  # Check if boss is defeated and trigger explosion
                        explosion_animations.append(ExplosionAnimation(boss.x, boss.y))
                    player_1.bullets.remove(bullet)  # Remove the bullet on collision

        for enemy in enemies:
            enemy.move()
            enemy.shoot()
            enemy.move_bullets()
            enemy.cooldown()

        # Move health items
        health_item.y += health_item.vel

        enemies_to_remove = []
        bullets_to_remove = []

        destroyed_enemy_ids = set()  # Set to store the IDs of destroyed enemies

        for explosion_animation in explosion_animations:
            explosion_animation.animate(win)

        player_1.draw(win)

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

                        if enemy.health <= 0 and enemy not in destroyed_enemy_ids:
                            destroyed_enemy_ids.add(enemy)
                            enemies_to_remove.append(enemy)

                            # Create an explosion animation at the enemy's coordinates
                            explosion_animations.append(ExplosionAnimation(enemy.x, enemy.y))

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

        update_and_display_stats(player_1)
        pygame.display.update()
        clock.tick(fps)
        redraw_game_window(player_1, enemies, background)

pygame.quit()
sys.exit()
