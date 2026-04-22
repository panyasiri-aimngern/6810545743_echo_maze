import pygame
from constants import *


class Map:
    def __init__(self, stage: int):
        raw = MAPS[min(stage, max(MAPS.keys()))]
        self.grid: list[list[str]] = []
        self.start = (1, 1)
        self.goal  = (COLS - 2, ROWS - 2)
        self.checkpoints: list[tuple[int, int]] = []
        self.breakable_hp: dict[tuple[int, int], int] = {}

        for r, row in enumerate(raw):
            line = []
            for c, ch in enumerate(row):
                if ch == 'P':
                    self.start = (c, r)
                    line.append(' ')
                elif ch == 'G':
                    self.goal = (c, r)
                    line.append(' ')
                elif ch == 'C':
                    self.checkpoints.append((c, r))
                    line.append(' ')
                elif ch == 'B':
                    self.breakable_hp[(c, r)] = 3
                    line.append('B')
                else:
                    line.append(ch)
            self.grid.append(line)

    # Queries
    def is_wall(self, x: int, y: int) -> bool:
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return True
        return self.grid[y][x] in ('#', 'B')

    def is_breakable(self, x: int, y: int) -> bool:
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return False
        return self.grid[y][x] == 'B'

    def break_wall(self, x: int, y: int):
        key = (x, y)
        if key in self.breakable_hp:
            self.breakable_hp[key] -= 1
            if self.breakable_hp[key] <= 0:
                self.grid[y][x] = ' '
                del self.breakable_hp[key]

    # Draw 
    def draw(self, surf: pygame.Surface, offset_y: int, goal_open: bool):
        T = TILE
        for r in range(ROWS):
            for c in range(COLS):
                x = c * T
                y = r * T + offset_y
                ch = self.grid[r][c]

                if ch == '#':
                    pygame.draw.rect(surf, C_WALL,       (x, y, T, T))
                    pygame.draw.rect(surf, C_WALL_INNER, (x+2, y+2, T-4, T-4))
                    pygame.draw.rect(surf, C_WALL_EDGE,  (x, y, T, T), 1)

                elif ch == 'B':
                    hp = self.breakable_hp.get((c, r), 3)
                    col = C_BREAK_3 if hp >= 3 else C_BREAK_2 if hp == 2 else C_BREAK_1
                    pygame.draw.rect(surf, C_WALL,  (x, y, T, T))
                    pygame.draw.rect(surf, col,     (x+2, y+2, T-4, T-4))
                    pygame.draw.rect(surf, C_BREAK_EDGE, (x+1, y+1, T-2, T-2), 2)
                    # crack lines
                    pygame.draw.line(surf, C_BREAK_LINE, (x+6, y+5),   (x+T//2, y+T//2), 1)
                    pygame.draw.line(surf, C_BREAK_LINE, (x+T//2, y+T//2), (x+T-6, y+T-5), 1)
                    if hp <= 2:
                        pygame.draw.line(surf, C_BREAK_LINE, (x+4, y+T-4), (x+T//2-2, y+T//2), 1)
                    if hp <= 1:
                        pygame.draw.line(surf, C_BREAK_LINE, (x+T-4, y+T-4), (x+T//2+2, y+T//2), 1)
                        s = pygame.Surface((T-4, T-4), pygame.SRCALPHA)
                        s.fill((255, 120, 40, 80))
                        surf.blit(s, (x+2, y+2))

                else:
                    pygame.draw.rect(surf, C_FLOOR, (x, y, T, T))

        # checkpoints
        for (cx, cy) in self.checkpoints:
            px = cx * T + T // 2
            py = cy * T + T // 2 + offset_y
            glow = pygame.Surface((T, T), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 0, 30), (T//2, T//2), T//2)
            surf.blit(glow, (cx*T, cy*T + offset_y))
            pygame.draw.circle(surf, C_CHECKPOINT, (px, py), T // 5)
            pygame.draw.circle(surf, (255, 255, 255), (px - 2, py - 2), 2)

        # goal
        gx, gy = self.goal
        gpx = gx * T + 5
        gpy = gy * T + 5 + offset_y
        gw = T - 10
        color = C_GOAL_OPEN if goal_open else C_GOAL_CLOSED
        pygame.draw.rect(surf, color, (gpx, gpy, gw, gw), border_radius=4)
        if goal_open:
            pygame.draw.rect(surf, (0, 255, 170), (gpx-2, gpy-2, gw+4, gw+4), 2, border_radius=5)

    def draw_scaled(self, surf: pygame.Surface, mx: int, my: int, tile: int, goal_open: bool, collected: set = None):
        if collected is None:
            collected = set()
        T = tile
        for r in range(ROWS):
            for c in range(COLS):
                x = mx + c * T
                y = my + r * T
                ch = self.grid[r][c]
                if ch == '#':
                    pygame.draw.rect(surf, C_WALL,       (x, y, T, T))
                    pygame.draw.rect(surf, C_WALL_INNER, (x+2, y+2, T-4, T-4))
                    pygame.draw.rect(surf, C_WALL_EDGE,  (x, y, T, T), 1)
                elif ch == 'B':
                    hp  = self.breakable_hp.get((c, r), 3)
                    col = C_BREAK_3 if hp >= 3 else C_BREAK_2 if hp == 2 else C_BREAK_1
                    pygame.draw.rect(surf, C_WALL, (x, y, T, T))
                    pygame.draw.rect(surf, col,    (x+2, y+2, T-4, T-4))
                    pygame.draw.rect(surf, C_BREAK_EDGE, (x+1, y+1, T-2, T-2), 2)
                    pygame.draw.line(surf, C_BREAK_LINE, (x+max(2,T//6), y+max(2,T//7)),   (x+T//2, y+T//2), 1)
                    pygame.draw.line(surf, C_BREAK_LINE, (x+T//2, y+T//2), (x+T-max(2,T//6), y+T-max(2,T//7)), 1)
                    if hp <= 2:
                        pygame.draw.line(surf, C_BREAK_LINE, (x+max(2,T//8), y+T-max(2,T//8)), (x+T//2-1, y+T//2), 1)
                    if hp <= 1:
                        pygame.draw.line(surf, C_BREAK_LINE, (x+T-max(2,T//8), y+T-max(2,T//8)), (x+T//2+1, y+T//2), 1)
                        s2 = pygame.Surface((T-4, T-4), pygame.SRCALPHA)
                        s2.fill((255, 120, 40, 80))
                        surf.blit(s2, (x+2, y+2))
                else:
                    pygame.draw.rect(surf, C_FLOOR, (x, y, T, T))

        # checkpoints
        for (cx2, cy2) in self.checkpoints:
            if (cx2, cy2) in collected:
                continue
            px2 = mx + cx2*T + T//2
            py2 = my + cy2*T + T//2
            r2  = max(2, T//5)
            glow = pygame.Surface((T, T), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255,220,0,40), (T//2,T//2), T//2)
            surf.blit(glow, (mx+cx2*T, my+cy2*T))
            pygame.draw.circle(surf, C_CHECKPOINT, (px2, py2), r2)
            pygame.draw.circle(surf, C_WHITE, (px2-max(1,r2//2), py2-max(1,r2//2)), max(1,r2//3))

        # goal
        gx2, gy2 = self.goal
        pad2 = max(3, T//7)
        gx3  = mx + gx2*T + pad2
        gy3  = my + gy2*T + pad2
        gs   = T - pad2*2
        color = C_GOAL_OPEN if goal_open else C_GOAL_CLOSED
        pygame.draw.rect(surf, color, (gx3, gy3, gs, gs), border_radius=max(2, T//9))
        if goal_open:
            pygame.draw.rect(surf, (0,255,170), (gx3-2, gy3-2, gs+4, gs+4), 2, border_radius=max(2,T//8))
