import torch
import torch.nn as nn
import torch.optim as optim
import random
from utils.replay_buffer import ReplayBuffer

# Neural network approximating Q-values: input = state, output = Q-values for each action
class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 128)  # First hidden layer with 128 neurons
        self.fc2 = nn.Linear(128, 128)        # Second hidden layer
        self.fc3 = nn.Linear(128, action_dim) # Output layer: one Q-value per action

    def forward(self, x):
        x = torch.relu(self.fc1(x))  # Apply ReLU activation on first hidden layer
        x = torch.relu(self.fc2(x))  # ReLU on second hidden layer
        return self.fc3(x)            # Raw Q-values output (no activation)

class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3):
        self.model = DQN(state_dim, action_dim)            # Main Q-network
        self.target = DQN(state_dim, action_dim)           # Target network for stable learning
        self.target.load_state_dict(self.model.state_dict())  # Synchronize target to main initially
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)  # Adam optimizer for training
        self.memory = ReplayBuffer(10000)                   # Experience replay buffer with capacity 10k
        self.gamma = 0.99                                   # Discount factor for future rewards
        self.epsilon = 1.0                                  # Initial epsilon for epsilon-greedy exploration
        self.epsilon_min = 0.1                              # Minimum epsilon (minimum exploration)
        self.epsilon_decay = 0.995                           # Exponential decay rate of epsilon
        self.action_dim = action_dim                         # Number of discrete actions
    
    # Choose action based on epsilon-greedy policy
    def select_action(self, state):
        if random.random() < self.epsilon:                  # With probability epsilon, explore
            return random.randint(0, self.action_dim - 1)   # Random action
        state = torch.FloatTensor(state).unsqueeze(0)       # Convert state to tensor and add batch dim
        with torch.no_grad():
            q = self.model(state)                            # Predict Q-values from main network
        return q.argmax().item()                             # Choose action with highest Q-value

    # Store experience tuple in replay buffer
    def store(self, s, a, r, s_, done):                     # state, action, reward, next_state, done
        self.memory.push(s, a, r, s_, done)

    # Perform one training step of Q-learning using replay buffer samples
    def train_step(self, batch_size=32):
        if len(self.memory) < batch_size:
            return                                          # Not enough samples yet
        
        s, a, r, s_, d = self.memory.sample(batch_size)    # Sample random mini-batch
        s = torch.FloatTensor(s)                            # Convert batch to tensors
        a = torch.LongTensor(a)
        r = torch.FloatTensor(r)
        s_ = torch.FloatTensor(s_)
        d = torch.FloatTensor(d)
        
        q = self.model(s).gather(1, a.unsqueeze(1)).squeeze(1)  # Q-values for taken actions
        q_next = self.target(s_).max(1)[0]                      # Max Q-value from target network for next states
        q_target = r + self.gamma * q_next * (1 - d)            # Compute target Q-values (Bellman eq.)
        
        loss = nn.MSELoss()(q, q_target.detach())                # Mean squared error loss between Q and target
        
        self.optimizer.zero_grad()
        loss.backward()                                          # Backpropagation of loss
        self.optimizer.step()                                    # Update network weights

    # Update target network to match main network parameters (periodically)
    def update_target(self):
        self.target.load_state_dict(self.model.state_dict())

    # Decay epsilon after each episode to reduce exploration over time
    def decay_epsilon(self):
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)