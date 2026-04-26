import pygame, sys, json, os
from pygame.locals import *
import config as C
import db
from game import Game

pygame.init()

screen = pygame.display.set_mode((C.W, C.H))
pygame.display.set_caption("Snake – TSIS 4")
clock = pygame.time.Clock()

# Fonts
font_big  = pygame.font.SysFont("Consolas", 52, bold=True)
font_med  = pygame.font.SysFont("Consolas", 26, bold=True)
font_sm   = pygame.font.SysFont("Consolas", 20)
font_tiny = pygame.font.SysFont("Consolas", 16)

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "snake_color": [60, 220, 60],
    "grid":        True,
    "sound":       False,
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


def draw_button(rect, text, active=False):
    """Draw a rounded button; returns rect for click detection."""
    bg = (55, 120, 220) if active else (50, 50, 70)
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    pygame.draw.rect(screen, (100, 120, 180), rect, 2, border_radius=8)
    t = font_sm.render(text, True, (240, 240, 240))
    screen.blit(t, (rect.centerx - t.get_width()//2,
                     rect.centery - t.get_height()//2))
    return rect

def center_text(text, y, font, color=(220, 220, 220)):
    s = font.render(text, True, color)
    screen.blit(s, (C.W//2 - s.get_width()//2, y))



def screen_username():
    """Prompt user to enter a name. Returns username string."""
    buf = ""
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_RETURN and buf.strip():
                    return buf.strip()
                elif e.key == K_BACKSPACE:
                    buf = buf[:-1]
                elif e.unicode.isprintable() and len(buf) < 16:
                    buf += e.unicode

        screen.fill(C.BG)
        center_text("SNAKE", C.H//2 - 130, font_big, (60, 220, 60))
        center_text("Enter your name:", C.H//2 - 30, font_med)
        # Input box
        box = pygame.Rect(C.W//2 - 140, C.H//2 + 10, 280, 40)
        pygame.draw.rect(screen, (30, 40, 60), box, border_radius=6)
        pygame.draw.rect(screen, (100, 140, 200), box, 2, border_radius=6)
        t = font_med.render(buf + "|", True, (255, 255, 255))
        screen.blit(t, (box.x + 10, box.y + 8))
        center_text("Press ENTER to continue", C.H//2 + 70, font_sm, (130, 130, 150))
        pygame.display.flip()



def screen_menu(username):
    """Main menu with Play, Leaderboard, Settings, Quit buttons."""
    BW, BH = 220, 44
    bx = C.W//2 - BW//2
    btns = {
        "play":    pygame.Rect(bx, C.H//2 - 10,  BW, BH),
        "leader":  pygame.Rect(bx, C.H//2 + 64,  BW, BH),
        "settings":pygame.Rect(bx, C.H//2 + 120, BW, BH),
        "quit":    pygame.Rect(bx, C.H//2 + 176, BW, BH),
    }
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if btns["play"].collidepoint(e.pos):    return "play"
                if btns["leader"].collidepoint(e.pos):  return "leaderboard"
                if btns["settings"].collidepoint(e.pos):return "settings"
                if btns["quit"].collidepoint(e.pos):
                    pygame.quit(); sys.exit()

        screen.fill(C.BG)
        center_text("SNAKE", C.H//2 - 100, font_big, (60, 220, 60))
        center_text(f"Player: {username}", C.H//2 - 36, font_sm, (150, 200, 150))
        draw_button(btns["play"],     "▶  Play")
        draw_button(btns["leader"],   "🏆  Leaderboard")
        draw_button(btns["settings"], "⚙  Settings")
        draw_button(btns["quit"],     "✕  Quit")
        pygame.display.flip()



def screen_gameover(score, level, best):
    BW, BH = 180, 40
    bx     = C.W//2 - BW//2
    b_retry = pygame.Rect(bx, C.H//2 + 60,  BW, BH)
    b_menu  = pygame.Rect(bx, C.H//2 + 114, BW, BH)
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if b_retry.collidepoint(e.pos): return "retry"
                if b_menu.collidepoint(e.pos):  return "menu"
            if e.type == KEYDOWN and e.key == K_SPACE: return "retry"

        screen.fill(C.BG)
        center_text("GAME OVER", C.H//2 - 100, font_big, (220, 40, 40))
        center_text(f"Score: {score}   Level: {level}", C.H//2 - 20, font_med)
        new_best = score >= best and best > 0
        center_text(f"Best:  {max(score, best)}" + (" ★ NEW!" if score > best else ""),
                    C.H//2 + 20, font_sm, (255, 200, 0) if new_best else C.TEXT_C)
        draw_button(b_retry, "▶  Retry")
        draw_button(b_menu,  "↩  Menu")
        pygame.display.flip()



def screen_leaderboard():
    b_back = pygame.Rect(C.W//2 - 80, C.H - 60, 160, 38)
    rows   = db.get_leaderboard(10)
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                if b_back.collidepoint(e.pos): return
            if e.type == KEYDOWN and e.key == K_ESCAPE: return

        screen.fill(C.BG)
        center_text("🏆  LEADERBOARD", 20, font_med, C.GOLD)

        if not rows:
            center_text("No data (DB not connected)", C.H//2, font_sm, (150, 150, 150))
        else:
            # Table header
            cols_x = [20, 50, 160, 260, 340, 450]
            headers = ["#", "Name", "Score", "Level", "Date"]
            for i, h in enumerate(headers):
                screen.blit(font_tiny.render(h, True, (160, 160, 200)),
                             (cols_x[i], 70))
            pygame.draw.line(screen, (60, 70, 100), (10, 92), (C.W-10, 92), 1)

            for ri, (rank, name, score, level, date) in enumerate(rows):
                y    = 100 + ri * 28
                vals = [str(rank), name, str(score), str(level), date]
                col  = C.GOLD if ri == 0 else C.TEXT_C
                for i, v in enumerate(vals):
                    screen.blit(font_tiny.render(v, True, col), (cols_x[i], y))

        draw_button(b_back, "↩  Back")
        pygame.display.flip()



SNAKE_COLOR_OPTIONS = [
    ([60,  220,  60],  "Green"),
    ([30,  80,  220],  "Blue"),
    ([220, 60,   60],  "Red"),
    ([220, 160,   0],  "Orange"),
    ([180,  0,  200],  "Purple"),
]

def screen_settings(settings):
    """Let user toggle grid, sound and pick snake colour. Returns updated settings."""
    s      = settings.copy()
    b_back = pygame.Rect(C.W//2 - 90, C.H - 60, 180, 38)
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # Grid toggle
                if pygame.Rect(C.W//2 + 40, 130, 90, 32).collidepoint(mx, my):
                    s["grid"] = not s["grid"]
                # Sound toggle
                if pygame.Rect(C.W//2 + 40, 180, 90, 32).collidepoint(mx, my):
                    s["sound"] = not s["sound"]
                # Colour buttons
                for ci, (col, _) in enumerate(SNAKE_COLOR_OPTIONS):
                    cr = pygame.Rect(40 + ci * 80, 260, 60, 30)
                    if cr.collidepoint(mx, my):
                        s["snake_color"] = col
                # Save & Back
                if b_back.collidepoint(mx, my):
                    save_settings(s)
                    return s

        screen.fill(C.BG)
        center_text("⚙  SETTINGS", 30, font_med)

        # Grid
        screen.blit(font_sm.render("Grid overlay:", True, C.TEXT_C), (40, 138))
        draw_button(pygame.Rect(C.W//2 + 40, 130, 90, 32),
                    "ON" if s["grid"] else "OFF", active=s["grid"])

        # Sound
        screen.blit(font_sm.render("Sound:", True, C.TEXT_C), (40, 188))
        draw_button(pygame.Rect(C.W//2 + 40, 180, 90, 32),
                    "ON" if s["sound"] else "OFF", active=s["sound"])

        # Snake colour
        screen.blit(font_sm.render("Snake colour:", True, C.TEXT_C), (40, 230))
        for ci, (col, name) in enumerate(SNAKE_COLOR_OPTIONS):
            cr      = pygame.Rect(40 + ci * 80, 260, 60, 30)
            active  = s["snake_color"] == col
            pygame.draw.rect(screen, col, cr, border_radius=4)
            bw = 3 if active else 1
            pygame.draw.rect(screen, (255,255,255), cr, bw, border_radius=4)
            t = font_tiny.render(name, True, (0,0,0))
            screen.blit(t, (cr.centerx - t.get_width()//2, cr.bottom + 2))

        draw_button(b_back, "💾  Save & Back")
        pygame.display.flip()



def main():
    db.init_db()           
    settings  = load_settings()
    username  = screen_username()
    player_id = db.get_or_create_player(username)
    best      = db.get_personal_best(player_id)

    state = "menu"

    while True:
        if state == "menu":
            action = screen_menu(username)
            state  = action

        elif state == "play" or state == "retry":
            g            = Game(screen, clock, settings, best)
            score, level = g.run()
            db.save_session(player_id, score, level)
            best  = max(best, score)
            state = screen_gameover(score, level, best)

        elif state == "leaderboard":
            screen_leaderboard()
            state = "menu"

        elif state == "settings":
            settings = screen_settings(settings)
            state    = "menu"


if __name__ == "__main__":
    main()
