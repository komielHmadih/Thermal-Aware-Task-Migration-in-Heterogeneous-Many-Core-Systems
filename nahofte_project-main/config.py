NUM_CORES = 52
NUM_TASKS_PER_CORE = 18
NUM_ITERATION = 3

GRID_W, GRID_H = 13, 4

T_DTM = 80.0      # DTM threshold from paper
T_AMB = 45.0      # Ambient temperature from paper

# Thermal model parameters - updated to match paper better
BETA = 0.6        # Reduced for more realistic heat transfer
GAMMA = 0.4       # Adjusted conductance
THRESH_MIG_GAIN = 0.01  # Increased threshold to prevent unnecessary migrations