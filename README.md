# 🧠 Reinforcement Learning Game with Deep Q-Networks 🎮
Welcome to the Reinforcement Learning Game developed using Deep Q-Networks (DQN)! This project demonstrates the application of reinforcement learning in a game environment where the player must survive by managing hunger and hydration levels while avoiding threats.

## 📝 Game Description
In this game, the player has two key survival metrics: **hunger** and **hydration**. The player must hunt for food to reduce hunger and drink water from a lake to stay hydrated. The game also features a **day-night cycle**, adding an additional layer of complexity:
- **Daytime**: The player can explore, hunt, and drink water.
- **Nighttime**: A dangerous wolf spawns with the objective of hunting down the player.

### 🛡️ The Cave
The player can find refuge in a cave. If the player stays in the cave for 5 seconds, it simulates sleep, and the game cycle shifts back to daytime, offering a brief respite from the dangers of the night.

## 🛠️ Installation and Setup
To run the game locally, follow these steps:

1. **Clone the repository:**
   ```bash git clone https://github.com/naginagiyev/cavemansim.git
2. **Open the cloned folder, then open terminal and download needed libraries using following command:**
   ```bash pip install torch, pygame
3. **Run the code using following command:**
   ```bash python agent.py

There is not a model ready to use. So, it will first train. Good results can be seen after 1.5-2 hours of training.
