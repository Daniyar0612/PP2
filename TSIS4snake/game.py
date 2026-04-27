import pygame, random
from pygame.locals import *
import config as C

class Game:
    def __init__(self, screen, clock, settings, personal_best=0):
        self.screen = screen
        self.clock = clock
        self.settings = settings       
        self.best = personal_best
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.font_big = pygame.font.SysFont("Consolas", 52, bold=True)

    def cell_rect(self, c, r):
        return pygame.Rect(c * C.CELL, C.HUD_H + r * C.CELL, C.CELL, C.CELL)

    def is_wall(self, c, r):
        return c <= 0 or c >= C.COLS-1 or r <= 0 or r >= C.ROWS-1

    def free_pos(self, occupied):
        while True:
            c = random.randint(2, C.COLS-3)
            r = random.randint(2, C.ROWS-3)
            if (c, r) not in occupied:
                return c, r

    def pick_food(self):
        return random.choices(C.FOOD_TYPES, weights=C.FOOD_WEIGHTS, k=1)[0]

    def generate_barriers(self, level, snake_head, current_obstacles):
        new_obs = set()
        num_structures = min(level // 2, 4)
        
        for _ in range(num_structures):
            start_pos = self.free_pos(current_obstacles | new_obs | {snake_head})
            style = random.choice(["hor", "ver", "l-shape"])
            length = random.randint(2, 4)
            
            temp_group = set()
            cx, cy = start_pos
            
            if style == "hor":
                for i in range(length):
                    if not self.is_wall(cx + i, cy): temp_group.add((cx + i, cy))
            elif style == "ver":
                for i in range(length):
                    if not self.is_wall(cx, cy + i): temp_group.add((cx, cy + i))
            elif style == "l-shape":
                for i in range(2):
                    if not self.is_wall(cx + i, cy): temp_group.add((cx + i, cy))
                for i in range(2):
                    if not self.is_wall(cx + 1, cy + i): temp_group.add((cx + 1, cy + i))

            safe = True
            for p in temp_group:
                dist = abs(p[0] - snake_head[0]) + abs(p[1] - snake_head[1])
                if dist < 4: safe = False; break
            
            if safe:
                new_obs.update(temp_group)
        
        return new_obs

    def draw(self, snake, foods, poison, powerup_on_field, obstacles,
             score, level, eaten, active_effect, shield_on):
        scr = self.screen
        scr.fill(C.OUTER_BG)
        pygame.draw.rect(scr, C.GAME_FIELD_BG, (0, C.HUD_H, C.W, C.H - C.HUD_H))

        for c in range(C.COLS):
            for r in range(C.ROWS):
                rect = self.cell_rect(c, r)
                if self.is_wall(c, r):
                    pygame.draw.rect(scr, C.WALL_C, rect)
                elif self.settings.get("grid", True):
                    pygame.draw.rect(scr, C.GRID_C, rect, 1)

        for (oc, or_) in obstacles:
            pygame.draw.rect(scr, C.OBSTACLE_COLOR, self.cell_rect(oc, or_))

        for (fc, fr), ftype, timer, lifetime in foods:
            val, color, lbl, _ = ftype
            rect = self.cell_rect(fc, fr)
            if timer >= lifetime * 0.3 or (timer % 4) < 2:
                pygame.draw.circle(scr, color, rect.center, C.CELL//2 - 2)
                t = self.font.render(lbl, True, (255, 255, 255))
                scr.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

        if poison:
            (pc, pr), timer, _ = poison
            rect = self.cell_rect(pc, pr)
            if timer >= C.POISON_LIFETIME * 0.3 or (timer % 4) < 2:
                pygame.draw.circle(scr, C.POISON_COLOR, rect.center, C.CELL//2 - 2)
                t = self.font.render(C.POISON_LABEL, True, (255, 255, 255))
                scr.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

        if powerup_on_field:
            (puc, pur), putype, _ = powerup_on_field
            rect = self.cell_rect(puc, pur)
            pygame.draw.rect(scr, C.PU_COLORS[putype], rect.inflate(-6, -6), border_radius=5)
            lbl = self.font.render(C.PU_LABELS[putype], True, (255, 255, 255))
            scr.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

        h_col = self.settings.get("snake_color", [0, 200, 0])
        b_col = [max(0, c-50) for c in h_col]

        for i, (sc, sr) in enumerate(snake):
            color = h_col if i == 0 else b_col
            pygame.draw.rect(scr, color, self.cell_rect(sc, sr).inflate(-2, -2))
            if i == 0 and shield_on:
                pygame.draw.rect(scr, (255, 150, 0), self.cell_rect(sc, sr).inflate(4, 4), 3)

        pygame.draw.rect(scr, C.HUD_C, (0, 0, C.W, C.HUD_H))
        scr.blit(self.font.render(f"SCORE: {score}", True, C.TEXT_C), (15, 18))
        lv = self.font.render(f"LEVEL: {level}", True, C.GOLD)
        scr.blit(lv, (C.W//2 - lv.get_width()//2, 18))
        
        if self.best > 0:
            pb = self.font.render(f"BEST: {self.best}", True, (150, 255, 150))
            scr.blit(pb, (C.W - pb.get_width() - 15, 18))

        if active_effect:
            etype, end_ms = active_effect
            rem = max(0, (end_ms - pygame.time.get_ticks()) // 1000)
            ind = self.font.render(f"{C.PU_LABELS[etype]} {rem}s", True, C.PU_COLORS[etype])
            scr.blit(ind, (15, C.HUD_H - 25))

        pygame.display.flip()

    def level_flash(self, level, snake, foods, poison, powerup, obstacles, score, eaten, effect, shield):
        self.draw(snake, foods, poison, powerup, obstacles, score, level, eaten, effect, shield)
        msg = self.font_big.render(f"LEVEL {level}", True, (255, 255, 255))
        box = pygame.Rect(C.W//2 - msg.get_width()//2 - 30, C.H//2 - 60, msg.get_width() + 60, 100)
        pygame.draw.rect(self.screen, C.HUD_C, box)
        pygame.draw.rect(self.screen, (255, 255, 255), box, 3)
        self.screen.blit(msg, (C.W//2 - msg.get_width()//2, C.H//2 - 45))
        pygame.display.flip()
        pygame.time.wait(1000)

    def run(self):
        sx, sy = C.COLS//2, C.ROWS//2
        snake = [(sx, sy), (sx-1, sy), (sx-2, sy)]
        body = set(snake)
        direction, next_dir = (1, 0), (1, 0)
        score, level, eaten, fps = 0, 1, 0, C.FPS_INIT
        ft = self.pick_food()
        foods = [(self.free_pos(body), ft, ft[3], ft[3])]
        poison, poison_cd = None, 5
        powerup_on_field = None
        pu_next_spawn = pygame.time.get_ticks() + C.PU_SPAWN_INTERVAL
        active_effect, shield_on = None, False
        obstacles = set()

        while True:
            self.clock.tick(fps)
            now = pygame.time.get_ticks()
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit(); import sys; sys.exit()
                if e.type == KEYDOWN:
                    if e.key in (K_UP, K_w) and direction != (0, 1): next_dir = (0,-1)
                    if e.key in (K_DOWN, K_s) and direction != (0,-1): next_dir = (0, 1)
                    if e.key in (K_LEFT, K_a) and direction != (1, 0): next_dir = (-1,0)
                    if e.key in (K_RIGHT, K_d) and direction != (-1,0): next_dir = (1, 0)

            direction = next_dir
            if active_effect and now > active_effect[1]:
                etype, _ = active_effect
                if etype == C.PU_SPEED: fps -= C.SPEED_BOOST_DELTA
                if etype == C.PU_SLOW:  fps += C.SLOW_DELTA
                active_effect = None

            if powerup_on_field and now - powerup_on_field[2] > C.PU_FIELD_MS: powerup_on_field = None
            if powerup_on_field is None and now >= pu_next_spawn:
                occ = body | obstacles | {f[0] for f in foods}
                pt = random.choice([C.PU_SPEED, C.PU_SLOW, C.PU_SHIELD])
                powerup_on_field = (self.free_pos(occ), pt, now)
                pu_next_spawn = now + C.PU_SPAWN_INTERVAL

            poison_cd -= 1
            if poison is None and poison_cd <= 0:
                if random.random() < 0.3:
                    occ = body | obstacles | {f[0] for f in foods}
                    poison = (self.free_pos(occ), C.POISON_LIFETIME, C.POISON_LIFETIME)
                poison_cd = 10

            hx, hy = snake[0]
            dx, dy = direction
            head = (hx+dx, hy+dy)

            if self.is_wall(*head) or head in obstacles or head in body:
                if shield_on: 
                    shield_on = False
                    active_effect = None
                else: return score, level

            snake.insert(0, head)
            body.add(head)
            grew = False

            nf_list = []
            for (fc, fr), ftype, timer, life in foods:
                if head == (fc, fr):
                    score += ftype[0]; eaten += 1; grew = True
                    nf = self.pick_food()
                    occ = body | obstacles | {f[0] for f in nf_list}
                    nf_list.append((self.free_pos(occ), nf, nf[3], nf[3]))
                elif timer - 1 > 0:
                    nf_list.append(((fc, fr), ftype, timer-1, life))
                else:
                    nf = self.pick_food()
                    occ = body | obstacles | {f[0] for f in nf_list}
                    nf_list.append((self.free_pos(occ), nf, nf[3], nf[3]))
            foods = nf_list

            if poison:
                (pc, pr), pt, pl = poison
                if head == (pc, pr):
                    for _ in range(C.POISON_SHORTEN):
                        if len(snake) > 1: body.discard(snake.pop())
                    if len(snake) <= 1: return score, level
                    poison = None; grew = True
                elif pt - 1 > 0: poison = ((pc, pr), pt-1, pl)
                else: poison = None

            if powerup_on_field and head == powerup_on_field[0]:
                pt = powerup_on_field[1]; powerup_on_field = None
                if active_effect:
                    old, _ = active_effect
                    if old == C.PU_SPEED: fps -= C.SPEED_BOOST_DELTA
                    if old == C.PU_SLOW:  fps += C.SLOW_DELTA
                if pt == C.PU_SPEED: fps += C.SPEED_BOOST_DELTA
                elif pt == C.PU_SLOW: fps -= C.SLOW_DELTA
                elif pt == C.PU_SHIELD: shield_on = True
                active_effect = (pt, now + C.PU_EFFECT_MS)

            if not grew: body.discard(snake.pop())
            if eaten >= 3:
                eaten = 0; level += 1; fps += 0.5
                if level >= 2:
                    new_barriers = self.generate_barriers(level, snake[0], body | obstacles | {f[0] for f in foods})
                    obstacles.update(new_barriers)
                self.level_flash(level, snake, foods, poison, powerup_on_field, obstacles, score, eaten, active_effect, shield_on)
            self.draw(snake, foods, poison, powerup_on_field, obstacles, score, level, eaten, active_effect, shield_on)