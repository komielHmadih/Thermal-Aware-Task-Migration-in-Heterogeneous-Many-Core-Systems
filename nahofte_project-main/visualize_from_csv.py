import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from models.thermal_model import ThermalModel
from models.core_info import PER_CORE
import ast

def load_and_process_csv(csv_file):
    """Load and process the CSV file with policy results"""
    print(f"Loading data from: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # Group by n_active and policy to get average values
    grouped = df.groupby(['n_active', 'policy']).agg({
        'throughput': 'mean',
        'rho': 'mean',
        'migrations': 'mean',
        'throughput_gain': 'mean'
    }).reset_index()
    
    return df, grouped

def visualize_policy_comparison(grouped_df):
    """Create comparison plots of different policies"""
    policies = grouped_df['policy'].unique()
    
    # Throughput comparison
    plt.figure(figsize=(12, 6))
    for policy in policies:
        policy_data = grouped_df[grouped_df['policy'] == policy]
        plt.plot(policy_data['n_active'], policy_data['throughput'], 
                 'o-', label=policy, linewidth=2, markersize=6)
    
    plt.title('Throughput Comparison by Policy')
    plt.xlabel('Number of Active Cores')
    plt.ylabel('Throughput')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('throughput_comparison.png', dpi=300)
    plt.show()
    
    # TSPD (rho) comparison
    plt.figure(figsize=(12, 6))
    for policy in policies:
        policy_data = grouped_df[grouped_df['policy'] == policy]
        plt.plot(policy_data['n_active'], policy_data['rho'], 
                 'o-', label=policy, linewidth=2, markersize=6)
    
    plt.title('TSPD (ρ) Comparison by Policy')
    plt.xlabel('Number of Active Cores')
    plt.ylabel('TSPD (ρ)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('tspd_comparison.png', dpi=300)
    plt.show()

def visualize_thermal_behavior_for_policy(thermal_model, n_active, policy_name, sample_df):
    """Visualize thermal behavior for a specific policy and active core count"""
    # Filter data for the specific policy and n_active
    policy_data = sample_df[(sample_df['policy'] == policy_name) & 
                           (sample_df['n_active'] == n_active)]
    
    if len(policy_data) == 0:
        print(f"No data found for {policy_name} with {n_active} active cores")
        return
    
    # Use the first sample
    sample = policy_data.iloc[0]
    
    # Create allocation vector (we'll simulate it based on n_active)
    # In a real implementation, you'd need to store the actual allocation vector
    A = [1] * n_active + [0] * (thermal_model.num_cores - n_active)
    
    # Create frequency vector (simplified - using average of max frequency)
    F = [0.7 * PER_CORE[i]["fmax"] for i in range(thermal_model.num_cores)]
    
    # Calculate temperatures
    T = thermal_model.calculate_temperatures(A, F)
    
    # Visualize temperature distribution
    grid = np.zeros((thermal_model.grid_h, thermal_model.grid_w))
    for i in range(thermal_model.num_cores):
        x, y = thermal_model.get_core_position(i)
        grid[y, x] = T[i]
    
    plt.figure(figsize=(14, 10))
    plt.imshow(grid, cmap='hot', interpolation='nearest')
    plt.colorbar(label='Temperature (°C)')
    plt.title(f'Temperature Distribution - {policy_name} Policy, {n_active} Active Cores\n'
              f'Throughput: {sample["throughput"]:.2f}, TSPD: {sample["rho"]:.2f}')
    
    # Annotate with core IDs and temperatures
    for i in range(thermal_model.num_cores):
        x, y = thermal_model.get_core_position(i)
        plt.text(x, y, f'{i}\n{T[i]:.1f}°C', 
                 ha='center', va='center', fontsize=6,
                 color='white' if T[i] > (thermal_model.T_dtm + thermal_model.T_amb)/2 else 'black')
    
    plt.savefig(f'temperature_{policy_name}_{n_active}_active.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print summary information
    print(f"Policy: {policy_name}")
    print(f"Active cores: {n_active}")
    print(f"Throughput: {sample['throughput']:.2f}")
    print(f"TSPD (ρ): {sample['rho']:.2f}")
    print(f"Migrations: {sample['migrations']}")
    print(f"Throughput gain: {sample['throughput_gain']:.2f}")
    print(f"Maximum temperature: {max(T):.2f}°C")
    print(f"Minimum temperature: {min(T):.2f}°C")
    print(f"Average temperature: {np.mean(T):.2f}°C")

def main():
    # Initialize thermal model
    thermal_model = ThermalModel()
    
    # Load and process CSV data
    csv_file = 'results_policies7.csv'  
    sample_df, grouped_df = load_and_process_csv(csv_file)
    
    # Create policy comparison plots
    visualize_policy_comparison(grouped_df)
    
    # Let user choose which policy and n_active to visualize
    print("Available policies:", grouped_df['policy'].unique())
    print("Available active core counts:", sorted(grouped_df['n_active'].unique()))
    
    # You can modify these values to visualize different scenarios
    policy_to_visualize = 'Proposed'  # Change to 'PdOracle', 'PerfOracle', or 'HotCold'
    n_active_to_visualize = 20  # Change to any value from 2 to 51
    
    # Visualize thermal behavior for the selected policy and active core count
    visualize_thermal_behavior_for_policy(thermal_model, n_active_to_visualize, 
                                         policy_to_visualize, sample_df)
    
    # Additional visualization: Show thermal relationships for a specific core
    core_id = 16
    relationships = thermal_model.get_core_relationships(core_id)
    
    print(f"\nThermal relationships for core {core_id}:")
    print("Core ID | Conductance | Position")
    print("-" * 40)
    for rel in relationships[:10]:
        print(f"{rel['core_id']:6} | {rel['conductance']:10.4f} | {rel['position']}")

if __name__ == "__main__":
    main()