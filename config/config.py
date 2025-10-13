STATE_DIM = 13  # hand strength (1) + community cards (5) + player chips (1) + pot size (1) + current bet (1) + opponent chips (1) + opponent bet (1) + position (1)
ACTION_DIM = 6  # fold, call/check, raise min, raise half-pot, raise pot
EPISODES = 10000
BATCH_SIZE = 64
TARGET_UPDATE = 100
STARTING_CHIPS = 1000