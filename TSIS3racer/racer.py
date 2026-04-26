import pygame, random, time
from pygame.locals import *

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

def load_image(name, size=None):
    try:
        img = pygame.image.load(f"assets/{name}").convert_alpha()
    except:
        img = pygame.Surface(size if size else (50, 50))
        img.fill((255, 0, 255))
    if size:
        img = pygame.transform.scale(img, size)
    return img

class Player(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.image = load_image(f"Player_{color}.png", (52, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (200, 500)
        self.shielded = False
        self.speed_boost = 1.0

    def move(self):
        keys = pygame.key.get_pressed()
        speed = 5 * self.speed_boost
        if self.rect.left > 56 and keys[K_LEFT]:
            self.rect.move_ip(-speed, 0)
        if self.rect.right < 344 and keys[K_RIGHT]:
            self.rect.move_ip(speed, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = load_image("Enemy.png", (52, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), random.randint(-200, -50))
        self.speed = speed

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        weight = random.randint(1, 100)
        if weight > 90:
            self.value = 5
            self.image = load_image("Coin_Gold.png", (30, 30))
        elif weight > 60:
            self.value = 3
            self.image = load_image("Coin_Silver.png", (28, 28))
        else:
            self.value = 1
            self.image = load_image("Coin_Bronze.png", (24, 24))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), random.randint(-100, -20))
        self.speed = speed

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.type = random.choice(["oil", "barrier"])
        if self.type == "oil":
            self.image = load_image("Oil.png", (40, 40))
        else:
            self.image = load_image("Barrier.png", (50, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), -50)
        self.speed = speed

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.type = random.choice(["nitro", "shield", "repair"])
        self.image = load_image(f"{self.type.capitalize()}.png", (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), -50)
        self.speed = speed

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def run_game(surface, settings, player_name):
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont("Verdana", 20)
    
    diff_mult = {"Easy": 0.8, "Medium": 1.0, "Hard": 1.5}[settings["difficulty"]]
    base_speed = 5 * diff_mult
    speed = base_speed
    
    P1 = Player(settings["color"])
    
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)
    
    score = 0
    coins_collected = 0
    distance = 0.0
    
    SPAWN_ENEMY = pygame.USEREVENT + 1
    SPAWN_COIN = pygame.USEREVENT + 2
    SPAWN_OBST = pygame.USEREVENT + 3
    SPAWN_POWER = pygame.USEREVENT + 4
    
    pygame.time.set_timer(SPAWN_ENEMY, int(2000 / diff_mult))
    pygame.time.set_timer(SPAWN_COIN, 1500)
    pygame.time.set_timer(SPAWN_OBST, int(3000 / diff_mult))
    pygame.time.set_timer(SPAWN_POWER, 10000)
    
    active_powerup = None
    powerup_end_time = 0
    
    bg = load_image("AnimatedStreet.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_y1 = 0
    bg_y2 = -SCREEN_HEIGHT
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        distance += (speed * dt) * 10
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == SPAWN_ENEMY:
                e = Enemy(speed)
                if not pygame.sprite.spritecollideany(e, all_sprites):
                    enemies.add(e)
                    all_sprites.add(e)
            if event.type == SPAWN_COIN:
                c = Coin(speed)
                if not pygame.sprite.spritecollideany(c, all_sprites):
                    coins.add(c)
                    all_sprites.add(c)
            if event.type == SPAWN_OBST:
                o = Obstacle(speed)
                if not pygame.sprite.spritecollideany(o, all_sprites):
                    obstacles.add(o)
                    all_sprites.add(o)
            if event.type == SPAWN_POWER:
                p = PowerUp(speed)
                if not pygame.sprite.spritecollideany(p, all_sprites):
                    powerups.add(p)
                    all_sprites.add(p)
        
        P1.move()
        for entity in all_sprites:
            if entity != P1:
                entity.speed = speed
                entity.move()
        
        bg_y1 += speed
        bg_y2 += speed
        if bg_y1 >= SCREEN_HEIGHT:
            bg_y1 = -SCREEN_HEIGHT
        if bg_y2 >= SCREEN_HEIGHT:
            bg_y2 = -SCREEN_HEIGHT
            
        if time.time() > powerup_end_time:
            if active_powerup == "nitro":
                P1.speed_boost = 1.0
                speed = base_speed + (coins_collected * 0.1)
            active_powerup = None
        
        collected_coins = pygame.sprite.spritecollide(P1, coins, True)
        for c in collected_coins:
            coins_collected += c.value
            score += c.value * 10
            if active_powerup != "nitro":
                speed += 0.1
            
        collected_powers = pygame.sprite.spritecollide(P1, powerups, True)
        for p in collected_powers:
            active_powerup = p.type
            if p.type == "nitro":
                P1.speed_boost = 1.5
                speed *= 1.5
                powerup_end_time = time.time() + 4
            elif p.type == "shield":
                P1.shielded = True
                powerup_end_time = time.time() + 9999
            elif p.type == "repair":
                pass 
        
        hit_obstacles = pygame.sprite.spritecollide(P1, obstacles, True)
        for o in hit_obstacles:
            if active_powerup == "repair":
                active_powerup = None
            elif P1.shielded:
                P1.shielded = False
                active_powerup = None
            else:
                if o.type == "oil":
                    speed = max(base_speed, speed - 2)
                else:
                    running = False
                    
        if pygame.sprite.spritecollideany(P1, enemies):
            if active_powerup == "repair":
                pygame.sprite.spritecollide(P1, enemies, True)
                active_powerup = None
            elif P1.shielded:
                pygame.sprite.spritecollide(P1, enemies, True)
                P1.shielded = False
                active_powerup = None
            else:
                running = False
        
        surface.blit(bg, (0, bg_y1))
        surface.blit(bg, (0, bg_y2))
        
        for entity in all_sprites:
            surface.blit(entity.image, entity.rect)
            
        score_surf = font_small.render(f"Score: {int(score + distance)}", True, (0, 0, 0))
        dist_surf = font_small.render(f"Dist: {int(distance)}m", True, (0, 0, 0))
        coin_surf = font_small.render(f"Coins: {coins_collected}", True, (0, 0, 0))
        
        surface.blit(score_surf, (10, 10))
        surface.blit(dist_surf, (10, 35))
        surface.blit(coin_surf, (SCREEN_WIDTH - coin_surf.get_width() - 10, 10))
        
        if active_powerup:
            pow_surf = font_small.render(f"Power: {active_powerup.upper()}", True, (0, 255, 0))
            surface.blit(pow_surf, (10, 60))
        
        pygame.display.update()
        
    final_score = int(score + distance)
    return {"score": final_score, "distance": int(distance), "coins": coins_collected}