from game.environment import PokerEnvironment
from game.player import Player
from agents.dqn_agent import DQNAgent
from agents.random_agent import RandomAgent
from config.config import *
import numpy as np

def encode_state(state):
    # Simple encoding: hand ranks, community ranks, chips, pot
    # For real use, encode as one-hot or more features
    hand = [Card.RANKS.index(c.rank) for c in state['hand']]
    community = [Card.RANKS.index(c.rank) for c in state['community']]
    chips = [state['chips']]
    pot = [state['pot']]
    return np.array(hand + community + chips + pot + [0]*(STATE_DIM - len(hand + community + chips + pot)))

def train():
    p1 = Player('DQN')
    p2 = Player('Random')
    env = PokerEnvironment([p1, p2])
    agent = DQNAgent(STATE_DIM, ACTION_DIM)
    opponent = RandomAgent(ACTION_DIM)
    for episode in range(EPISODES):
        state = env.reset()
        done = False
        while not done:
            s = encode_state(state)
            if env.current_player == 0:
                a = agent.select_action(s)
            else:
                a = opponent.select_action(s)
            next_state, reward, done = env.step(a)
            s_ = encode_state(next_state)
            if env.current_player == 0:
                agent.store(s, a, reward, s_, done)
                agent.train_step(BATCH_SIZE)
            state = next_state
        if episode % TARGET_UPDATE == 0:
            agent.update_target()
            agent.decay_epsilon()
        if episode % 100 == 0:
            print(f"Episode {episode}, Epsilon: {agent.epsilon:.2f}")

if __name__ == "__main__":
    train()
