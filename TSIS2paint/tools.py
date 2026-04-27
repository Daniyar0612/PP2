import pygame
import math
from collections import deque



def draw_line(surface, color, start, end, size):
    
    pygame.draw.line(surface, color, start, end, size)


def draw_rect(surface, color, start, end, size):
    x0, y0 = start
    x1, y1 = end
    rect = (min(x0,x1), min(y0,y1), abs(x1-x0), abs(y1-y0))
    if rect[2] > 0 and rect[3] > 0:
        pygame.draw.rect(surface, color, rect, size)


def draw_square(surface, color, start, end, size):
    x0, y0 = start
    x1, y1 = end
    side = min(abs(x1-x0), abs(y1-y0))
    sx = side if x1 >= x0 else -side
    sy = side if y1 >= y0 else -side
    rect = (min(x0, x0+sx), min(y0, y0+sy), side, side)
    if side > 0:
        pygame.draw.rect(surface, color, rect, size)


def draw_circle(surface, color, start, end, size):
    r = int(math.hypot(end[0]-start[0], end[1]-start[1]))
    if r > 0:
        pygame.draw.circle(surface, color, start, r, size)


def draw_right_triangle(surface, color, start, end, size):
    x0, y0 = start
    x1, y1 = end
    pts = [(x0, y0), (x1, y0), (x0, y1)]
    pygame.draw.polygon(surface, color, pts, size)


def draw_equilateral_triangle(surface, color, start, end, size):
    x0, y0 = start
    x1, y1 = end
    base = math.hypot(x1-x0, y1-y0)
    if base < 1:
        return
    h = (math.sqrt(3) / 2) * base
    dx, dy = (x1-x0)/base, (y1-y0)/base
    nx, ny = -dy, dx
    mx, my = (x0+x1)/2, (y0+y1)/2         
    apex = (mx + nx*h, my + ny*h)
    pts = [(x0, y0), (x1, y1), apex]
    pygame.draw.polygon(surface, color, pts, size)


def draw_rhombus(surface, color, start, end, size):
    x0, y0 = start
    x1, y1 = end
    mx, my = (x0+x1)//2, (y0+y1)//2
    pts = [(mx, y0), (x1, my), (mx, y1), (x0, my)]
    pygame.draw.polygon(surface, color, pts, size)

def flood_fill(surface, pos, new_color):
    
    x, y = int(pos[0]), int(pos[1])
    w, h = surface.get_size()

    target = surface.get_at((x, y))[:3] 
    if target == new_color[:3]:
        return

    queue = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if surface.get_at((cx, cy))[:3] != target:
            continue

        surface.set_at((cx, cy), new_color)

        for nx, ny in [(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)]:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))
