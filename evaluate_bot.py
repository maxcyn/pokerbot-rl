import torch
from game.environment import PokerEnvironment
from game.player import Player
from agents.dqn_agent import DQNAgent
from agents.random_agent import RandomAgent
from config.config import *
from training.train import encode_state
import numpy as np

# --- Configuration ---
EVALUATION_EPISODES = 20000
BIG_BLIND = 20

def evaluate():
    print(f"Starting evaluation... Running {EVALUATION_EPISODES} hands.")
    
    # Setup players
    p1 = Player('DQN', chips=STARTING_CHIPS)
    p2 = Player('Random', chips=STARTING_CHIPS)
    
    # Setup environment
    env = PokerEnvironment([p1, p2])

    # 1. Load your trained DQN Agent
    agent = DQNAgent(STATE_DIM, ACTION_DIM)
    try:
        agent.load("pokerbot_dqn.pth")
    except FileNotFoundError:
        print("Error: 'pokerbot_dqn.pth' not found.")
        print("Please run main.py to train and save the model first.")
        return

    # 2. Set Epsilon to 0 (Exploitation mode)
    agent.epsilon = 0.0

    # 3. Setup the opponent
    opponent = RandomAgent(ACTION_DIM)

    # 4. Setup tracking
    total_wins = 0
    total_reward = 0 # This is the total chip profit/loss

    for episode in range(EVALUATION_EPISODES):
        if p1.chips <= 0 or p2.chips <= 0:
            p1.reset_chips(STARTING_CHIPS)
            p2.reset_chips(STARTING_CHIPS)

        state = env.reset()
        done = False
        
        while not done:
            s = encode_state(state)
            
            if env.current_player_index == 0:
                action = agent.select_action(s)
            else:
                action = opponent.select_action(s)

            next_state, reward, done = env.step(action)
            
            state = next_state
        
        # Hand is done, record the final reward (net chip change)
        if reward > 0:
            total_wins += 1
        total_reward += reward

        if (episode + 1) % 1000 == 0:
            print(f"Completed episode {episode + 1}/{EVALUATION_EPISODES}")

    # --- Print Final Results ---
    print("\n" + "="*30)
    print("--- Evaluation Finished ---")
    print("="*30)

    # --- Calculate Metrics ---
    winrate = (total_wins / EVALUATION_EPISODES)
    avg_chips_per_hand = total_reward / EVALUATION_EPISODES
    
    # Calculate BB/100
    total_bb_won = total_reward / BIG_BLIND
    bb_per_100 = (total_bb_won / EVALUATION_EPISODES) * 100

    print(f"Total Hands Played: {EVALUATION_EPISODES}")
    print(f"Hand Winrate:       {winrate:.2%}")
    print(f"Avg. Chips/Hand:    {avg_chips_per_hand:.2f}")
    print(f"Profitability:      {bb_per_100:.2f} BB/100 hands")
    print("="*30)

if __name__ == "__main__":
    evaluate()