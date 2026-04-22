import pygame
from constants import SCREEN_W, SCREEN_H
from game_manager import GameManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
    pygame.display.set_caption('EcHo MaZe')
    GameManager(screen).run()


if __name__ == '__main__':
    main()