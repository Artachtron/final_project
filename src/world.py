import pygame as pg
import sys
import entities

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GRID_HEIGHT = 20
GRID_WIDTH = 20
BLOCK_SIZE = 20

WINDOW_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
WINDOW_WIDTH = BLOCK_SIZE * GRID_WIDTH


def main():
    global SCREEN, CLOCK
    
    pg.init()
    SCREEN = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pg.time.Clock()
    SCREEN.fill(WHITE)
    
    animal_group = pg.sprite.Group()
    animal_group.add(entities.Animal())

    while True:
        drawGrid()
        drawEntities(animal_group)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()


def drawGrid():
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pg.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pg.draw.rect(SCREEN, BLACK, rect, 1)

def drawEntities(animal_group):
    animal_group.draw(SCREEN)

if __name__ == "__main__":
    main()