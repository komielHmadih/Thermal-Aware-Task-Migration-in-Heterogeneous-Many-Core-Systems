from data.core_types import CORE_TYPES, CORE_INFO
from config import NUM_CORES

PER_CORE = []
for cid in range(NUM_CORES):
    core_type = CORE_TYPES[cid]
    info = CORE_INFO[core_type]
    PER_CORE.append({
        "id": cid,
        "type_key": core_type,
        "fmax": info['fmax'],
        "alpha": info['alpha'],
        "p_idle": info['p_idle'],
        "sum_task_time": info['sum_task_time']
    })

def get_core_type(core_id):
    return PER_CORE[core_id]["type_key"]

def same_type(i, j):
    return get_core_type(i) == get_core_type(j)