CORE_TYPES = ['amd_k6_iii'] * 16 + ['amd_k6_2'] * 20 + ['PowerPC'] * 16

CORE_INFO = {
    'amd_k6_2': {
        'alpha': 3.4,
        'fmax': 3.0e9,
        'p_idle': 0.28,
        'sum_task_time': 0.01780165,
        'thermal_resistance': 0.8,
    },
    'PowerPC': {
        'alpha': 4.4,
        'fmax': 2.0e9,
        'p_idle': 0.04,
        'sum_task_time': 0.04166495,
        'thermal_resistance': 1.2,
    },
    'amd_k6_iii': {
        'alpha': 5.6,
        'fmax': 4.2e9,
        'p_idle': 0.31,
        'sum_task_time': 0.01629255,
        'thermal_resistance': 0.6,
    }

}