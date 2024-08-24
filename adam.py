import pygame
import os
import random
from constants import *

class Adam:
    def __init__(self):
        # Load images for different directions (left, right, up, down) and store them in a dictionary
        self.frames = {
            'left': [pygame.image.load(os.path.join(ADAM_DIR, f"left{i}.png")).convert_alpha() for i in range(1, 4)],
            'right': [pygame.image.load(os.path.join(ADAM_DIR, f"right{i}.png")).convert_alpha() for i in range(1, 4)],
            'up': [pygame.image.load(os.path.join(ADAM_DIR, f"up{i}.png")).convert_alpha() for i in range(1, 4)],
            'down': [pygame.image.load(os.path.join(ADAM_DIR, f"down{i}.png")).convert_alpha() for i in range(1, 4)]
        }
        self.direction = "down"  # Set the initial direction to 'down'
        self.image = self.frames[self.direction][0]  # Set the initial image based on the direction
        self.rect = self.image.get_rect()  # Get the rectangle area of the image for positioning
        self.x, self.y = 100, 100  # Set the initial position of the character
        self.speed = 6  # Set the movement speed
        self.blinking = False  # Flag to check if the character is blinking
        self.blink_start_time = 0  # Store the start time of the blink
        self.blink_duration = 150  # Set the duration of the blink in milliseconds
        self.next_blink_time = pygame.time.get_ticks() + random.randint(4000, 7000)  # Set the next blink time
        
        # Animation variables
        self.frame_index = 0  # Index to track the current animation frame
        self.animation_timer = 0  # Timer to control the animation speed
        self.animation_speed = 150  # Milliseconds between frames
        self.is_moving = False  # Flag to check if the character is moving

        # Transparency variables
        self.alpha = 255  # Initial alpha value (fully opaque)
        self.is_colliding = False  # Flag to check if the character is colliding

        # Hydration and food levels
        self.hydration = 100  # Initial hydration level
        self.food = 100  # Initial food level
        self.last_update_time = pygame.time.get_ticks()  # Time of the last update

        self.is_alive = True
        self.collided_forest = False
        self.collided_forest_timer = 0

        self.born_time = pygame.time.get_ticks()
    
    def get_born_time(self):
        return round((((pygame.time.get_ticks() - self.born_time) / 1000) / 60), 2)

    def move(self, action):
        if self.is_alive:
            self.is_moving = False  # Assume the character is not moving initially
            old_x, old_y = self.x, self.y  # Store the old position
            
            if action == 0:  # Check if the left arrow key is pressed
                self.direction = "left"  # Set direction to 'left'
                self.x -= self.speed  # Move the character left
                self.is_moving = True  # Set the moving flag to True
            if action == 1:  # Check if the right arrow key is pressed
                self.direction = "right"  # Set direction to 'right'
                self.x += self.speed  # Move the character right
                self.is_moving = True  # Set the moving flag to True
            if action == 2:  # Check if the up arrow key is pressed
                self.direction = "up"  # Set direction to 'up'
                self.y -= self.speed  # Move the character up
                self.is_moving = True  # Set the moving flag to True
            if action == 3:  # Check if the down arrow key is pressed
                self.direction = "down"  # Set direction to 'down'
                self.y += self.speed  # Move the character down
                self.is_moving = True  # Set the moving flag to True

            # Ensure the character stays within the screen boundaries
            screen_width, screen_height = WIDTH, HEIGHT  # Get the screen size
            self.x = max(0, min(self.x, screen_width - self.rect.width))  # Keep x within bounds
            self.y = max(0, min(self.y, screen_height - self.rect.height))  # Keep y within bounds

            # Update the character's rectangle position
            self.rect.topleft = (self.x, self.y)

            # Check for collisions with obstacles
            if self.rect.colliderect(CAVE_RECT):
                self.is_colliding = True  # Set colliding flag to True
            elif self.rect.colliderect(FOREST_RECT):
                self.is_colliding = True

                if self.collided_forest == False:
                    self.food = 100
                    self.collided_forest = True
                    self.collided_forest_timer = pygame.time.get_ticks()

            elif self.rect.colliderect(LAKE_RECT):
                self.x, self.y = old_x, old_y
                if self.hydration < 100:
                    self.hydration = self.hydration + 1
                    
            else:
                self.is_colliding = False  # Set colliding flag to False

            # Update the image to the current frame if moving, else reset to the first frame
            if self.is_moving:
                current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
                if current_time - self.animation_timer > self.animation_speed:  # Check if it's time to update the frame
                    self.frame_index = (self.frame_index + 1) % len(self.frames[self.direction])  # Cycle through frames
                    self.image = self.frames[self.direction][self.frame_index]  # Update the image
                    self.animation_timer = current_time  # Reset the animation timer
            else:
                self.frame_index = 0  # Reset to the first frame if not moving
                self.image = self.frames[self.direction][self.frame_index]  # Update the image

            # Adjust the alpha value based on collision state
            if self.is_colliding:
                self.alpha = max(0, self.alpha - 20)  # Reduce alpha value to make Adam more transparent
            else:
                self.alpha = min(255, self.alpha + 20)  # Increase alpha value to make Adam more opaque

            self.image.set_alpha(self.alpha)  # Apply the alpha value to the image
            
            if self.collided_forest and pygame.time.get_ticks() - self.collided_forest_timer >= 30000:
                self.collided_forest = False

    def blink(self):
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if self.blinking:
            if current_time - self.blink_start_time >= self.blink_duration:  # Check if blink duration has passed
                self.image = self.frames[self.direction][self.frame_index]  # Reset the image to the current frame
                self.blinking = False  # Set blinking to False
                self.next_blink_time = current_time + random.randint(4000, 7000)  # Set the next blink time
        elif current_time >= self.next_blink_time:  # Check if it's time to blink
            if self.direction != "up":  # Ensure the character is not facing up
                self.image = pygame.image.load(os.path.join(ADAM_DIR, f"{self.direction}_blink.png")).convert_alpha()  # Load blink image
                self.blinking = True  # Set blinking to True
                self.blink_start_time = current_time  # Set the blink start time

    def update_hydration_food(self):
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if current_time - self.last_update_time >= 1000:  # Check if 1 second has passed
            self.hydration = max(0, self.hydration - 1)  # Reduce hydration by 1, ensuring it doesn't go below 0
            self.food = max(0, self.food - 1)  # Reduce food by 1, ensuring it doesn't go below 0
            self.last_update_time = current_time  # Reset the update time

            # Check if hydration or food level reaches 0
            if self.hydration == 0 or self.food == 0:
                self.is_alive = False

    def draw(self, surface):
        # Draw the character on the given surface
        surface.blit(self.image, (self.x, self.y))

        # Draw the hydration and food bars above the character
        bar_width, bar_height = 50, 5
        bar_x, bar_y = self.x + (self.rect.width - bar_width) // 2, self.y - 20

        # Calculate the widths of the hydration and food bars based on current levels
        hydration_width = int((self.hydration / 100) * bar_width)
        food_width = int((self.food / 100) * bar_width)

        # Create surfaces for the hydration and food bars with adjusted alpha values
        hydration_bar = pygame.Surface((hydration_width, bar_height), pygame.SRCALPHA)
        food_bar = pygame.Surface((food_width, bar_height), pygame.SRCALPHA)
        hydration_bar.fill((0, 0, 255, self.alpha))  # Blue color for hydration bar
        food_bar.fill((255, 0, 0, self.alpha))  # Red color for food bar

        # Draw the hydration and food bars on the surface
        surface.blit(hydration_bar, (bar_x, bar_y))
        surface.blit(food_bar, (bar_x, bar_y + bar_height + 2))