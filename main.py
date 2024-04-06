import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1920, 1080
PLAYER_SIZE = 40
ENEMY_SIZE = 60
PERK_SIZE = 45
PLAYER_SPEED = 4
ENEMY_SPEED = 1.5
BULLET_SIZE = 5

# Färger
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWNISHYELLOW = (155, 122, 1)

# Spel fönster
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("2D Game")

# Font rendering
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(WHITE)
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.lives = 3
        self.ammo = 12

    def move(self, keys):
        # Rörelselogik för spelaren
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
        self.is_active = False  #Ställ in på True när fienden dyker upp och blir aktiv.
        self.sprites = {
            'go': [pygame.transform.scale(pygame.image.load(f"go_{i}.png"), (ENEMY_SIZE, ENEMY_SIZE)) for i in range(1, 4)],
            'hit': [pygame.transform.scale(pygame.image.load(f"hit_{i}.png"), (ENEMY_SIZE, ENEMY_SIZE)) for i in range(1, 3)],
            'die': [pygame.transform.scale(pygame.image.load(f"die_{i}.png"), (ENEMY_SIZE, ENEMY_SIZE)) for i in range(1, 4)],
            'appear': [pygame.transform.scale(pygame.image.load(f"appear_{i}.png"), (ENEMY_SIZE, ENEMY_SIZE)) for i in range(1, 3)]
        }
        self.current_sprites = self.sprites['appear']
        self.current_sprite_index = 0
        self.image = self.current_sprites[self.current_sprite_index]
        self.x = random.randint(0, WIDTH - ENEMY_SIZE)
        self.y = random.randint(0, HEIGHT - ENEMY_SIZE)
        self.speed_multiplier = 0  # Börja stilla tills helt visas
        self.state = 'appear'  # Initialtillstånd
        self.body_hitbox = pygame.Rect(self.x, self.y, ENEMY_SIZE, ENEMY_SIZE * 0.75)
        self.head_hitbox = pygame.Rect(self.x, self.y, ENEMY_SIZE, ENEMY_SIZE * 0.25)
        self.body_hits_required = 2
        self.head_hits_required = 1

    def animate(self):
        self.current_sprite_index += 0.1
        if self.current_sprite_index >= len(self.current_sprites):
            self.current_sprite_index = 0
            if self.state == 'appear':
                self.speed_multiplier = 1  #Börja röra på dig
                self.update_animation_state('go')
            elif self.state == 'die':
                self.remove()  # Ta bort fienden när tärningsanimeringen är klar

        self.image = self.current_sprites[int(self.current_sprite_index)]

    def update_animation_state(self, state):
        self.state = state
        self.current_sprites = self.sprites[state]
        self.current_sprite_index = 0
        if state == 'appear':
            self.speed_multiplier = 0  # Sluta röra på sig tills helt visas
        elif state == 'go':
            self.speed_multiplier = 1  #Rör dig normalt
        elif state == 'die':
            self.speed_multiplier = 0  # Sluta röra på dig när du dör

    def hit(self):
        if self.state != 'hit': # Se till att vi bara utlöser detta en gång per kollision
            self.update_animation_state('hit')
            self.state = 'attack' # Ändra tillstånd till attack för att stoppa rörelsen
    def update(self):
        # Kallar den här metoden varje bildruta för att uppdatera zombies beteende
        if self.state == 'attack' and self.current_sprite_index == len(self.current_sprites) - 1:
           # Efter att ha avslutat attackanimeringen, håll dig stilla eller återgå till en annan animation
            self.state = 'go'
            self.update_animation_state('go') # Återställ till go-tillstånd eller något annat önskat tillstånd
    def remove(self):
        global enemies  #Använd en global fiendelista
        enemies.remove(self)  # Ta bort mig själv från fiendelistan


    def move_towards_player(self, player_x, player_y):
    # Flytta bara om fienden är i "gå" tillstånd.
        if self.state == 'go':
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.hypot(dx, dy)
            if distance != 0:  # Förhindra division med noll
                dx = dx / distance
                dy = dy / distance
            self.x += dx * ENEMY_SPEED * self.speed_multiplier
            self.y += dy * ENEMY_SPEED * self.speed_multiplier

        self.body_hitbox.x = self.x
        self.body_hitbox.y = self. y + ENEMY_SIZE * 0.25 #Kroppens hitbox
        self.head_hitbox.x = self.x
        self.head_hitbox.y = self.y


    def hit(self):
        self.update_animation_state('die')
    
    def adjust_for_collision(self, all_enemies):
        for other in all_enemies:
            if other != self:
                dx, dy = self.x - other.x, self.y - other.y
                distance = math.hypot(dx, dy)
                if distance < ENEMY_SIZE:  # Justera denna9 efter behov
                    # Beräkna överlappningen och tryck isär fiender
                    overlap = 0.5 * (distance - ENEMY_SIZE)
                    self.x -= overlap * (dx / distance)
                    self.y -= overlap * (dy / distance)
                    other.x += overlap * (dx / distance)
                    other.y += overlap * (dy / distance)


class Perk:
    def __init__(self):
        # Initialiserar power-up
        self.image = pygame.image.load("freeze.png")
        self.image = pygame.transform.scale(self.image, (PERK_SIZE, PERK_SIZE))
        self.active = False
        self.start_time = None
        self.spawn_time = random.randint(5000, 6000)

    def spawn(self):
        # Logik för att spawn power-up
        current_time = pygame.time.get_ticks()
        if not self.active and current_time >= self.spawn_time:
            self.x = random.randint(0, WIDTH - PERK_SIZE)
            self.y = random.randint(0, HEIGHT - PERK_SIZE)
            self.active = True
            self.start_time = current_time
            self.spawn_time = current_time + random.randint(5000, 6000)

    def pickup(self, player_x, player_y):
        # Logik för att plocka upp power-up
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

