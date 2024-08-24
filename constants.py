import pygame
import os
from math import sqrt

ASSETS_DIR = os.path.join(os.getcwd(), 'assets') 
ADAM_DIR = os.path.join(ASSETS_DIR, 'Adam')
EVE_DIR = os.path.join(ASSETS_DIR, 'Eve')
WOLF_DIR = os.path.join(ASSETS_DIR, 'Wolf')

pygame.init() 
info = pygame.display.Info()

WIDTH, HEIGHT = info.current_w, info.current_h
MAX_DISTANCE = sqrt(WIDTH**2 + HEIGHT**2)

CAVE_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "cave.png"))
FOREST_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "forest.png"))
LAKE_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "lake.png"))
GRAVE_IMAGE = pygame.image.load(os.path.join(ASSETS_DIR, "grave.png"))

BACKGROUND_IMAGE_DAY = pygame.image.load(os.path.join(ASSETS_DIR, "ground.png"))
BACKGROUND_IMAGE_NIGHT = pygame.image.load(os.path.join(ASSETS_DIR, "groundnight.png"))

CAVE_RECT = CAVE_IMAGE.get_rect(topleft=(0, 50))
FOREST_RECT = FOREST_IMAGE.get_rect(topleft=(1250, 30))
LAKE_RECT = LAKE_IMAGE.get_rect(topleft=(512, 550))