# PokerBot-RL: Deep Q-Learning Poker Agent

**PokerBot-RL** is a reinforcement learning project that trains a **Deep Q-Network (DQN)** agent to play **Heads-Up No-Limit Texas Hold'em**. The bot interacts with a custom-built poker environment and learns optimal strategies by playing against a random opponent.

The project features a custom gym-like environment, hand evaluation using `treys`, and a standard DQN architecture with Experience Replay and Target Networks.

## Features

- **Custom Poker Environment**: A complete simulation of Heads-Up No-Limit Hold'em, handling betting rounds (Pre-flop, Flop, Turn, River), blinds, and pot logic.
- **Deep Q-Network (DQN)**:
    - Implements Experience Replay (Replay Buffer).
    - Uses a Target Network for stable training.
    - Epsilon-Greedy exploration strategy with decay.
- **Hand Evaluation**:
    - **Pre-flop**: Uses a heuristic based on a simplified Chen Formula to estimate hand strength before community cards are revealed.
    - **Post-flop**: Utilizes the [treys](https://github.com/msol/treys) library for accurate combinatorial hand evaluation.
- **State Representation**: The agent perceives a 13-dimensional state vector including hand strength, community cards, chip stacks, pot odds, and opponent actions.
- **Performance Tracking**: Tracks total chips won/lost over episodes and calculates Win Rate and BB/100 (Big Blinds per 100 hands) during evaluation.

## Project Structure

```text
pokerbot-rl/
├── agents/                 # Agent implementations
│   ├── dqn_agent.py        # Deep Q-Network Agent (PyTorch)
│   └── random_agent.py     # Random Agent (Baseline opponent)
├── config/
│   └── config.py           # Hyperparameters (LR, episodes, stack sizes)
├── game/                   # Poker game logic and environment
│   ├── card.py             # Card class definition
│   ├── deck.py             # Deck shuffling and dealing logic
│   ├── environment.py      # Main Gym-like poker environment
│   ├── hand_evaluator.py   # Hand strength calc (Treys + Heuristics)
│   ├── player.py           # Player state (chips, hand, status)
│   └── table.py            # Table state (Pot, Community Cards)
├── training/
│   └── train.py            # Main training loop and state encoding
├── utils/
│   └── replay_buffer.py    # Experience Replay Buffer for DQN
├── evaluate_bot.py         # Script to evaluate the trained model
├── main.py                 # Entry point to start training
├── .gitignore              # Git ignore file
└── pokerbot_dqn.pth        # Saved model weights (generated after training)
```

## Usage

### 1. Training the Agent

To train the DQN agent against the Random Agent, run `main.py`. This initializes the environment, runs the training loop for the configured number of episodes, and saves the trained model.

Output:

- Prints training progress (chips count, epsilon value).
- Displays a plot of the agent's Profit/Loss over time.
- Saves the trained model weights to `pokerbot_dqn.pth`.

### 2. Evaluating the Agent

Once trained, you can evaluate the agent's performance using `evaluate_bot.py`.

Metrics:

- **Winrate**: Percentage of hands won against the Random Agent.
- **Avg. Chips/Hand**: Average profit per hand.
- **BB/100**: Profitability measured in Big Blinds per 100 hands.

## Configuration

You can adjust the training hyperparameters in `config/config.py`:

- `EPISODES`: Total number of training hands (default: 10000).
- `STARTING_CHIPS`: Initial stack size for players (default: 1000).
- `BATCH_SIZE`: Batch size for experience replay (default: 64).
- `TARGET_UPDATE`: Frequency (in episodes) to update the target network (default: 100).
- `STATE_DIM`: Input dimension for the neural network (13).
- `ACTION_DIM`: Number of discrete actions available (6).

## State & Action Space

### Action Space (Discrete: 6)

The agent chooses one of 6 discrete actions at every decision point:

- `0`: Fold – Forfeit the hand.
- `1`: Check/Call – Match the current bet or check if no bet exists.
- `2`: Min-Raise – Raise by the minimum allowable amount.
- `3`: Raise Half-Pot – Raise by 50% of the current pot size.
- `4`: Raise Pot – Raise by 100% of the current pot size.
- `5`: All-In – Bet all remaining chips.

### State Space (Vector: 13)

The state is encoded as a normalized vector of size 13, containing:

- **Hand Strength**: Normalized score (0–1) based on heuristics (pre-flop) or Treys evaluation (post-flop).
- **Community Cards**: 5 inputs representing the ranks of community cards (or placeholders if not yet dealt).
- **Chip Counts**: Current chips for the Agent and the Opponent (normalized by starting stack).
- **Pot Info**: Current pot size (normalized).
- **Betting Info**: Current bet amounts for the Agent and Opponent.
- **Context**: Position (Dealer/Big Blind) and the current betting round (Pre-flop, Flop, Turn, River).

