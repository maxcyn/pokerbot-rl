from game.environment import PokerEnvironment
from game.player import Player
from agents.dqn_agent import DQNAgent
from agents.random_agent import RandomAgent
from config.config import *
import numpy as np
from game.hand_evaluator import evaluate_hand
from game.card import Card
import matplotlib.pyplot as plt

def encode_state(state):
    hand_strength = evaluate_hand(state['hand'], state['community']) / 7462.0 # Normalize hand strength
    
    community_ranks = [Card.RANKS.index(c.rank) / 12.0 for c in state['community']] # Normalize ranks
    community_ranks += [-1] * (5 - len(community_ranks))
    
    state_vector = [
        hand_strength,
        *community_ranks,
        state['chips'] / STARTING_CHIPS, # Normalize chips
        state['pot'] / (STARTING_CHIPS * 2), # Normalize pot
        state['current_bet'] / STARTING_CHIPS,
        state['opponent_chips'] / STARTING_CHIPS,
        state['opponent_bet'] / STARTING_CHIPS,
        state['position']
    ]
    return np.array(state_vector)

def train():
    p1 = Player('DQN', chips=STARTING_CHIPS)
    p2 = Player('Random', chips=STARTING_CHIPS)
    env = PokerEnvironment([p1, p2])
    agent = DQNAgent(STATE_DIM, ACTION_DIM, lr=5e-4) # Adjusted learning rate
    opponent = RandomAgent(ACTION_DIM)

    dqn_chips_history = []

    for episode in range(EPISODES):
        state = env.reset()
        done = False
        while not done:
            s = encode_state(state)
            
            if env.current_player_index == 0:
                action = agent.select_action(s)
            else:
                action = opponent.select_action(s)

            next_state, reward, done = env.step(action)
            s_ = encode_state(next_state)

            if env.current_player_index == 0:
                agent.store(s, action, reward, s_, done)
                agent.train_step(BATCH_SIZE)
            
            state = next_state
        
        dqn_chips_history.append(p1.chips)

        if episode % TARGET_UPDATE == 0:
            agent.update_target()
        
        if episode % 100 == 0:
            agent.decay_epsilon()
            print(f"Episode {episode}, DQN Chips: {p1.chips}, Epsilon: {agent.epsilon:.4f}")

    # Plotting the P/L curve
    plt.figure(figsize=(10, 5))
    plt.plot(dqn_chips_history)
    plt.title('DQN Bot P/L Over Time')
    plt.xlabel('Episode')
    plt.ylabel('Total Chips')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    train()