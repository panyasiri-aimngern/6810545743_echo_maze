import pygame
from constants import *


class Ghost:
    def __init__(self, path: list[dict], color_idx: int = 0):
        self.path = path
        self.color = C_GHOST[color_idx % len(C_GHOST)]
        self.idx = 0
        self.x = path[0]['x']
        self.y = path[0]['y']
        self.px = float(self.x * TILE)
        self.py = float(self.y * TILE)
        self.moving = False
        self.progress = 0.0
        self.done = False

    def reset(self):
        self.idx = 0
        self.x = self.path[0]['x']
        self.y = self.path[0]['y']
        self.px = float(self.x * TILE)
        self.py = float(self.y * TILE)
        self.moving = False
        self.progress = 0.0
        self.done = False

    def update(self):
        if self.done:
            return
        if self.moving:
            self.progress += SPEED / TILE
            if self.progress >= 1.0:
                self.x = self.path[self.idx]['x']
                self.y = self.path[self.idx]['y']
                self.px = float(self.x * TILE)
                self.py = float(self.y * TILE)
                self.moving = False
                self.progress = 0.0
            else:
                prev_idx = max(0, self.idx - 1)
                px0 = self.path[prev_idx]['x']
                py0 = self.path[prev_idx]['y']
                px1 = self.path[self.idx]['x']
                py1 = self.path[self.idx]['y']
                self.px = (px0 + (px1 - px0) * self.progress) * TILE
                self.py = (py0 + (py1 - py0) * self.progress) * TILE
        else:
            self.idx += 1
            if self.idx >= len(self.path):
                self.idx = 0
            self.moving = True
            self.progress = 0.0

    def check_collision(self, player) -> bool:
        return round(self.px / TILE) == player.x and round(self.py / TILE) == player.y

    def draw(self, surf: pygame.Surface, offset_y: int):
        T = TILE
        cx = int(self.px) + T // 2
        cy = int(self.py) + T // 2 + offset_y

        glow = pygame.Surface((T+4, T+4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 51), (T//2+2, T//2+2), T//2+2)
        surf.blit(glow, (int(self.px)-2, int(self.py)-2+offset_y))

        body = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.circle(body, (*self.color, 204), (T//2, T//2), T//2-5)
        surf.blit(body, (int(self.px), int(self.py)+offset_y))

        for ex, ey in [(-5, -3), (5, -3)]:
            pygame.draw.circle(surf, C_GHOST_EYE,   (cx+ex, cy+ey), 4)
            pygame.draw.circle(surf, C_GHOST_PUPIL, (cx+ex+1, cy+ey), 2)

    def draw_scaled(self, surf: pygame.Surface, mx: int, my: int, tile: int):
        T  = tile
        px = mx + int(self.px * T / TILE)
        py = my + int(self.py * T / TILE)
        cx = px + T//2; cy = py + T//2
        r  = max(2, T//2 - max(2, T//7))
        glow = pygame.Surface((T+4, T+4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 51), (T//2+2, T//2+2), T//2+2)
        surf.blit(glow, (px-2, py-2))
        body = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.circle(body, (*self.color, 204), (T//2, T//2), r)
        surf.blit(body, (px, py))
        er = max(2, T//9)
        for ex, ey in [(-max(2,T//7), -max(1,T//10)), (max(2,T//7), -max(1,T//10))]:
            pygame.draw.circle(surf, C_GHOST_EYE,   (cx+ex, cy+ey), er+1)
            pygame.draw.circle(surf, C_GHOST_PUPIL, (cx+ex+1, cy+ey), max(1,er-1))
