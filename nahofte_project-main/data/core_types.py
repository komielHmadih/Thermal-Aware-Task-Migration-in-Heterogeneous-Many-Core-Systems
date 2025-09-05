# data/core_types.py
CORE_TYPES = ['amd_k6_iii'] * 16 + ['amd_k6_2'] * 20 + ['PowerPC'] * 16

CORE_INFO = {
    'amd_k6_2': {
        'alpha': 3.4,  # mm²
        'fmax': 3.0e9,  # Hz (3.0 GHz)
        'p_idle': 0.28,  # W
        'sum_task_time': 0.01780165,  # Sum of task execution times
        'thermal_resistance': 0.8,  # Additional thermal property
    },
    'PowerPC': {
        'alpha': 4.4,  # mm²
        'fmax': 2.0e9,  # Hz (2.0 GHz)
        'p_idle': 0.04,  # W
        'sum_task_time': 0.04166495,  # Sum of task execution times
        'thermal_resistance': 1.2,  # Additional thermal property
    },
    'amd_k6_iii': {
        'alpha': 5.6,  # mm²
        'fmax': 4.2e9,  # Hz (4.2 GHz)
        'p_idle': 0.31,  # W
        'sum_task_time': 0.01629255,  # Sum of task execution times
        'thermal_resistance': 0.6,  # Additional thermal property
    }

}