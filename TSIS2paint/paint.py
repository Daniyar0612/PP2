import pygame, sys, math, datetime
from pygame.locals import *
import tools   
 
pygame.init()
 
# SETTINGS
W, H = 960, 660
PANEL = 60          
CANVAS_H = H - PANEL
 
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Paint – TSIS 2")
clock = pygame.time.Clock()
 
# FONTS
font_ui = pygame.font.SysFont("Arial", 12, bold=True)
font_txt = pygame.font.SysFont("Arial", 20)   
 
canvas = pygame.Surface((W, CANVAS_H))
canvas.fill((255, 255, 255))
 
# PALETTE
COLORS = [
    (0,0,0),(255,255,255),(200,30,30),(30,180,30),
    (30,80,220),(255,200,0),(255,120,0),(180,0,200),
    (0,200,200),(255,150,180),(100,60,10),(150,150,150),
]
 
# SIZES
SIZES = [2, 5, 10]
SIZE_KEYS = [K_1, K_2, K_3]
SIZE_NAMES = ["S", "M", "L"]
 
# TOOLS
TOOL_LIST = [
    ("pencil",  "Pencil"),
    ("line",    "Line"),
    ("rect",    "Rect"),
    ("square",  "Square"),
    ("circle",  "Circle"),
    ("rtri",    "R.Tri"),
    ("etri",    "Eq.Tri"),
    ("rhombus", "Rhombus"),
    ("fill",    "Fill"),
    ("text",    "Text"),
    ("eraser",  "Eraser"),
]
 
DRAG_TOOLS = {"line","rect","square","circle","rtri","etri","rhombus"}
 
 
 
SW = 26
 
def build_ui():
    swatches, tool_btns, size_btns = [], [], []
 
    for i, c in enumerate(COLORS):
        swatches.append((c, pygame.Rect(6 + i*(SW+3), CANVAS_H+17, SW, SW)))
 
    bx = 6 + len(COLORS)*(SW+3) + 10
    BW = 52
    for i, (tid, lbl) in enumerate(TOOL_LIST):
        tool_btns.append((tid, lbl, pygame.Rect(bx + i*(BW+3), CANVAS_H+6, BW, 22)))
 
    sx = bx
    for i, nm in enumerate(SIZE_NAMES):
        size_btns.append((i, nm, pygame.Rect(sx + i*30, CANVAS_H+32, 26, 20)))
 
    return swatches, tool_btns, size_btns
 
swatches, tool_btns, size_btns = build_ui()
 
 
def draw_panel(color, tool, size_idx):
    """Render the bottom toolbar."""
    pygame.draw.rect(screen, (38, 38, 38), (0, CANVAS_H, W, PANEL))
    pygame.draw.line(screen, (80,80,80), (0, CANVAS_H), (W, CANVAS_H), 1)
 
    for c, r in swatches:
        pygame.draw.rect(screen, c, r)
        bw = 3 if c == color else 1
        bc = (255,255,255) if c != (255,255,255) else (0,0,0)
        pygame.draw.rect(screen, bc, r, bw)
 
    for tid, lbl, r in tool_btns:
        bg = (55, 120, 220) if tid == tool else (65,65,65)
        pygame.draw.rect(screen, bg, r, border_radius=3)
        t = font_ui.render(lbl, True, (255,255,255))
        screen.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))
 
    for idx, nm, r in size_btns:
        bg = (55, 180, 90) if idx == size_idx else (65,65,65)
        pygame.draw.rect(screen, bg, r, border_radius=3)
        t = font_ui.render(nm, True, (255,255,255))
        screen.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))
 
    pr = pygame.Rect(W-42, CANVAS_H+17, SW, SW)
    pygame.draw.rect(screen, color, pr)
    pygame.draw.rect(screen, (200,200,200), pr, 2)
 
    hint = font_ui.render("1/2/3 size   Ctrl+S save   DEL clear", True, (110,110,110))
    screen.blit(hint, (W - hint.get_width() - 6, CANVAS_H + 46))
 
 
 
def draw_shape(surface, tool, color, start, end, size):
    """Call the correct tools.py function for the active tool."""
    if tool == "line":    tools.draw_line(surface, color, start, end, size)
    elif tool == "rect":  tools.draw_rect(surface, color, start, end, size)
    elif tool == "square":tools.draw_square(surface, color, start, end, size)
    elif tool == "circle":tools.draw_circle(surface, color, start, end, size)
    elif tool == "rtri":  tools.draw_right_triangle(surface, color, start, end, size)
    elif tool == "etri":  tools.draw_equilateral_triangle(surface, color, start, end, size)
    elif tool == "rhombus":tools.draw_rhombus(surface, color, start, end, size)
 
 
