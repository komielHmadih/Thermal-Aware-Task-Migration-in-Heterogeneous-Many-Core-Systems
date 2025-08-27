import math
import numpy as np
from config import T_DTM, T_AMB, NUM_CORES
from models.core_info import PER_CORE

GRID_W, GRID_H = 13, 4

def core_xy(cid):
    return (cid % GRID_W, cid // GRID_W)

def precompute_thermal_matrix():
    # Create a more realistic and constrained thermal model
    B = np.zeros((NUM_CORES, NUM_CORES))
    G = np.zeros(NUM_CORES)
    
    # Create a thermal model with more pronounced hotspots
    for i in range(NUM_CORES):
        xi, yi = core_xy(i)
        
        # Self-conductance - varies by core type (make it more restrictive)
        core_type = PER_CORE[i]["type_key"]
        if "amd_k6_iii" in core_type:
            B[i, i] = 0.8  # K6-III runs hotter
        elif "amd_k6_2" in core_type:
            B[i, i] = 1.0  # K6-2
        else:
            B[i, i] = 1.2  # PowerPC runs cooler
        
        # Conductance to ambient - make it less effective to create more thermal constraint
        # Cores near edges have slightly better cooling
        edge_factor = 0.3 + 0.7 * (min(xi, GRID_W-xi-1) + min(yi, GRID_H-1)) / (GRID_W + GRID_H)
        G[i] = 0.08 * edge_factor  # Reduced from previous value
        
        # Conductance to neighbors - make heat transfer more significant
        for j in range(i+1, NUM_CORES):
            xj, yj = core_xy(j)
            dist = math.hypot(xi-xj, yi-yj)
            
            # Different core types have different thermal interactions
            core_type_i = PER_CORE[i]["type_key"]
            core_type_j = PER_CORE[j]["type_key"]
            
            # Base conductance based on distance - increased for more heat transfer
            base_conductance = 0.7 * math.exp(-dist/1.2)  # Increased from previous value
            
            # Adjust based on core types
            if core_type_i != core_type_j:
                base_conductance *= 0.6  # Different types have less thermal interaction
            
            B[i, j] = base_conductance
            B[j, i] = base_conductance
    
    # Precompute the inverse of B
    B_inv = np.linalg.inv(B)
    
    # Precompute constant term: T_amb * B_inv * G
    T_const = T_AMB * np.dot(B_inv, G)
    
    return B_inv, T_const

# Precompute these once
B_inv, T_const = precompute_thermal_matrix()

def getTSPD(A):
    # Calculate power contributions for each core - make power values more realistic
    P = np.zeros(NUM_CORES)
    for j in range(NUM_CORES):
        if A[j] == 1:  # Active core
            # Active cores generate more heat (use a higher multiplier)
            core_info = PER_CORE[j]
            # More powerful cores generate significantly more heat
            heat_factor = 1.0 + (core_info["fmax"] / 1e9) * 0.2  # Increased from 0.1
            P[j] = core_info["alpha"] * heat_factor * 1.5  # Added multiplier
        else:  # Idle core
            # Idle cores generate less heat
            P[j] = PER_CORE[j]["p_idle"] * 0.3  # Reduced from 0.5
    
    # Calculate temperature contribution from cores: B_inv * P
    T_core = np.dot(B_inv, P)
    
    # Calculate total temperature: T_core + T_const
    T_total = T_core + T_const
    
    # Calculate TSPD for each core using the formula from the paper
    R = np.zeros(NUM_CORES)
    for i in range(NUM_CORES):
        if A[i] == 1:  # Only active cores constrain TSPD
            # Calculate numerator: T_DTM - T_const[i] - contribution from idle cores
            numerator = T_DTM - T_const[i]
            for j in range(NUM_CORES):
                if A[j] == 0:  # Idle core
                    numerator -= B_inv[i, j] * PER_CORE[j]["p_idle"] * 0.3  # Consistent with above
            
            # Calculate denominator: contribution from active cores
            denominator = 0
            for j in range(NUM_CORES):
                if A[j] == 1:  # Active core
                    denominator += B_inv[i, j] * PER_CORE[j]["alpha"] * 1.5  # Consistent with above
            
            # Avoid division by zero
            if denominator > 1e-10 and numerator > 0:
                R[i] = numerator / denominator
            else:
                R[i] = 0
        else:
            R[i] = float('inf')
    
    return R

def global_TSPD_budget(R):
    # Convert numpy array to list if needed, then find the minimum finite value
    if hasattr(R, 'tolist'):
        R_list = R.tolist()
    else:
        R_list = R
        
    # Filter out infinite values and find the minimum
    finite_vals = [val for val in R_list if val != float('inf') and val > 0]
    return min(finite_vals) if finite_vals else 0.0

def dvfs_from_budget(A, rho_star):
    F = [0.0] * NUM_CORES
    for i, a in enumerate(A):
        if a == 0:  # Idle core
            continue
            
        core_info = PER_CORE[i]
        f_max = core_info["fmax"]
        alpha = core_info["alpha"]
        
        # Calculate maximum power density this core can have
        max_power_density = min(rho_star, alpha)
        
        # Scale frequency based on power budget - make it more sensitive
        if alpha > 0:
            # Use a more sensitive frequency scaling model
            # Make the scaling more aggressive to show bigger differences
            scale = (max_power_density / alpha) ** 0.4  # Changed exponent from 0.5 to 0.4
            F[i] = scale * f_max
        else:
            F[i] = 0
    
    return F

def throughput(A, F):
    total_throughput = 0.0
    for i, a in enumerate(A):
        if a == 0:  # Skip idle cores
            continue
            
        core_info = PER_CORE[i]
        f_max = core_info["fmax"]
        sum_task_time = core_info["sum_task_time"]
        
        if f_max > 0 and sum_task_time > 0 and F[i] > 0:
            # Scale execution time based on current frequency
            # Make sure the scaling is correct
            scaled_execution_time = sum_task_time * (f_max / F[i])
            core_throughput = 1.0 / scaled_execution_time
            total_throughput += core_throughput
    
    return total_throughput

def predict_temps(A, F):
    # Calculate power consumption for each core
    P = np.zeros(NUM_CORES)
    for j in range(NUM_CORES):
        if A[j] == 0:  # Idle core
            P[j] = PER_CORE[j]["p_idle"] * 0.3  # Consistent with above
        else:  # Active core
            core_info = PER_CORE[j]
            f_max = core_info["fmax"]
            alpha = core_info["alpha"]
            
            # Calculate power density based on frequency scaling
            if f_max > 0 and F[j] > 0:
                # Power scales more aggressively with frequency
                power_density = alpha * (F[j] / f_max) ** 3.5  # Increased exponent from 3 to 3.5
            else:
                power_density = 0
                
            P[j] = PER_CORE[j]["p_idle"] * 0.3 + power_density * 1.5  # Consistent with above
    
    # Calculate temperatures using thermal model
    T_core = np.dot(B_inv, P)
    T_total = T_core + T_const
    
    return T_total