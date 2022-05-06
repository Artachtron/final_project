import pygame as pg

class Animal(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load(r"H:\UoL\Semester 5\Code\final_project\assets\Fichier 1.png").convert()
        self.rect = self.image.get_rect()
        
