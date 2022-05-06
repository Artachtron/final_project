import pygame
import sys


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GRID_HEIGHT = 20
GRID_WIDTH = 20
BLOCK_SIZE = 20

WINDOW_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
WINDOW_WIDTH = BLOCK_SIZE * GRID_WIDTH


def main():
    global SCREEN, CLOCK
    
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)

    while True:
        drawGrid()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


def drawGrid():
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(SCREEN, BLACK, rect, 1)


if __name__ == "__main__":
    main()