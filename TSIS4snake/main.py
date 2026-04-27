import pygame, sys, json, os
from pygame.locals import *
import config as C
import db
from game import Game

pygame.init()
screen = pygame.display.set_mode((C.W, C.H))
pygame.display.set_caption("Snake - PostgreSQL")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Consolas", 52, bold=True)
font_med = pygame.font.SysFont("Consolas", 26, bold=True)
font_sm = pygame.font.SysFont("Consolas", 20)
font_tiny = pygame.font.SysFont("Consolas", 16)

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"snake_color": [0, 200, 0], "grid": True, "sound": False}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f: return {**DEFAULT_SETTINGS, **json.load(f)}
        except: pass
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f: json.dump(s, f, indent=2)

def draw_button(rect, text, active=False):
    bg = (60, 100, 200) if active else (40, 60, 100)
    pygame.draw.rect(screen, bg, rect, border_radius=10)
    t = font_sm.render(text, True, (255, 255, 255))
    screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
    return rect

def center_text(text, y, font, color=(35, 35, 50)):
    s = font.render(text, True, color)
    screen.blit(s, (C.W//2 - s.get_width()//2, y))

def screen_username():
    buf = ""
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_RETURN and buf.strip(): return buf.strip()
                elif e.key == K_BACKSPACE: buf = buf[:-1]
                elif e.unicode.isprintable() and len(buf) < 16: buf += e.unicode
        screen.fill(C.OUTER_BG)
        center_text("SNAKE GAME", C.H//2 - 130, font_big, C.HUD_C)
        center_text("ENTER NAME:", C.H//2 - 30, font_med)
        box = pygame.Rect(C.W//2 - 140, C.H//2 + 10, 280, 45)
        pygame.draw.rect(screen, (255, 255, 255), box)
        pygame.draw.rect(screen, C.HUD_C, box, 3)
        t = font_med.render(buf + "|", True, (0, 0, 0))
        screen.blit(t, (box.x + 10, box.y + 8))
        pygame.display.flip()

def screen_menu(username):
    bw, bh, bx = 220, 48, C.W//2 - 110
    btns = {
        "play": pygame.Rect(bx, C.H//2 - 20, bw, bh),
        "leader": pygame.Rect(bx, C.H//2 + 40, bw, bh),
        "settings": pygame.Rect(bx, C.H//2 + 100, bw, bh),
        "quit": pygame.Rect(bx, C.H//2 + 160, bw, bh),
    }
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if btns["play"].collidepoint(e.pos): return "play"
                if btns["leader"].collidepoint(e.pos): return "leaderboard"
                if btns["settings"].collidepoint(e.pos): return "settings"
                if btns["quit"].collidepoint(e.pos): pygame.quit(); sys.exit()
        screen.fill(C.OUTER_BG)
        center_text("MAIN MENU", C.H//2 - 120, font_big, C.HUD_C)
        center_text(f"PLAYER: {username}", C.H//2 - 55, font_sm)
        draw_button(btns["play"], "PLAY")
        draw_button(btns["leader"], "LEADERBOARD")
        draw_button(btns["settings"], "SETTINGS")
        draw_button(btns["quit"], "QUIT")
        pygame.display.flip()

def screen_gameover(score, level, best):
    bw, bh, bx = 180, 45, C.W//2 - 90
    b_retry = pygame.Rect(bx, C.H//2 + 70, bw, bh)
    b_menu = pygame.Rect(bx, C.H//2 + 125, bw, bh)
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if b_retry.collidepoint(e.pos): return "retry"
                if b_menu.collidepoint(e.pos): return "menu"
        screen.fill(C.OUTER_BG)
        center_text("GAME OVER", C.H//2 - 100, font_big, (200, 30, 30))
        center_text(f"SCORE: {score}  LEVEL: {level}", C.H//2 - 20, font_med)
        center_text(f"BEST: {max(score, best)}", C.H//2 + 20, font_sm)
        draw_button(b_retry, "RETRY")
        draw_button(b_menu, "MENU")
        pygame.display.flip()

def screen_leaderboard():
    b_back = pygame.Rect(C.W//2 - 80, C.H - 60, 160, 40)
    rows = db.get_leaderboard(10)
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if b_back.collidepoint(e.pos): return
        screen.fill(C.OUTER_BG)
        center_text("LEADERBOARD", 30, font_med, C.HUD_C)
        if not rows: center_text("NO DATA", C.H//2, font_sm)
        else:
            cols_x = [30, 70, 200, 320, 430]
            for i, h in enumerate(["#", "NAME", "SCORE", "LVL", "DATE"]):
                screen.blit(font_tiny.render(h, True, (50, 50, 80)), (cols_x[i], 80))
            for ri, (rank, name, score, lvl, date) in enumerate(rows):
                y = 110 + ri * 30
                for i, v in enumerate([str(rank), name, str(score), str(lvl), date]):
                    screen.blit(font_tiny.render(v, True, (20, 20, 40)), (cols_x[i], y))
        draw_button(b_back, "BACK")
        pygame.display.flip()

def screen_settings(settings):
    s, b_back = settings.copy(), pygame.Rect(C.W//2 - 90, C.H - 60, 180, 40)
    cols = [([0, 200, 0], "Green"), ([0, 100, 255], "Blue"), ([255, 50, 50], "Red")]
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if pygame.Rect(C.W//2 + 40, 130, 90, 35).collidepoint(e.pos): s["grid"] = not s["grid"]
                for i, (c, _) in enumerate(cols):
                    if pygame.Rect(50 + i * 100, 260, 70, 35).collidepoint(e.pos): s["snake_color"] = c
                if b_back.collidepoint(e.pos): save_settings(s); return s
        screen.fill(C.OUTER_BG)
        center_text("SETTINGS", 30, font_med, C.HUD_C)
        screen.blit(font_sm.render("GRID OVERLAY:", True, (0, 0, 0)), (50, 138))
        draw_button(pygame.Rect(C.W//2 + 40, 130, 90, 35), "ON" if s["grid"] else "OFF", s["grid"])
        center_text("SNAKE COLOR:", 220, font_sm)
        for i, (c, n) in enumerate(cols):
            cr = pygame.Rect(50 + i * 100, 260, 70, 35)
            pygame.draw.rect(screen, c, cr, border_radius=5)
            if s["snake_color"] == c: pygame.draw.rect(screen, (255, 255, 255), cr, 3, border_radius=5)
        draw_button(b_back, "SAVE")
        pygame.display.flip()

def main():
    db.init_db()
    settings = load_settings()
    username = screen_username()
    pid = db.get_or_create_player(username)
    best = db.get_personal_best(pid)
    state = "menu"
    while True:
        if state == "menu": state = screen_menu(username)
        elif state in ["play", "retry"]:
            score, lvl = Game(screen, clock, settings, best).run()
            db.save_session(pid, score, lvl)
            best = max(best, score)
            state = screen_gameover(score, lvl, best)
        elif state == "leaderboard": screen_leaderboard(); state = "menu"
        elif state == "settings": settings = screen_settings(settings); state = "menu"

if __name__ == "__main__": main()