color = (0, 0, 0)
tool = "pencil"
size_idx = 0           
drawing = False
start = None
last_pos = None
 
text_active = False    
text_pos = None    
text_buf = ""       
 
 
while True:
    sz = SIZES[size_idx]   
 
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit(); sys.exit()
 
        if e.type == KEYDOWN:
 
            if text_active:
                if e.key == K_RETURN:
                    surf = font_txt.render(text_buf, True, color)
                    canvas.blit(surf, text_pos)
                    text_active = False
                    text_buf = ""
                    text_pos = None
                elif e.key == K_ESCAPE:
                    text_active = False
                    text_buf = ""
                    text_pos = None
                elif e.key == K_BACKSPACE:
                    text_buf = text_buf[:-1]  
                else:
                    if e.unicode and e.unicode.isprintable():
                        text_buf += e.unicode
                continue  
 
            for ki, key in enumerate(SIZE_KEYS):
                if e.key == key:
                    size_idx = ki
 
            if e.key == K_p: tool = "pencil"
            if e.key == K_l: tool = "line"
            if e.key == K_r: tool = "rect"
            if e.key == K_c: tool = "circle"
            if e.key == K_e: tool = "eraser"
            if e.key == K_f: tool = "fill"
            if e.key == K_t: tool = "text"
 
            if e.key in (K_DELETE, K_BACKSPACE):
                canvas.fill((255, 255, 255))
 
            if e.key == K_s and (pygame.key.get_mods() & KMOD_CTRL):
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"drawing_{ts}.png"
                pygame.image.save(canvas, filename)
                pygame.display.set_caption(f"Paint – saved {filename}")
 
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
 
            if my >= CANVAS_H:
                for c, r in swatches:
                    if r.collidepoint(mx, my): color = c
                for tid, lbl, r in tool_btns:
                    if r.collidepoint(mx, my): tool = tid
                for idx, nm, r in size_btns:
                    if r.collidepoint(mx, my): size_idx = idx
 
            else:
                if tool == "fill":
                    tools.flood_fill(canvas, (mx, my), color)
 
                elif tool == "text":
                    text_active = True
                    text_pos = (mx, my)
                    text_buf = ""
 
                else:
                    drawing = True
                    start = (mx, my)
                    last_pos = (mx, my)
                    if tool == "pencil":
                        pygame.draw.circle(canvas, color, (mx,my), sz)
                    if tool == "eraser":
                        pygame.draw.circle(canvas, (255,255,255), (mx,my), sz*4)
 
        if e.type == MOUSEBUTTONUP and e.button == 1:
            if drawing and start and tool in DRAG_TOOLS:
                end = (e.pos[0], min(e.pos[1], CANVAS_H-1))
                draw_shape(canvas, tool, color, start, end, sz)
            drawing = False
            start = None
            last_pos = None
 
        if e.type == MOUSEMOTION and drawing:
            mx, my = e.pos[0], min(e.pos[1], CANVAS_H-1)
            if tool == "pencil" and last_pos:
                pygame.draw.line(canvas, color, last_pos, (mx,my), sz*2)
            if tool == "eraser" and last_pos:
                pygame.draw.line(canvas, (255,255,255), last_pos, (mx,my), sz*8)
            last_pos = (mx, my)
 
    screen.blit(canvas, (0, 0))   
 
    if drawing and start and tool in DRAG_TOOLS:
        mx, my = pygame.mouse.get_pos()[0], min(pygame.mouse.get_pos()[1], CANVAS_H-1)
        draw_shape(screen, tool, color, start, (mx, my), sz)
 
    if tool == "eraser":
        mx, my = pygame.mouse.get_pos()
        if my < CANVAS_H:
            pygame.draw.circle(screen, (160,160,160), (mx,my), sz*8, 2)
 
    if text_active and text_pos:
        preview = font_txt.render(text_buf + "|", True, color)
        screen.blit(preview, text_pos)
        box = pygame.Rect(text_pos[0]-2, text_pos[1]-2,
                          preview.get_width()+4, preview.get_height()+4)
        s = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        s.fill((255, 255, 255, 160))
        screen.blit(s, box.topleft)
        screen.blit(preview, text_pos)
 
    draw_panel(color, tool, size_idx)
    pygame.display.flip()
    clock.tick(60)