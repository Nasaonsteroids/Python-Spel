import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1800, 1000
PLAYER_SIZE = 40
ENEMY_SIZE = 60
PERK_SIZE = 40
PLAYER_SPEED = 6
ENEMY_SPEED = 2
BULLET_SIZE = 5

# Färger
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Spel fönster
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Game")

# Font rendering
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(WHITE)
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

    def move(self, keys):
        if keys[pygame.K_w] and self.y - PLAYER_SPEED > 0:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_s] and self.y + PLAYER_SIZE + PLAYER_SPEED < HEIGHT:
            self.y += PLAYER_SPEED
        if keys[pygame.K_a] and self.x - PLAYER_SPEED > 0:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_d] and self.x + PLAYER_SIZE + PLAYER_SPEED < WIDTH:
            self.x += PLAYER_SPEED


class Enemy:
    def __init__(self):
        self.sprites = [pygame.transform.scale(pygame.image.load(f"animation/go_{i}.png"), (ENEMY_SIZE, ENEMY_SIZE)) for i in range(1, 4)]
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.x = random.randint(0, WIDTH - ENEMY_SIZE)
        self.y = random.randint(0, HEIGHT - ENEMY_SIZE)
        self.speed_multiplier = 1

    def animate(self):
        self.current_sprite += 0.1  # Adjust the speed of animation
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def move_towards_player(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx = dx / distance
            dy = dy / distance
        self.x += dx * ENEMY_SPEED * self.speed_multiplier
        self.y += dy * ENEMY_SPEED * self.speed_multiplier

class Perk:
    def __init__(self):
        self.image = pygame.image.load("images/freeze.png")
        self.image = pygame.transform.scale(self.image, (PERK_SIZE, PERK_SIZE))
        self.active = False
        self.start_time = None
        self.spawn_time = random.randint(5000, 6000)

    def spawn(self):
        current_time = pygame.time.get_ticks()
        if not self.active and current_time >= self.spawn_time:
            self.x = random.randint(0, WIDTH - PERK_SIZE)
            self.y = random.randint(0, HEIGHT - PERK_SIZE)
            self.active = True
            self.start_time = current_time
            self.spawn_time = current_time + random.randint(5000, 6000)

    def pickup(self, player_x, player_y):
        if self.active and math.hypot(player_x - self.x, player_y - self.y) < PLAYER_SIZE / 2 + PERK_SIZE / 2:
            self.active = False
            self.start_time = pygame.time.get_ticks()
            for enemy in enemies:
                enemy.speed_multiplier = 0

    def duration(self):
        current_time = pygame.time.get_ticks()
        if self.start_time is not None and current_time - self.start_time >= 3000:
            self.start_time = None
            for enemy in enemies:
                enemy.speed_multiplier = 1

class Bullet:
    def __init__(self, x, y, direction):
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(BLUE)
        self.x = x
        self.y = y
        self.direction = direction

    def move(self):
        self.x += self.direction[0] * 10  # ändra hastiget på skotten
        self.y += self.direction[1] * 10  # ändra hasigheten på skotten

background = pygame.image.load("images/backgroundriver.png")

# Spel Objekt
player = Player()
enemies = [Enemy() for _ in range(3)]
perk = Perk()
bullets = []

# Variabel för att se senaste skottets avlossnings tid
last_bullet_fired_time = 0

# Poäng och Tid
score = 0
start_time = pygame.time.get_ticks()
elapsed_time = 0  # tid spelat

def game_over_screen(elapsed_time):
    text = font.render(f"Game Over! You survived for {elapsed_time:.2f} seconds.", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

def replay_or_exit_screen():
    replay_text = font.render("Press R to replay", True, (0, 0, 0))
    exit_text = font.render("Press Q to exit", True, (0, 0, 0))
    replay_rect = replay_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
    screen.blit(replay_text, replay_rect)
    screen.blit(exit_text, exit_rect)

# Main game loop
running = True
game_over = False
spawn_enemy_count = 3  # Antalet fiender som spawnar först
enemies = [Enemy() for _ in range(spawn_enemy_count)]  # Fiendernas spawn

clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        player.move(keys)
        perk.spawn()
        perk.pickup(player.x, player.y)
        perk.duration()

        for enemy in enemies:
            enemy.move_towards_player(player.x, player.y)

        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - last_bullet_fired_time >= 100:  # 500 milliseconds
            if len(bullets) < 1000000:  # Max antal skott på skärmen
                bullet = Bullet(player.x, player.y, (0, -1))  # Ändra riktningen
                bullets.append(bullet)
                last_bullet_fired_time = current_time  # Uppdaterar senast skjutet tid

        # Kollar för bullet-enemy kollision och döda fiender
        bullets_to_remove = []
        for bullet in bullets:
            bullet.move()
            for enemy in enemies:
                if math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) < BULLET_SIZE / 2 + ENEMY_SIZE / 2:
                # Collision detected, remove enemy and bullet
                    enemies.remove(enemy)
                    bullets_to_remove.append(bullet)
                    score += 5  

        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        if len(enemies) == 0:  # Alla fiender är döda
            # Spawn nya fiender
            spawn_enemy_count += 2  # Öka mängden fiender med 2 per runda
            enemies = [Enemy() for _ in range(spawn_enemy_count)]

        if any(math.hypot(player.x - enemy.x, player.y - enemy.y) < PLAYER_SIZE / 2 + ENEMY_SIZE / 2 for enemy in enemies):
            end_time = pygame.time.get_ticks()
            elapsed_time = (end_time - start_time) / 1000.0
            game_over = True

    # Ritar  bakgrunden, spelaren, fienden, power-ups och skott
    screen.blit(background, (0, 0))
    screen.blit(player.image, (player.x, player.y))

    for enemy in enemies:
        enemy.animate()
        enemy.move_towards_player(player.x, player.y)
        screen.blit(enemy.image, (enemy.x, enemy.y))

    if perk.active:
        screen.blit(perk.image, (perk.x, perk.y))

    for bullet in bullets:
        screen.blit(bullet.image, (bullet.x, bullet.y))

    #Poäng
    font_size = 48
    font = pygame.font.Font(None, font_size)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(topright=(WIDTH - 30, 30))
    screen.blit(score_text, score_rect)

    # Hanterar game over och replay logik
    if game_over:
        game_over_screen(elapsed_time)
        replay_or_exit_screen()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Start om spelet för att köra igen
                    player = Player()
                    spawn_enemy_count = 3
                    enemies = [Enemy() for _ in range(spawn_enemy_count)]
                    perk = Perk()
                    bullets = []  
                    score = 0  
                    start_time = pygame.time.get_ticks()
                    elapsed_time = 0  
                    game_over = False
                elif event.key == pygame.K_q:
                    running = False
    else:
        pygame.display.update()
        
    clock.tick(60)
#Avlustar spelet
pygame.quit()
