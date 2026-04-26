import pygame, sys
from ui import Button, draw_text
from persistence import load_settings, save_settings, load_leaderboard, save_score
import racer

pygame.init()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

font_large = pygame.font.SysFont("Verdana", 40)
font_med = pygame.font.SysFont("Verdana", 30)
font_small = pygame.font.SysFont("Verdana", 20)

settings = load_settings()
player_name = ""

def main_menu():
    btn_play = Button(100, 200, 200, 50, "Play", font_med, (50, 150, 50), (255, 255, 255))
    btn_lb = Button(100, 270, 200, 50, "Leaderboard", font_med, (50, 50, 150), (255, 255, 255))
    btn_settings = Button(100, 340, 200, 50, "Settings", font_med, (150, 150, 50), (255, 255, 255))
    btn_quit = Button(100, 410, 200, 50, "Quit", font_med, (150, 50, 50), (255, 255, 255))

    while True:
        DISPLAYSURF.fill((30, 30, 30))
        draw_text(DISPLAYSURF, "RACER", font_large, (255, 255, 255), (SCREEN_WIDTH//2, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in [btn_play, btn_lb, btn_settings, btn_quit]:
            btn.update(mouse_pos)
            btn.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_play.is_clicked(event):
                return "name_input"
            if btn_lb.is_clicked(event):
                return "leaderboard"
            if btn_settings.is_clicked(event):
                return "settings"
            if btn_quit.is_clicked(event):
                pygame.quit()
                sys.exit()

        pygame.display.update()

def name_input_screen():
    global player_name
    input_rect = pygame.Rect(100, 250, 200, 40)
    while True:
        DISPLAYSURF.fill((30, 30, 30))
        draw_text(DISPLAYSURF, "Enter Name:", font_med, (255, 255, 255), (SCREEN_WIDTH//2, 180))
        
        pygame.draw.rect(DISPLAYSURF, (255, 255, 255), input_rect)
        draw_text(DISPLAYSURF, player_name, font_med, (0, 0, 0), input_rect.center)
        
        draw_text(DISPLAYSURF, "Press ENTER to Start", font_small, (200, 200, 200), (SCREEN_WIDTH//2, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    return "game"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10 and event.unicode.isprintable():
                        player_name += event.unicode

        pygame.display.update()

def settings_screen():
    global settings
    btn_diff = Button(100, 150, 200, 50, f"Diff: {settings['difficulty']}", font_small, (100, 100, 100), (255, 255, 255))
    btn_color = Button(100, 220, 200, 50, f"Color: {settings['color']}", font_small, (100, 100, 100), (255, 255, 255))
    btn_sound = Button(100, 290, 200, 50, f"Sound: {'On' if settings['sound'] else 'Off'}", font_small, (100, 100, 100), (255, 255, 255))
    btn_back = Button(100, 400, 200, 50, "Back", font_med, (150, 50, 50), (255, 255, 255))

    while True:
        DISPLAYSURF.fill((30, 30, 30))
        draw_text(DISPLAYSURF, "SETTINGS", font_large, (255, 255, 255), (SCREEN_WIDTH//2, 70))
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in [btn_diff, btn_color, btn_sound, btn_back]:
            btn.update(mouse_pos)
            btn.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_diff.is_clicked(event):
                diffs = ["Easy", "Medium", "Hard"]
                settings["difficulty"] = diffs[(diffs.index(settings["difficulty"]) + 1) % 3]
                btn_diff.text = f"Diff: {settings['difficulty']}"
            if btn_color.is_clicked(event):
                colors = ["Red", "Blue", "Green"]
                settings["color"] = colors[(colors.index(settings["color"]) + 1) % 3]
                btn_color.text = f"Color: {settings['color']}"
            if btn_sound.is_clicked(event):
                settings["sound"] = not settings["sound"]
                btn_sound.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
            if btn_back.is_clicked(event):
                save_settings(settings)
                return "menu"

        pygame.display.update()

def leaderboard_screen():
    btn_back = Button(100, 500, 200, 50, "Back", font_med, (150, 50, 50), (255, 255, 255))
    lb_data = load_leaderboard()

    while True:
        DISPLAYSURF.fill((30, 30, 30))
        draw_text(DISPLAYSURF, "TOP 10", font_large, (255, 255, 255), (SCREEN_WIDTH//2, 50))
        
        y = 120
        for i, entry in enumerate(lb_data):
            text = f"{i+1}. {entry['name']} - {entry['score']} ({entry['distance']}m)"
            draw_text(DISPLAYSURF, text, font_small, (255, 255, 255), (SCREEN_WIDTH//2, y))
            y += 35
        
        mouse_pos = pygame.mouse.get_pos()
        btn_back.update(mouse_pos)
        btn_back.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_back.is_clicked(event):
                return "menu"

        pygame.display.update()

def game_over_screen(result):
    save_score(player_name, result["score"], result["distance"])
    
    btn_retry = Button(100, 350, 200, 50, "Retry", font_med, (50, 150, 50), (255, 255, 255))
    btn_menu = Button(100, 420, 200, 50, "Menu", font_med, (150, 50, 50), (255, 255, 255))

    while True:
        DISPLAYSURF.fill((180, 0, 0))
        draw_text(DISPLAYSURF, "CRASHED!", font_large, (255, 255, 255), (SCREEN_WIDTH//2, 100))
        
        draw_text(DISPLAYSURF, f"Score: {result['score']}", font_med, (255, 255, 255), (SCREEN_WIDTH//2, 180))
        draw_text(DISPLAYSURF, f"Distance: {result['distance']}m", font_med, (255, 255, 255), (SCREEN_WIDTH//2, 230))
        draw_text(DISPLAYSURF, f"Coins: {result['coins']}", font_med, (255, 255, 255), (SCREEN_WIDTH//2, 280))

        mouse_pos = pygame.mouse.get_pos()
        for btn in [btn_retry, btn_menu]:
            btn.update(mouse_pos)
            btn.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_retry.is_clicked(event):
                return "game"
            if btn_menu.is_clicked(event):
                return "menu"

        pygame.display.update()

def main():
    state = "menu"
    result = None
    while True:
        if state == "menu":
            state = main_menu()
        elif state == "name_input":
            state = name_input_screen()
        elif state == "settings":
            state = settings_screen()
        elif state == "leaderboard":
            state = leaderboard_screen()
        elif state == "game":
            result = racer.run_game(DISPLAYSURF, settings, player_name)
            if result is None:
                break
            state = "game_over"
        elif state == "game_over":
            state = game_over_screen(result)

if __name__ == "__main__":
    main()