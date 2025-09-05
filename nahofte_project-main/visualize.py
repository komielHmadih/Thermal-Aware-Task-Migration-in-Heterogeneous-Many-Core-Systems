import numpy as np
import matplotlib.pyplot as plt
from models.thermal_model import thermal_model
from models.core_info import PER_CORE

def visualize_thermal_matrix():
    """Visualize the thermal conductance matrix"""
    B = thermal_model.get_thermal_matrix()
    
    plt.figure(figsize=(10, 8))
    plt.imshow(B, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Thermal Conductance')
    plt.title('Thermal Conductance Matrix B')
    plt.xlabel('Core ID')
    plt.ylabel('Core ID')
    plt.savefig('thermal_matrix.png')
    plt.show()

def visualize_core_temperatures(A, F):
    """Visualize temperatures across all cores"""
    T = thermal_model.calculate_temperatures(A, F)
    
    # Reshape to grid
    grid = np.zeros((thermal_model.grid_h, thermal_model.grid_w))
    for i in range(thermal_model.num_cores):
        x, y = thermal_model.get_core_position(i)
        grid[y, x] = T[i]
    
    plt.figure(figsize=(12, 8))
    plt.imshow(grid, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Temperature (°C)')
    plt.title('Core Temperatures')
    
    # Annotate with core IDs and temperatures
    for i in range(thermal_model.num_cores):
        x, y = thermal_model.get_core_position(i)
        plt.text(x, y, f'{i}\n{T[i]:.1f}°C', 
                 ha='center', va='center', 
                 color='white' if T[i] > (thermal_model.T_dtm + thermal_model.T_amb)/2 else 'black')
    
    plt.savefig('core_temperatures.png')
    plt.show()

def visualize_core_relationships(core_id):
    """Visualize the thermal relationships for a specific core"""
    relationships = thermal_model.get_core_relationships(core_id)
    
    print(f"Thermal relationships for core {core_id}:")
    print("Core ID | Conductance | Position")
    print("-" * 40)
    for rel in relationships[:10]:  # Show top 10 relationships
        print(f"{rel['core_id']:6} | {rel['conductance']:10.4f} | {rel['position']}")
    
    # Create a visualization of the core and its relationships
    plt.figure(figsize=(10, 8))
    
    # Plot all cores
    all_x = []
    all_y = []
    for i in range(thermal_model.num_cores):
        x, y = thermal_model.get_core_position(i)
        all_x.append(x)
        all_y.append(y)
        if i == core_id:
            plt.plot(x, y, 'ro', markersize=15, label=f'Core {core_id}')
        else:
            plt.plot(x, y, 'bo', markersize=8, alpha=0.5)
    
    # Plot relationships
    for rel in relationships[:5]:  # Show top 5 strongest relationships
        x, y = rel['position']
        plt.plot([core_id % thermal_model.grid_w, x], 
                 [core_id // thermal_model.grid_w, y], 
                 'r-', alpha=0.7, linewidth=rel['conductance']*10)
        plt.text(x, y, f"{rel['core_id']}\n{rel['conductance']:.3f}", 
                 ha='center', va='center', fontsize=8)
    
    plt.title(f'Thermal Relationships for Core {core_id}')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'core_{core_id}_relationships.png')
    plt.show()

if __name__ == "__main__":
    # Example usage
    visualize_thermal_matrix()
    
    # Create a sample allocation and frequency vector
    A = [1 if i % 4 == 0 else 0 for i in range(thermal_model.num_cores)]
    F = [0.5 * PER_CORE[i]["fmax"] for i in range(thermal_model.num_cores)]
    
    visualize_core_temperatures(A, F)
    visualize_core_relationships(16)  # Show relationships for core 16