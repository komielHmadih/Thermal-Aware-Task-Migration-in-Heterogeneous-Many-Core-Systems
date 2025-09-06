from models.thermal import getTSPD, global_TSPD_budget, dvfs_from_budget, throughput, predict_temps
from models.migration import enumerate_migration_pairs, apply_migration
from models.core_info import PER_CORE
from config import THRESH_MIG_GAIN, NUM_CORES

# ------------------- Proposed -------------------
def run_Proposed(A, max_migs=15):
    migs = 0
    R = getTSPD(A)
    rho = global_TSPD_budget(R)
    F = dvfs_from_budget(A, rho)
    initial_throughput = throughput(A, F)

    while migs < max_migs:
        actives = [i for i,a in enumerate(A) if a==1]
        idles = [i for i,a in enumerate(A) if a==0]
        
        S = sorted(actives, key=lambda i: R[i])
        
        idle_R_estimates = []
        for d in idles:
            A_temp = A.copy()
            A_temp[d] = 1
            R_temp = getTSPD(A_temp)
            rho_temp = global_TSPD_budget(R_temp)
            idle_R_estimates.append((d, rho_temp))
        
        D = sorted(idle_R_estimates, key=lambda x: x[1], reverse=True)
        D = [d for d, _ in D]
        
        used_types = set()
        moved = False

        for s in S:
            t_s = PER_CORE[s]['type_key']
            if t_s in used_types: 
                continue
                
            for d in D:
                if PER_CORE[d]['type_key'] != t_s: 
                    continue
                    
                A2 = apply_migration(A, s, d)
                R2 = getTSPD(A2)
                rho2 = global_TSPD_budget(R2)
                
                if rho2 - rho > THRESH_MIG_GAIN:
                    A, R, rho = A2, R2, rho2
                    F = dvfs_from_budget(A, rho)
                    migs += 1
                    moved = True
                    used_types.add(t_s)
                    break
                    
            if moved: 
                break
                
        if not moved: 
            break
            
    final_throughput = throughput(A, F)
    return {
        'A': A, 
        'F': F, 
        'rho': rho, 
        'throughput': final_throughput, 
        'migrations': migs,
        'throughput_gain': final_throughput - initial_throughput
    }

# ------------------- PdOracle -------------------
def run_PdOracle(A, max_migs=15):
    migs = 0
    R = getTSPD(A)
    rho = global_TSPD_budget(R)
    F = dvfs_from_budget(A, rho)
    initial_throughput = throughput(A, F)

    while migs < max_migs:
        best_gain = 0.0
        best_pair = None
        
        for s, d in enumerate_migration_pairs(A):
            A2 = apply_migration(A, s, d)
            R2 = getTSPD(A2)
            rho2 = global_TSPD_budget(R2)
            gain = rho2 - rho
            
            if gain > best_gain:
                best_gain = gain
                best_pair = (s, d)
                
        if best_gain > THRESH_MIG_GAIN and best_pair:
            s, d = best_pair
            A = apply_migration(A, s, d)
            R = getTSPD(A)
            rho = global_TSPD_budget(R)
            F = dvfs_from_budget(A, rho)
            migs += 1
        else:
            break
            
    final_throughput = throughput(A, F)
    return {
        'A': A, 
        'F': F, 
        'rho': rho, 
        'throughput': final_throughput, 
        'migrations': migs,
        'throughput_gain': final_throughput - initial_throughput
    }

# ------------------- PerfOracle -------------------
def run_PerfOracle(A, max_migs=15):
    migs = 0
    R = getTSPD(A)
    rho = global_TSPD_budget(R)
    F = dvfs_from_budget(A, rho)
    tp = throughput(A, F)
    initial_throughput = tp

    while migs < max_migs:
        best_gain = 0.0
        best_pair = None
        
        for s, d in enumerate_migration_pairs(A):
            A2 = apply_migration(A, s, d)
            R2 = getTSPD(A2)
            rho2 = global_TSPD_budget(R2)
            F2 = dvfs_from_budget(A2, rho2)
            tp2 = throughput(A2, F2)
            gain = tp2 - tp
            
            if gain > best_gain:
                best_gain = gain
                best_pair = (s, d)
                
        if best_gain > 0 and best_pair:
            s, d = best_pair
            A = apply_migration(A, s, d)
            R = getTSPD(A)
            rho = global_TSPD_budget(R)
            F = dvfs_from_budget(A, rho)
            tp = throughput(A, F)
            migs += 1
        else:
            break
            
    return {
        'A': A, 
        'F': F, 
        'rho': rho, 
        'throughput': tp, 
        'migrations': migs,
        'throughput_gain': tp - initial_throughput
    }

# ------------------- HotCold -------------------
def run_HotCold(A, max_migs=15, temp_eps=0.5):
    migs = 0
    R = getTSPD(A)
    rho = global_TSPD_budget(R)
    F = dvfs_from_budget(A, rho)
    T = predict_temps(A, F)
    initial_throughput = throughput(A, F)
    
    visited = set()
    
    def A_key(A):
        return tuple(A)

    while migs < max_migs:
        moved = False
        types = set(PER_CORE[i]['type_key'] for i in range(NUM_CORES))
        
        for tk in types:
            act = [i for i,a in enumerate(A) if a==1 and PER_CORE[i]['type_key']==tk]
            idle = [i for i,a in enumerate(A) if a==0 and PER_CORE[i]['type_key']==tk]
            
            if not act or not idle:
                continue
                
            s = max(act, key=lambda i: T[i])
            d = min(idle, key=lambda i: T[i])
            
            if T[s] - T[d] <= temp_eps:
                continue
                
            A2 = apply_migration(A, s, d)
            
            if A_key(A2) in visited:
                continue
                
            visited.add(A_key(A2))
            A = A2
            R = getTSPD(A)
            rho = global_TSPD_budget(R)
            F = dvfs_from_budget(A, rho)
            T = predict_temps(A, F)
            migs += 1
            moved = True
            break
            
        if not moved:
            break
            
    final_throughput = throughput(A, F)
    return {
        'A': A, 
        'F': F, 
        'rho': rho, 
        'throughput': final_throughput, 
        'migrations': migs,
        'throughput_gain': final_throughput - initial_throughput
    }