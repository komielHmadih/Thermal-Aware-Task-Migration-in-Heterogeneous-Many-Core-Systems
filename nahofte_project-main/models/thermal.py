import math
import numpy as np
from config import T_DTM, T_AMB, NUM_CORES
from models.core_info import PER_CORE

GRID_W, GRID_H = 13, 4

def core_xy(cid):
    return (cid % GRID_W, cid // GRID_W)

def precompute_thermal_matrix():
    B = np.zeros((NUM_CORES, NUM_CORES))
    G = np.zeros(NUM_CORES)
    
    for i in range(NUM_CORES):
        xi, yi = core_xy(i)
        
        core_type = PER_CORE[i]["type_key"]
        if "amd_k6_iii" in core_type:
            B[i, i] = 0.8
        elif "amd_k6_2" in core_type:
            B[i, i] = 1.0
        else:
            B[i, i] = 1.2
        
        edge_factor = 0.3 + 0.7 * (min(xi, GRID_W-xi-1) + min(yi, GRID_H-1)) / (GRID_W + GRID_H)
        G[i] = 0.08 * edge_factor
        
        for j in range(i+1, NUM_CORES):
            xj, yj = core_xy(j)
            dist = math.hypot(xi-xj, yi-yj)
            
            core_type_i = PER_CORE[i]["type_key"]
            core_type_j = PER_CORE[j]["type_key"]
            
            base_conductance = 0.7 * math.exp(-dist/1.2)
            
            if core_type_i != core_type_j:
                base_conductance *= 0.6
            
            B[i, j] = base_conductance
            B[j, i] = base_conductance
    
    B_inv = np.linalg.inv(B)
    
    T_const = T_AMB * np.dot(B_inv, G)
    
    return B_inv, T_const

B_inv, T_const = precompute_thermal_matrix()

def getTSPD(A):
    P = np.zeros(NUM_CORES)
    for j in range(NUM_CORES):
        if A[j] == 1:  # Active core
            core_info = PER_CORE[j]
            heat_factor = 1.0 + (core_info["fmax"] / 1e9) * 0.2
            P[j] = core_info["alpha"] * heat_factor * 1.5
        else:  # Idle core
            P[j] = PER_CORE[j]["p_idle"] * 0.3
    
    T_core = np.dot(B_inv, P)
    
    T_total = T_core + T_const
    
    R = np.zeros(NUM_CORES)
    for i in range(NUM_CORES):
        if A[i] == 1:
            numerator = T_DTM - T_const[i]
            for j in range(NUM_CORES):
                if A[j] == 0:
                    numerator -= B_inv[i, j] * PER_CORE[j]["p_idle"] * 0.3
            
            denominator = 0
            for j in range(NUM_CORES):
                if A[j] == 1:
                    denominator += B_inv[i, j] * PER_CORE[j]["alpha"] * 1.5
            
            if denominator > 1e-10 and numerator > 0:
                R[i] = numerator / denominator
            else:
                R[i] = 0
        else:
            R[i] = float('inf')
    
    return R

def global_TSPD_budget(R):
    if hasattr(R, 'tolist'):
        R_list = R.tolist()
    else:
        R_list = R
        
    finite_vals = [val for val in R_list if val != float('inf') and val > 0]
    return min(finite_vals) if finite_vals else 0.0

def dvfs_from_budget(A, rho_star):
    F = [0.0] * NUM_CORES
    for i, a in enumerate(A):
        if a == 0:
            continue
            
        core_info = PER_CORE[i]
        f_max = core_info["fmax"]
        alpha = core_info["alpha"]
        
        max_power_density = min(rho_star, alpha)
        
        if alpha > 0:
            scale = (max_power_density / alpha) ** 0.4
            F[i] = scale * f_max
        else:
            F[i] = 0
    
    return F

def throughput(A, F):
    total_throughput = 0.0
    for i, a in enumerate(A):
        if a == 0:
            continue
            
        core_info = PER_CORE[i]
        f_max = core_info["fmax"]
        sum_task_time = core_info["sum_task_time"]
        
        if f_max > 0 and sum_task_time > 0 and F[i] > 0:
            scaled_execution_time = sum_task_time * (f_max / F[i])
            core_throughput = 1.0 / scaled_execution_time
            total_throughput += core_throughput
    
    return total_throughput

def predict_temps(A, F):
    P = np.zeros(NUM_CORES)
    for j in range(NUM_CORES):
        if A[j] == 0:
            P[j] = PER_CORE[j]["p_idle"] * 0.3
        else:
            core_info = PER_CORE[j]
            f_max = core_info["fmax"]
            alpha = core_info["alpha"]
            
            if f_max > 0 and F[j] > 0:
                power_density = alpha * (F[j] / f_max) ** 3.5
            else:
                power_density = 0
                
            P[j] = PER_CORE[j]["p_idle"] * 0.3 + power_density * 1.5
    
    T_core = np.dot(B_inv, P)
    T_total = T_core + T_const
    
    return T_total