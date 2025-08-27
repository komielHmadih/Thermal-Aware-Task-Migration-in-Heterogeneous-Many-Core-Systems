core_types = ['k6-3']*16 + ['k6-2']*20 + ['powerpc']*16

task = {
    "cores": {
        "amd_k6_2": {
            "processor": "AMD K6-2E+",
            "frequency": 3,
            "alpha": 3.4,
            "idle_power": 0.28,
            "C_eff": 1.23,
            "V": 1.2,
            "p_dynamic": 5.3,
            "p_static": 1.3,
            "tasks": [{"id":i,"task_time":t,"task_power":2.8} for i,t in enumerate([6e-06, 1.15e-05, 0.000365, 1.7e-06, 1.25e-06, 0.0055, 3.85e-05, 4.6e-05,0.000335, 0.005, 0.0032, 0.000195, 2.4e-06, 1.8e-06, 1.4e-05, 3.35e-05,0.00055, 0.0025])]
        },
        "PowerPC": {
            "processor": "IBM PowerPC 405GP",
            "frequency": 2,
            "alpha": 4.4,
            "idle_power": 0.04,
            "C_eff": 0.29,
            "V": 1.4,
            "p_dynamic": 1.1,
            "p_static": 0.3,
            "tasks": [{"id":i,"task_time":t,"task_power":0.4} for i,t in enumerate([4.6e-06, 9e-06, 0.00046, 1.2e-06, 9e-07, 0.00405, 2.05e-05, 4.25e-05,0.000285, 0.0035, 0.00155, 0.000185, 1.6e-06, 1.65e-06, 1.45e-05, 3.85e-05,0.009, 0.0225])]
        },
        "amd_k6_iii": {
            "processor": "AMD K6-IIIE+",
            "frequency": 4.2,
            "alpha": 5.6,
            "idle_power": 0.31,
            "C_eff": 1.73,
            "V": 1.1,
            "p_dynamic": 8.8,
            "p_static": 2.2,
            "tasks": [{"id":i,"task_time":t,"task_power":3.1} for i,t in enumerate([5.5e-06, 1.05e-05, 0.00033, 1.55e-06, 1.15e-06, 0.005, 3.5e-05, 4.2e-05,0.000305, 0.00465, 0.0029, 0.000175, 2.2e-06, 1.65e-06, 1.3e-05, 3e-05,0.00049, 0.0023])]
        }
    }
}

TYPE_KEY = {'k6-2':'amd_k6_2', 'k6-3':'amd_k6_iii','powerpc':'PowerPC'}
