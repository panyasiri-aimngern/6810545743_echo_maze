import pygame
from constants import *


class Player:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.px = float(x * TILE)
        self.py = float(y * TILE)
        self.dx = 0
        self.dy = 0
        self.moving = False
        self.progress = 0.0
        self.steps = 0
        self.path: list[dict] = [{'x': x, 'y': y, 't': 0.0}]

    # Movement 
    def try_move(self, dx: int, dy: int, maze, elapsed: float):
        if self.moving:
            return
        nx, ny = self.x + dx, self.y + dy
        if maze.is_wall(nx, ny):
            return
        self.moving = True
        self.dx = dx
        self.dy = dy
        self.progress = 0.0
        self.path.append({'x': nx, 'y': ny, 't': elapsed})

    def try_break(self, keys, maze) -> bool:
        dirs = [
            (keys[pygame.K_UP]    or keys[pygame.K_w], 0, -1),
            (keys[pygame.K_DOWN]  or keys[pygame.K_s], 0,  1),
            (keys[pygame.K_LEFT]  or keys[pygame.K_a], -1, 0),
            (keys[pygame.K_RIGHT] or keys[pygame.K_d],  1, 0),
        ]
        for held, dx, dy in dirs:
            if held:
                tx, ty = self.x + dx, self.y + dy
                if maze.is_breakable(tx, ty):
                    maze.break_wall(tx, ty)
                    return True
                break
        return False

    def update(self, elapsed: float) -> tuple[int, int] | None:
        if not self.moving:
            return None
        self.progress += SPEED / TILE
        if self.progress >= 1.0:
            self.x += self.dx
            self.y += self.dy
            self.px = float(self.x * TILE)
            self.py = float(self.y * TILE)
            self.moving = False
            self.progress = 0.0
            self.steps += 1
            return (self.x, self.y)
        else:
            self.px = (self.x + self.dx * self.progress) * TILE
            self.py = (self.y + self.dy * self.progress) * TILE
            return None

    # Draw 
    def draw(self, surf: pygame.Surface, offset_y: int):
        T = TILE
        cx = int(self.px) + T // 2
        cy = int(self.py) + T // 2 + offset_y

        # glow
        glow = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*C_PLAYER, 38), (T//2, T//2), T//2)
        surf.blit(glow, (int(self.px), int(self.py) + offset_y))

        # body
        pygame.draw.rect(surf, C_PLAYER,
                         (int(self.px)+5, int(self.py)+5+offset_y, T-10, T-10),
                         border_radius=5)

        # eyes
        pygame.draw.rect(surf, C_WHITE,
                         (int(self.px)+9, int(self.py)+10+offset_y, 5, 5))
        pygame.draw.rect(surf, C_WHITE,
                         (int(self.px)+T-14, int(self.py)+10+offset_y, 5, 5))

    def draw_scaled(self, surf: pygame.Surface, mx: int, my: int, tile: int):
        T  = tile
        px = mx + int(self.px * T / TILE)
        py = my + int(self.py * T / TILE)
        cx = px + T//2; cy = py + T//2
        pad = max(3, T//7)
        glow = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*C_PLAYER, 38), (T//2, T//2), T//2)
        surf.blit(glow, (px, py))
        pygame.draw.rect(surf, C_PLAYER, (px+pad, py+pad, T-pad*2, T-pad*2), border_radius=max(2,T//7))
        ew = max(2, T//7); eh = max(2, T//7)
        ep = max(3, T//4)
        pygame.draw.rect(surf, C_WHITE, (px+ep,       py+ep+2,     ew, eh))
        pygame.draw.rect(surf, C_WHITE, (px+T-ep-ew,  py+ep+2,     ew, eh))
