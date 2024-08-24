import pygame
import random
from adam import Adam
from wolf import Wolf
from constants import *
from math import sqrt

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game of Life")
        self.background = BACKGROUND_IMAGE_DAY
        self.current_time = pygame.time.get_ticks()
        self.current_background = "day"
        self.cycle_duration = 60000  

        self.episode_count = 0
        self.best_score = 0
    
        self.adam = Adam()
        self.wolf = None
        self.running = True
        self.time_in_cave = None

    def reset(self):
        self.adam = Adam()
        self.wolf = None

        if self.current_background == "night":
            self.background = BACKGROUND_IMAGE_NIGHT
            self.wolf = Wolf()
        else:
            self.background = BACKGROUND_IMAGE_DAY
            self.current_background = "day"

        self.current_time = pygame.time.get_ticks()

    def calculate_distance(self, x1, y1, x2, y2):
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def get_time_to_next_cycle(self):
        elapsed_time = pygame.time.get_ticks() - self.current_time
        time_to_next_cycle = max(0, self.cycle_duration - elapsed_time)
        return time_to_next_cycle / 1000

    def play_episode(self, action):
        reward = 0
        clock = pygame.time.Clock()

        # Check if it's time to switch between day and night
        if pygame.time.get_ticks() - self.current_time > self.cycle_duration:  
            if self.current_background == "day":
                self.background = BACKGROUND_IMAGE_NIGHT
                self.current_background = "night"
                self.wolf = Wolf()  # Spawn wolf immediately at night
            else:
                self.background = BACKGROUND_IMAGE_DAY
                self.current_background = "day"
                self.wolf = None  # Remove wolf during the day
            self.current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        if self.adam.is_alive:
            # Calculate previous distances for Adam
            dist_forest_prev_adam = self.calculate_distance(self.adam.x, self.adam.y, 1379, 147)
            dist_lake_prev_adam = self.calculate_distance(self.adam.x, self.adam.y, 768, 686)
            dist_cave_prev_adam = self.calculate_distance(self.adam.x, self.adam.y, 128, 106)
            dist_wolf_prev_adam = self.calculate_distance(self.adam.x, self.adam.y, self.wolf.x, self.wolf.y) if self.wolf else float('inf')
            
            # Calculate previous food levels for Adam
            prev_food_adam = self.adam.food
            prev_hydration_adam = self.adam.hydration

            # Update Adam's position
            self.adam.move(action)
            self.adam.blink()
            self.adam.update_hydration_food()

            # Calculate current distances
            dist_forest_curr_adam = self.calculate_distance(self.adam.x, self.adam.y, 1379, 147)
            dist_lake_curr_adam = self.calculate_distance(self.adam.x, self.adam.y, 768, 686)
            dist_cave_curr_adam = self.calculate_distance(self.adam.x, self.adam.y, 128, 106)
            dist_wolf_curr_adam = self.calculate_distance(self.adam.x, self.adam.y, self.wolf.x, self.wolf.y) if self.wolf else float('inf')
            
            # Rewards for maintaining needs
            if self.adam.food > prev_food_adam:
                reward += (self.adam.food - prev_food_adam) * ((100 - prev_food_adam) / 100)
            if self.adam.hydration > prev_hydration_adam:
                reward += (self.adam.hydration - prev_hydration_adam) * ((100 - prev_hydration_adam) / 100)

            # Reward for moving closer to forest, lake, and cave, but scale down as agent gets closer
            reward += max(0, (dist_forest_prev_adam - dist_forest_curr_adam) * ((100 - self.adam.food) / 100) * ((MAX_DISTANCE - dist_forest_curr_adam) / MAX_DISTANCE))
            reward += max(0, (dist_lake_prev_adam - dist_lake_curr_adam) * ((100 - self.adam.hydration) / 100) * ((MAX_DISTANCE - dist_lake_curr_adam) / MAX_DISTANCE))

            if self.current_background == "night":
                if dist_cave_curr_adam < dist_cave_prev_adam:
                    reward += (dist_cave_prev_adam - dist_cave_curr_adam)
                else:
                    reward -= (dist_cave_curr_adam - dist_cave_prev_adam)

            if self.wolf:
                if dist_wolf_curr_adam < dist_wolf_prev_adam:
                    penalty_scale = max(0, ((MAX_DISTANCE - dist_wolf_curr_adam) / MAX_DISTANCE))
                    reward -= max(0, (dist_wolf_prev_adam - dist_wolf_curr_adam) * penalty_scale)

            # Adjust survival reward over time
            reward += self.adam.get_born_time()

            # Little penalty for getting close to the Wolf's spawn point
            distance_to_wolf_spawn = self.calculate_distance(self.adam.x, self.adam.y, 1300, 500)
            reward -= ((MAX_DISTANCE - distance_to_wolf_spawn) / MAX_DISTANCE) * 0.2                            

            if self.adam.rect.colliderect(CAVE_RECT) and self.current_background == "night":
                if self.cave_enter_time is None: 
                    self.cave_enter_time = pygame.time.get_ticks() 
                else:
                    time_in_cave = (pygame.time.get_ticks() - self.cave_enter_time) / 1000.0
                    reward += time_in_cave * 0.5
                    if time_in_cave >= 5:
                        self.background = BACKGROUND_IMAGE_DAY
                        self.current_background = "day"
                        self.wolf = None
                        self.cave_enter_time = None  
                        self.current_time = pygame.time.get_ticks()
                        reward = reward + 10
                        print("Player sleeped. Cycle changed!")
            else:
                self.cave_enter_time = None

        if self.current_background == "night" and self.wolf:
            self.wolf.move([self.adam])

        # Drawing elements on the screen
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(CAVE_IMAGE, CAVE_RECT)
        self.screen.blit(FOREST_IMAGE, FOREST_RECT)
        self.screen.blit(LAKE_IMAGE, LAKE_RECT)

        game_over = False

        if not self.adam.is_alive:
            game_over = True
            self.screen.blit(GRAVE_IMAGE, (self.adam.x, self.adam.y))
            reward -= 20 / self.adam.get_born_time()
            return reward, game_over, self.adam.get_born_time()
        
        else:
            self.adam.draw(self.screen)

        if self.current_background == "night" and self.wolf:
            self.wolf.draw(self.screen)
        
        font = pygame.font.Font(None, 24)
        epsiode_text = font.render(f"Epsiode : {self.episode_count}", True, (255, 255, 255)) 
        score_text = font.render(f"Best Score : {self.best_score} mins", True, (255, 255, 255)) 
        self.screen.blit(epsiode_text, (50, 780))
        self.screen.blit(score_text, (50, 810))

        pygame.display.flip()
        clock.tick(60)
        return reward, game_over, self.adam.get_born_time()