from game.environment import PokerEnvironment
from game.player import Player
from agents.dqn_agent import DQNAgent
from agents.random_agent import RandomAgent
from config.config import *
import numpy as np
from game.hand_evaluator import evaluate_hand, get_preflop_strength
from game.card import Card
import matplotlib.pyplot as plt

def encode_state(state):
    hand_strength = 0
    if not state['community']:
        # We subtract from 1.0 because the network expects lower scores to be better.
        hand_strength = 1.0 - get_preflop_strength(state['hand'])
    else:
        # Post-flop: Use the Treys library (1=best, 7462=worst) and normalize.
        hand_strength = evaluate_hand(state['hand'], state['community']) / 7462.0

    community_ranks = [Card.RANKS.index(c.rank) / 12.0 for c in state['community']]
    community_ranks += [-1] * (5 - len(community_ranks))
    
    state_vector = [
        hand_strength,
        *community_ranks,
        state['chips'] / STARTING_CHIPS,
        state['pot'] / (STARTING_CHIPS * 2),
        state['current_bet'] / STARTING_CHIPS,
        state['opponent_chips'] / STARTING_CHIPS,
        state['opponent_bet'] / STARTING_CHIPS,
        state['position'],
        state['betting_round'] / 4.0 # Normalize betting round
    ]
    return np.array(state_vector)

def train():
    p1 = Player('DQN', chips=STARTING_CHIPS)
    p2 = Player('Random', chips=STARTING_CHIPS)
    env = PokerEnvironment([p1, p2])
    agent = DQNAgent(STATE_DIM, ACTION_DIM, lr=5e-4)
    opponent = RandomAgent(ACTION_DIM)

    dqn_chips_history = []

    for episode in range(EPISODES):
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
            s_ = encode_state(next_state)

            if env.current_player_index == 0:
                agent.store(s, action, reward, s_, done)
                agent.train_step(BATCH_SIZE)
            
            state = next_state
        
        dqn_chips_history.append(p1.chips)

        if episode % TARGET_UPDATE == 0:
            agent.update_target()
        
        if episode % 10 == 0:
            agent.decay_epsilon()
        
        if episode % 100 == 0:
            print(f"Episode {episode}, DQN Chips: {p1.chips}, Epsilon: {agent.epsilon:.4f}")

    # Plotting the P/L curve
    plt.figure(figsize=(10, 5))
    plt.plot(dqn_chips_history)
    plt.title('DQN Bot P/L Over Time')
    plt.xlabel('Episode')
    plt.ylabel('Total Chips')
    plt.grid(True)
    plt.show()

    # Save the trained model
    print("Training finished. Saving model...")
    agent.save("pokerbot_dqn.pth")

if __name__ == "__main__":
    train()