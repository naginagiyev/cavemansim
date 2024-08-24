import pygame
import os
import random
from constants import *

class Wolf:
    def __init__(self):
        # Load images for different directions (left, right) and store them in a dictionary
        self.frames = {
            'left': [pygame.image.load(os.path.join(WOLF_DIR, f"left{i}.png")).convert_alpha() for i in range(1, 5)],
            'right': [pygame.image.load(os.path.join(WOLF_DIR, f"right{i}.png")).convert_alpha() for i in range(1, 5)],
        }
        self.direction = "left"  # Set the initial direction to 'left'
        self.image = self.frames[self.direction][0]  # Set the initial image based on the direction
        self.rect = self.image.get_rect()  # Get the rectangle area of the image for positioning
        self.x, self.y = 1300, 500  # Set the initial position of the wolf
        self.speed = 5  # Set the movement speed
        
        # Animation variables
        self.frame_index = 0  # Index to track the current animation frame
        self.animation_timer = 0  # Timer to control the animation speed
        self.animation_speed = 200  # Milliseconds between frames

        self.collided_with_adam = False  # Flag to check if the wolf collided with Adam
        self.vision_range = 400  # Set the vision range for the wolf

        self.direction_timer = pygame.time.get_ticks()

    def random_walk(self):
        self.speed = 2  # Default speed when Adam is not in vision range
        current_time = pygame.time.get_ticks()
        if current_time - self.direction_timer > 5000:
            self.direction = random.choice(["right", "left"])
            self.direction_timer = current_time

        if self.direction == "right":
            self.x += self.speed        
        elif self.direction == "left":
            self.x -= self.speed

    def move(self, targets):
        old_x, old_y = self.x, self.y
        
        # Find the closest target not in a safe area, or the closest target overall if all are in safe areas
        closest_target = None
        closest_distance = float('inf')
        for target in targets:
            if target.is_alive:
                distance = ((target.x - self.x) ** 2 + (target.y - self.y) ** 2) ** 0.5
                if not self.is_target_in_safe_area(target) and distance < closest_distance:
                    closest_distance = distance
                    closest_target = target
                elif self.is_target_in_safe_area(target) and distance < closest_distance and closest_target is None:
                    closest_distance = distance
                    closest_target = target

        # Logic to determine movement and animation
        if closest_target:
            if closest_distance <= self.vision_range and not self.is_target_in_safe_area(closest_target):
                self.speed = 5  # Increase speed when the target is in vision range
                diff_x = closest_target.x - self.x
                diff_y = closest_target.y - self.y

                if abs(diff_x) > abs(diff_y):
                    if diff_x > 0:
                        self.direction = "right"
                        self.x += self.speed
                    else:
                        self.direction = "left"
                        self.x -= self.speed
                else:
                    if diff_y > 0:
                        self.y += self.speed
                    else:
                        self.y -= self.speed
            else:
                self.random_walk()
        else:
            self.random_walk()

        # Update animation timer regardless of movement
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_speed:
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])
            self.image = self.frames[self.direction][self.frame_index]
            self.animation_timer = current_time

        # Ensure the wolf stays within the screen boundaries
        self.x = max(0, min(self.x, WIDTH - self.rect.width))
        self.y = max(0, min(self.y, HEIGHT - self.rect.height))

        # Update the wolf's rectangle position
        self.rect.topleft = (self.x, self.y)

        # Check for collision with targets and other objects
        for target in targets:
            if self.rect.colliderect(target.rect) and target.is_alive:
                self.collided_with_adam = True
                target.is_alive = False

        if self.rect.colliderect(LAKE_RECT) or self.rect.colliderect(FOREST_RECT) or self.rect.colliderect(CAVE_RECT):
            self.x, self.y = old_x, old_y

    def is_target_in_safe_area(self, target):
        # Check if the target is in a safe area (cave, forest)
        return (CAVE_RECT.collidepoint(target.x, target.y) or 
                FOREST_RECT.collidepoint(target.x, target.y))

    def draw(self, surface):
        # Draw the wolf on the given surface
        surface.blit(self.image, (self.x, self.y))