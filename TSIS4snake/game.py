
import pygame, random
from pygame.locals import *
import config as C


class Game:
    def __init__(self, screen, clock, settings, personal_best=0):
        self.screen       = screen
        self.clock        = clock
        self.settings     = settings       
        self.best         = personal_best

        # Fonts
        self.font     = pygame.font.SysFont("Consolas", 20)
        self.font_big = pygame.font.SysFont("Consolas", 52, bold=True)

    # Helpers

    def cell_rect(self, c, r):
        return pygame.Rect(c * C.CELL, C.HUD_H + r * C.CELL, C.CELL, C.CELL)

    def is_wall(self, c, r):
        return c == 0 or c == C.COLS-1 or r == 0 or r == C.ROWS-1

    def free_pos(self, occupied):
        """Random cell not in occupied set."""
        while True:
            c = random.randint(1, C.COLS-2)
            r = random.randint(1, C.ROWS-2)
            if (c, r) not in occupied:
                return c, r

    def pick_food(self):
        return random.choices(C.FOOD_TYPES, weights=C.FOOD_WEIGHTS, k=1)[0]


    def draw(self, snake, foods, poison, powerup_on_field, obstacles,
             score, level, eaten, active_effect, shield_on):
        scr = self.screen
        scr.fill(C.BG)

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
                pygame.draw.circle(scr, color, rect.center, C.CELL//2 - 1)
                t = self.font.render(lbl, True, (0, 0, 0))
                scr.blit(t, (rect.centerx - t.get_width()//2,
                              rect.centery - t.get_height()//2))

        # Poison food
        if poison:
            (pc, pr), timer, _ = poison
            rect = self.cell_rect(pc, pr)
            if timer >= C.POISON_LIFETIME * 0.3 or (timer % 4) < 2:
                pygame.draw.circle(scr, C.POISON_COLOR, rect.center, C.CELL//2 - 1)
                t = self.font.render("☠", True, (255, 100, 100))
                scr.blit(t, (rect.centerx - t.get_width()//2,
                              rect.centery - t.get_height()//2))

        if powerup_on_field:
            (puc, pur), putype, _ = powerup_on_field
            rect  = self.cell_rect(puc, pur)
            color = C.PU_COLORS[putype]
            pygame.draw.rect(scr, color, rect.inflate(-4, -4), border_radius=4)
            lbl = self.font.render(C.PU_LABELS[putype], True, (0, 0, 0))
            scr.blit(lbl, (rect.centerx - lbl.get_width()//2,
                            rect.centery - lbl.get_height()//2))

        # Snake
        head_color = self.settings.get("snake_color", [60, 220, 60])
        body_color = [max(0, c-60) for c in head_color]

        if shield_on:
            hr = self.cell_rect(*snake[0])
            pygame.draw.rect(scr, (255, 230, 80), hr.inflate(6, 6), 3, border_radius=6)
        for i, (sc, sr) in enumerate(snake):
            color = head_color if i == 0 else body_color
            pygame.draw.rect(scr, color,
                             self.cell_rect(sc, sr).inflate(-3, -3), border_radius=4)


        pygame.draw.rect(scr, C.HUD_C, (0, 0, C.W, C.HUD_H))
        scr.blit(self.font.render(f"Score: {score}", True, C.TEXT_C), (8, 14))
        lv = self.font.render(f"Level: {level}", True, C.GOLD)
        scr.blit(lv, (C.W//2 - lv.get_width()//2, 14))
        nx = self.font.render(f"Next: {3-eaten}", True, (150, 150, 200))
        scr.blit(nx, (C.W - nx.get_width() - 8, 14))


        if self.best > 0:
            pb = self.font.render(f"Best: {self.best}", True, (150, 220, 150))
            scr.blit(pb, (C.W//2 - pb.get_width()//2, C.HUD_H - 18))


        if active_effect:
            etype, end_ms = active_effect
            remaining = max(0, (end_ms - pygame.time.get_ticks()) // 1000)
            col = C.PU_COLORS[etype]
            ind = self.font.render(
                f"{C.PU_LABELS[etype]} {remaining}s", True, col)
            scr.blit(ind, (8, C.HUD_H - 18))

        pygame.display.flip()

    def level_flash(self, level, snake, foods, poison, powerup,
                    obstacles, score, eaten, effect, shield):
        """Show LEVEL N! message for 900 ms."""
        self.draw(snake, foods, poison, powerup, obstacles,
                  score, level, eaten, effect, shield)
        msg = self.font_big.render(f"LEVEL  {level}!", True, C.GOLD)
        box = pygame.Rect(C.W//2 - msg.get_width()//2 - 20,
                          C.H//2 - 54,
                          msg.get_width() + 40, 92)
        pygame.draw.rect(self.screen, (20, 28, 44), box, border_radius=12)
        self.screen.blit(msg, (C.W//2 - msg.get_width()//2, C.H//2 - 40))
        pygame.display.flip()
        pygame.time.wait(900)



    def run(self):
        """Play one game session. Returns (score, level)."""


        sx, sy    = C.COLS//2, C.ROWS//2
        snake     = [(sx, sy), (sx-1, sy), (sx-2, sy)]
        body      = set(snake)
        direction = (1, 0)
        next_dir  = (1, 0)
        score, level, eaten, fps = 0, 1, 0, C.FPS_INIT


        ft       = self.pick_food()
        foods    = [(self.free_pos(body), ft, ft[3], ft[3])]


        poison = None
        poison_cd = 5    


        powerup_on_field = None
        pu_next_spawn    = pygame.time.get_ticks() + C.PU_SPAWN_INTERVAL


        active_effect = None
        shield_on     = False


        obstacles: set = set()


        while True:
            self.clock.tick(fps)
            now = pygame.time.get_ticks()


            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit(); import sys; sys.exit()
                if e.type == KEYDOWN:
                    if e.key in (K_UP,    K_w) and direction != (0, 1):  next_dir = (0,-1)
                    if e.key in (K_DOWN,  K_s) and direction != (0,-1):  next_dir = (0, 1)
                    if e.key in (K_LEFT,  K_a) and direction != (1, 0):  next_dir = (-1,0)
                    if e.key in (K_RIGHT, K_d) and direction != (-1,0):  next_dir = (1, 0)

            direction = next_dir


            if active_effect and now > active_effect[1]:
                etype, _ = active_effect
                # Reverse speed change
                if etype == C.PU_SPEED: fps -= C.SPEED_BOOST_DELTA
                if etype == C.PU_SLOW:  fps += C.SLOW_DELTA
                active_effect = None


            if powerup_on_field:
                pos, putype, spawn_ms = powerup_on_field
                if now - spawn_ms > C.PU_FIELD_MS:
                    powerup_on_field = None


            if powerup_on_field is None and now >= pu_next_spawn:
                occupied = body | obstacles | {f[0] for f in foods}
                putype   = random.choice([C.PU_SPEED, C.PU_SLOW, C.PU_SHIELD])
                powerup_on_field = (self.free_pos(occupied), putype, now)
                pu_next_spawn    = now + C.PU_SPAWN_INTERVAL


            poison_cd -= 1
            if poison is None and poison_cd <= 0:
                if random.random() < 0.3:   
                    occupied = body | obstacles | {f[0] for f in foods}
                    poison   = (self.free_pos(occupied), C.POISON_LIFETIME, C.POISON_LIFETIME)
                poison_cd = 10


            hx, hy = snake[0]
            dx, dy = direction
            head   = (hx+dx, hy+dy)
            nx, ny = head


            hit = (self.is_wall(nx, ny)
                   or head in obstacles
                   or head in body)
            if hit:
                if shield_on:
                    shield_on = False   
                else:
                    return score, level

            snake.insert(0, head)
            body.add(head)

            grew = False


            new_foods = []
            for (fc, fr), ftype, timer, lifetime in foods:
                if head == (fc, fr):
                    score += ftype[0]
                    eaten += 1
                    grew   = True
                    nf     = self.pick_food()
                    occ    = body | obstacles | {f[0] for f in new_foods}
                    new_foods.append((self.free_pos(occ), nf, nf[3], nf[3]))
                elif timer - 1 > 0:
                    new_foods.append(((fc, fr), ftype, timer-1, lifetime))
                else:
                    nf  = self.pick_food()
                    occ = body | obstacles | {f[0] for f in new_foods}
                    new_foods.append((self.free_pos(occ), nf, nf[3], nf[3]))
            foods = new_foods


            if poison:
                (pc, pr), ptimer, plife = poison
                if head == (pc, pr):
                    
                    for _ in range(C.POISON_SHORTEN):
                        if len(snake) > 1:
                            removed = snake.pop()
                            body.discard(removed)
                    if len(snake) <= 1:
                        return score, level   
                    poison = None
                    grew   = True             
                elif ptimer - 1 > 0:
                    poison = ((pc, pr), ptimer-1, plife)
                else:
                    poison = None 


            if powerup_on_field:
                (puc, pur), putype, spawn_ms = powerup_on_field
                if head == (puc, pur):
                    powerup_on_field = None
                    
                    if active_effect:
                        old, _ = active_effect
                        if old == C.PU_SPEED: fps -= C.SPEED_BOOST_DELTA
                        if old == C.PU_SLOW:  fps += C.SLOW_DELTA
                        
                    if putype == C.PU_SPEED:
                        fps           += C.SPEED_BOOST_DELTA
                        active_effect  = (putype, now + C.PU_EFFECT_MS)
                    elif putype == C.PU_SLOW:
                        fps           -= C.SLOW_DELTA
                        active_effect  = (putype, now + C.PU_EFFECT_MS)
                    elif putype == C.PU_SHIELD:
                        shield_on     = True
                        active_effect = (putype, now + C.PU_EFFECT_MS)


            if not grew:
                tail = snake.pop()
                body.discard(tail)


            if eaten >= 3:
                eaten  = 0
                level += 1
                fps   += 0.5   


                if level >= 3:
                    occ = body | obstacles | {f[0] for f in foods}
                    added = 0
                    while added < C.OBSTACLES_PER_LVL:
                        pos = self.free_pos(occ)
                        
                        if abs(pos[0]-snake[0][0]) + abs(pos[1]-snake[0][1]) > 3:
                            obstacles.add(pos)
                            occ.add(pos)
                            added += 1

                self.level_flash(level, snake, foods, poison, powerup_on_field,
                                 obstacles, score, eaten, active_effect, shield_on)


            self.draw(snake, foods, poison, powerup_on_field, obstacles,
                      score, level, eaten, active_effect, shield_on)
