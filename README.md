# pokerbot-rl
PokerBot-RL: Deep Q-Learning Poker AgentPokerBot-RL is a reinforcement learning project that trains a Deep Q-Network (DQN) agent to play Heads-Up No-Limit Texas Hold'em. The bot interacts with a custom-built poker environment and learns optimal strategies by playing against a random opponent.

The project features a custom gym-like environment, hand evaluation using treys, and a standard DQN architecture with Experience Replay and Target Networks.

**Features**
Custom Poker Environment: A complete simulation of Heads-Up No-Limit Hold'em, handling betting rounds (Pre-flop, Flop, Turn, River), blinds, and pot logic.

Deep Q-Network (DQN):
  Implements Experience Replay (Replay Buffer).
  Uses a Target Network for stable training.
  Epsilon-Greedy exploration strategy with decay.

Hand Evaluation:
  Pre-flop: Uses a heuristic based on a simplified Chen Formula to estimate hand strength before community cards are revealed.
  Post-flop: Utilizes the treys library for accurate combinatorial hand evaluation.

State Representation: The agent perceives a 13-dimensional state vector including hand strength, community cards, chip stacks, pot odds, and opponent actions.

Performance Tracking: Tracks total chips won/lost over episodes and calculates Win Rate and BB/100 (Big Blinds per 100 hands) during evaluation.

**Project Structure**
pokerbot-rl/
├── agents/                 # Agent implementations
│   ├── dqn_agent.py        # Deep Q-Network Agent (PyTorch)
│   └── random_agent.py     # Random Agent (Baseline opponent)
├── config/
│   └── config.py           # Hyperparameters (Learning rate, episodes, stack sizes)
├── game/                   # Poker game logic and environment
│   ├── card.py             # Card class
│   ├── deck.py             # Deck shuffling and dealing
│   ├── environment.py      # Main poker environment (Gym-like interface)
│   ├── hand_evaluator.py   # Hand strength calculation (Treys + Heuristics)
│   ├── player.py           # Player state management
│   └── table.py            # Table state (Pot, Community Cards)
├── training/
│   └── train.py            # Training loop and encoding logic
├── utils/
│   └── replay_buffer.py    # Experience Replay Buffer implementation
├── evaluate_bot.py         # Script to evaluate the trained model
└── main.py                 # Entry point to start training

**Usage**
1. Training the Agent
To train the DQN agent against the Random Agent, run main.py. This will initialize the environment, run the training loop for the number of episodes specified in config.py, and save the model.

Output: Prints training progress every 100 episodes (Chips, Epsilon). Displays a plot of the agent's Profit/Loss over time. Saves the trained model weights to pokerbot_dqn.pth.

2. Evaluating the Agent

Once trained, you can evaluate the agent's performance without exploration using evaluate_bot.py.
Metrics:
Winrate: Percentage of hands won.
Avg. Chips/Hand: Average profit per hand.
BB/100: Profitability measured in Big Blinds per 100 hands.

**Configuration**
You can adjust the training hyperparameters in config/config.py:
EPISODES: Total number of training hands (default: 10,000).
STARTING_CHIPS: Initial stack size for players (default: 1000).
BATCH_SIZE: Size of the batch for experience replay (default: 64).
LR: Learning rate for the Adam optimizer (found in dqn_agent.py or config if moved).
STATE_DIM: Input dimension for the Neural Network (default: 13).
ACTION_DIM: Number of discrete actions available (Fold, Check/Call, Min-Raise, Pot-Raise, etc.).

State & Action Space
Action Space (Discrete: 6)
Fold
Check/Call
Min-Raise
Raise Half-Pot
Raise Pot
All-In

State Space (Vector: 13)
The state is encoded as a normalized vector containing:
Hand Strength: (0-1 score based on Chen formula or Treys evaluation)
Community Cards: (5 inputs representing card ranks)
Chip Counts: (Self and Opponent stack sizes)
Pot Info: (Pot size, Current Bets)
Context: (Position, Betting Round)
