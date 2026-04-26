
CELL = 20     
COLS = 25      
ROWS = 25    
HUD_H = 50     
W = COLS * CELL
H = ROWS * CELL + HUD_H
FPS_INIT = 8     


BG = (15,  24,  36)
WALL_C = (80,  95, 120)
GRID_C = (25,  35,  50)
HUD_C = (10,  16,  26)
TEXT_C = (220, 220, 220)
GOLD = (255, 200,   0)


FOOD_TYPES = [
    (10, (220,  55,  55), "+10", 40),   
    (20, ( 80, 180, 255), "+20", 25),   
    (30, (255, 200,   0), "+30", 15),   
]
FOOD_WEIGHTS = [60, 30, 10]


POISON_COLOR = (120,   0,   0)
POISON_LABEL = "☠"
POISON_SHORTEN = 2     
POISON_LIFETIME = 30    


PU_SPEED  = "speed"
PU_SLOW   = "slow"
PU_SHIELD = "shield"

PU_COLORS = {
    PU_SPEED:  (50,  220, 255),
    PU_SLOW:   (200,  80, 255),
    PU_SHIELD: (255, 200,  50),
}
PU_LABELS = {PU_SPEED: "⚡", PU_SLOW: "🐢", PU_SHIELD: "🛡"}

PU_FIELD_MS = 8000   
PU_EFFECT_MS = 5000   
PU_SPAWN_INTERVAL = 6000   


SPEED_BOOST_DELTA = 3
SLOW_DELTA = 3


OBSTACLE_COLOR = (140, 100,  60)   
OBSTACLES_PER_LVL = 4                 