class AmmoPickup:
    def __init__(self):
        self.image = pygame.image.load("ammo.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PERK_SIZE, PERK_SIZE))
        self.x = random.randint(0, WIDTH - PERK_SIZE)
        self.y = random.randint(0, HEIGHT - PERK_SIZE)
        self.active = False
        self.next_spawn_time = pygame.time.get_ticks() + 5000
        
    def picked_up(self, player):
        if self.active and math.hypot(player.x - self.x, player.y - self.y) < PLAYER_SIZE / 2 + PERK_SIZE / 2:
            self.active = False
            self.next_spawn_time = pygame.time.get_ticks() + 5000
            player.ammo = min(12, player.ammo + 6) #Ger 6, max 12

    def respawn(self):
        if not self.active and pygame.time.get_ticks() >= self.next_spawn_time:
            self.x = random.randint(0, WIDTH - PERK_SIZE)
            self.y = random.randint(0, HEIGHT - PERK_SIZE)
            self.active = True
            print(f"Respawning ammo at: {self.x}, {self.y}")  


            
background = pygame.image.load("dalle.jpg")

# Spel Objekt
player = Player()
enemies = [Enemy() for _ in range(3)]
perk = Perk()
bullets = []
ammo_pickup = AmmoPickup()

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
        ammo_pickup.respawn()

 

        for enemy in enemies:
            enemy.update()
            enemy.move_towards_player(player.x, player.y)
            enemy.adjust_for_collision(enemies)

        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()  # Hämta den aktuella muspositionen
        if keys[pygame.K_SPACE] and current_time - last_bullet_fired_time >= 100 and player.ammo > 0:  # Kontrollera om du trycker på mellanslagstangenten
            player.ammo -= 1
            dx, dy = mouse_x - player.x, mouse_y - player.y  # Beräkna riktningsvektor
            distance = math.hypot(dx, dy)
            if distance != 0:  # Förhindra division med noll
                dx, dy = dx / distance, dy / distance  # Normalisera riktningsvektorn
            bullet = Bullet(player.x + PLAYER_SIZE / 2 - BULLET_SIZE / 2, player.y + PLAYER_SIZE / 2 - BULLET_SIZE / 2, (dx, dy))
            bullets.append(bullet)
            last_bullet_fired_time = current_time  # Uppdatera tiden då en kula senast avfyrades

        
        # Initiera bullets_to_remove innan din spelloop
        bullets_to_remove = []
        # Kollar för bullet-enemy kollision och döda fiender
        # Inuti din spelloop, för varje kula
        for bullet in bullets:
            bullet.move()  # Flytta kulan
            for enemy in enemies:
                if enemy.head_hitbox.collidepoint((bullet.x, bullet.y)):
                    enemy.head_hits_required-= 1
                    bullets_to_remove.append(bullet)
                    if enemy.head_hits_required <= 0:
                        enemies.remove(enemy)
                        score += 5
                    break  #Viktigt att förhindra att denna kula kontrolleras mot andra fiender
                elif enemy.body_hitbox.collidepoint((bullet.x, bullet.y)):
                    enemy.body_hits_required -= 1
                    bullets_to_remove.append(bullet)
                    if enemy.body_hits_required <= 0:
                        enemies.remove(enemy)
                        score += 5
                    break
        # Efter att ha kontrollerat alla kulor, ta bort de som är markerade för borttagning
        bullets = [bullet for bullet in bullets if bullet not in bullets_to_remove]


        if len(enemies) == 0:  # Alla fiender är döda
            # Spawna nya fiender
            spawn_enemy_count += 2  # Öka mängden fiender med 2 per runda
            enemies = [Enemy() for _ in range(spawn_enemy_count)]

        if any(math.hypot(player.x - enemy.x, player.y - enemy.y) < PLAYER_SIZE / 2 + ENEMY_SIZE / 2 for enemy in enemies):
            enemy.hit()
            player.lives -= 1
            enemies = [Enemy()for _ in range (spawn_enemy_count)] #Reset fiender eller hantera som önskat
            if player.lives == 0:
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
        pygame.draw.rect(screen, (255, 0, 0), enemy.head_hitbox, 2)  # Hitbox check head 
        pygame.draw.rect(screen, (0, 255, 0), enemy.body_hitbox, 2)  # Hitbox check body

    if perk.active:
        screen.blit(perk.image, (perk.x, perk.y))

    if ammo_pickup.active:
        screen.blit(ammo_pickup.image, (ammo_pickup.x, ammo_pickup.y))
        print("Ammo Pickup is active and should be visible at", ammo_pickup.x, ammo_pickup.y)

    ammo_pickup.picked_up(player)


    for bullet in bullets:
        bullet.move()
        screen.blit(bullet.image, (bullet.x, bullet.y))

    #Poäng
    font_size = 48
    font = pygame.font.Font(None, font_size)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(topright=(WIDTH - 30, 30))
    screen.blit(score_text, score_rect)

    #Liv
    lives_text = font.render(f"Lives: {player.lives}", True, (255,255,255))
    lives_rect = lives_text.get_rect(topleft=(30,30))
    screen.blit(lives_text, lives_rect)

    #Ammo
    ammo_text = font.render(f"Ammo: {player.ammo}", True, WHITE)
    ammo_rect = ammo_text.get_rect(topright=(WIDTH - 30, 60))
    screen.blit(ammo_text, ammo_rect)


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
                    player.lives = 3
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
