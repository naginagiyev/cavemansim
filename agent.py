import torch 
import random
import numpy as np
from collections import deque
from game import Game
from constants import *
from math import sqrt
from model import Linear_QNet, QTrainer

MAX_MEMORY = 1000000
BATCH_SIZE = 10000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0.1
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(18, 128, 128, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
        self.hit_top = False
        self.hit_bottom = True
        self.limit = self.epsilon + 0.1
    
    def update_epsilon(self):
        if self.limit == 0.9:
            self.epsilon = 0.95
        else:
            if not self.hit_top and self.hit_bottom:
                self.epsilon += 0.01
                if self.epsilon >= 0.95:
                    self.epsilon = 0.95
                    self.hit_top = True
                    self.hit_bottom = False

            elif self.hit_top and not self.hit_bottom:
                self.epsilon -= 0.01
                if self.epsilon <= self.limit:
                    self.epsilon = self.limit
                    self.hit_top = False
                    self.hit_bottom = True
                    self.limit += 0.1
        
    def get_state(self, game):
        adam_x = game.adam.x / WIDTH
        adam_y = game.adam.y / HEIGHT
        adam_hydration = game.adam.hydration / 100
        adam_food = game.adam.food / 100
        
        distance_to_cave = sqrt((game.adam.x - 128)**2 + (game.adam.y - 106)**2) / MAX_DISTANCE
        distance_to_forest = sqrt((game.adam.x - 1379)**2 + (game.adam.y - 147)**2) / MAX_DISTANCE
        distance_to_lake = sqrt((game.adam.x - 768)**2 + (game.adam.y - 686)**2) / MAX_DISTANCE

        if game.wolf is not None:
            distance_to_wolf = sqrt((game.adam.x - game.wolf.x)**2 + (game.adam.y - game.wolf.y)**2) / MAX_DISTANCE
            state = [
                adam_x, adam_y, adam_hydration, adam_food,
                game.wolf.x / WIDTH, game.wolf.y / HEIGHT, distance_to_wolf / MAX_DISTANCE,
                128 / WIDTH, 106 / HEIGHT, distance_to_cave / MAX_DISTANCE,
                1379 / WIDTH, 147 / HEIGHT, distance_to_forest / MAX_DISTANCE,
                768 / WIDTH, 686 / HEIGHT, distance_to_lake / MAX_DISTANCE,
                game.get_time_to_next_cycle() / 60,
                game.adam.is_alive
            ]
        else:
            state = [
                adam_x, adam_y, adam_hydration, adam_food,
                1, 1, 1,
                128 / WIDTH, 106 / HEIGHT, distance_to_cave / MAX_DISTANCE,
                1379 / WIDTH, 147 / HEIGHT, distance_to_forest / MAX_DISTANCE,
                768 / WIDTH, 686 / HEIGHT, distance_to_lake / MAX_DISTANCE,
                game.get_time_to_next_cycle() / 60,
                game.adam.is_alive
            ]

        return np.round(np.array(state, dtype=float), 2)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        loss = self.trainer.train_step(states, actions, rewards, next_states, dones)
        return loss

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        if random.random() > self.epsilon:
            move = random.randint(0, 3)

        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
        return move
    
def train():
    best_score = 0
    agent = Agent()
    game = Game()
    live_times = []

    while True:
        state_old = agent.get_state(game)
        move = agent.get_action(state_old)

        reward, done, live_score = game.play_episode(move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, move, reward, state_new, done)
        agent.remember(state_old, move, reward, state_new, done)  

        if done:
            agent.update_epsilon()
            game.reset()
            agent.n_games += 1
            game.episode_count += 1 
            loss = agent.train_long_memory()

            live_times.append(live_score)
            if len(live_times) == 6:
                live_times.pop(0)
            average_live_time = sum(live_times) / len(live_times)

            print(f"Episode : {agent.n_games}, Reward : {round(reward, 2)}, Epsilon : {round(agent.epsilon, 2)}, Loss : {round(loss, 2)}, Lived : {live_score} mins, Average Live : {round(average_live_time, 2)}, Best Score : {best_score}")
            if  live_score > best_score:
                best_score = live_score
                game.best_score = best_score
                agent.model.save()

if __name__ == "__main__":  
    train()