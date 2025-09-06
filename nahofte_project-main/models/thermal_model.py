import numpy as np
from config import NUM_CORES, GRID_W, GRID_H, T_DTM, T_AMB
from models.core_info import PER_CORE

class ThermalModel:
    def __init__(self):
        self.grid_w = GRID_W
        self.grid_h = GRID_H
        self.num_cores = NUM_CORES
        self.T_dtm = T_DTM
        self.T_amb = T_AMB
        
        self.B = np.zeros((self.num_cores, self.num_cores))
        self.G = np.zeros(self.num_cores)
        self.B_inv = None
        self.T_const = None
        
        self.initialize_thermal_matrices()
    
    def initialize_thermal_matrices(self):
        for i in range(self.num_cores):
            x_i, y_i = self.get_core_position(i)
            
            core_type = PER_CORE[i]["type_key"]
            if "amd_k6_iii" in core_type:
                self.B[i, i] = 0.8
            elif "amd_k6_2" in core_type:
                self.B[i, i] = 1.0
            else:
                self.B[i, i] = 1.2
            
            edge_factor = 0.3 + 0.7 * (min(x_i, self.grid_w-1-x_i) + min(y_i, self.grid_h-1)) / (self.grid_w + self.grid_h)
            self.G[i] = 0.08 * edge_factor  # Reduced from previous value
            
            for j in range(i+1, self.num_cores):
                x_j, y_j = self.get_core_position(j)
                dist = np.sqrt((x_i-x_j)**2 + (y_i-y_j)**2)
                
                core_type_i = PER_CORE[i]["type_key"]
                core_type_j = PER_CORE[j]["type_key"]
                
                base_conductance = 0.7 * np.exp(-dist/1.2)
                
                if core_type_i != core_type_j:
                    base_conductance *= 0.6
                
                self.B[i, j] = base_conductance
                self.B[j, i] = base_conductance
                self.B[i, i] += base_conductance
                self.B[j, j] += base_conductance
        
        self.B_inv = np.linalg.inv(self.B)
        self.T_const = self.T_amb * np.dot(self.B_inv, self.G)
    
    def get_core_position(self, core_id):
        x = core_id % self.grid_w
        y = core_id // self.grid_w
        return x, y
    
    def calculate_temperatures(self, A, F):
        P = np.zeros(self.num_cores)
        for i in range(self.num_cores):
            if A[i] == 1:
                core_info = PER_CORE[i]
                heat_factor = 1.0 + (core_info["fmax"] / 1e9) * 0.2
                power_density = core_info["alpha"] * heat_factor * 1.5
                P[i] = power_density
            else:  # Idle core
                P[i] = PER_CORE[i]["p_idle"] * 0.3
        
        T_core = np.dot(self.B_inv, P)
        T_total = T_core + self.T_const
        
        return T_total
    
    def calculate_tspd(self, A):
        F_min = [0.1 * PER_CORE[i]["fmax"] for i in range(self.num_cores)]
        T = self.calculate_temperatures(A, F_min)
        
        R = np.zeros(self.num_cores)
        for i in range(self.num_cores):
            if A[i] == 1:
                thermal_headroom = self.T_dtm - T[i]
                R[i] = thermal_headroom / PER_CORE[i]["alpha"] if thermal_headroom > 0 else 0
            else:
                R[i] = float('inf')
        
        return min(R)
    
    def get_thermal_matrix(self):
        return self.B
    
    def get_core_relationships(self, core_id):
        relationships = []
        for other_id in range(self.num_cores):
            if other_id != core_id:
                conductance = abs(self.B[core_id, other_id])
                if conductance > 0.01:
                    relationships.append({
                        'core_id': other_id,
                        'conductance': conductance,
                        'position': self.get_core_position(other_id)
                    })
        
        relationships.sort(key=lambda x: x['conductance'], reverse=True)
        return relationships

thermal_model = ThermalModel()