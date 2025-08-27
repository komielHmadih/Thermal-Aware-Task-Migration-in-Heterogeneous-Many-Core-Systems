import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

def create_figure4_visualizations():
    # Find the most recent results file
    result_files = glob.glob("results_policies6.csv")
    if not result_files:
        print("No results files found. Run main.py first.")
        return
    
    # Use the most recent file
    results_file = max(result_files, key=os.path.getctime)
    print(f"Using results file: {results_file}")
    
    # Load the results data
    df = pd.read_csv(results_file)
    
    # Calculate the percentage of active cores (n_active out of 52 total cores)
    df['percent_active'] = (df['n_active'] / 52) * 100
    
    # Create bins for every 10% of active cores
    df['active_bin'] = (df['percent_active'] // 10) * 10
    
    # Group by bin and policy, then calculate averages
    grouped = df.groupby(['active_bin', 'policy']).agg({
        'throughput': 'mean',
        'rho': 'mean',
        'migrations': 'mean',
        'throughput_gain': 'mean'
    }).reset_index()
    
    # Pivot the data for easier plotting
    throughput_pivot = grouped.pivot(index='active_bin', columns='policy', values='throughput')
    rho_pivot = grouped.pivot(index='active_bin', columns='policy', values='rho')
    migrations_pivot = grouped.pivot(index='active_bin', columns='policy', values='migrations')
    throughput_gain_pivot = grouped.pivot(index='active_bin', columns='policy', values='throughput_gain')
    
    # Calculate normalized gains relative to oracles
    # For TSPD-Budget Gain: Normalize relative to PdOracle
    rho_norm = rho_pivot.copy()
    for policy in ['Proposed', 'PerfOracle', 'HotCold']:
        if policy in rho_pivot.columns and 'PdOracle' in rho_pivot.columns:
            rho_norm[policy] = rho_pivot[policy] / rho_pivot['PdOracle']
    
    # For Performance Gain: Normalize relative to PerfOracle
    throughput_norm = throughput_pivot.copy()
    for policy in ['Proposed', 'PdOracle', 'HotCold']:
        if policy in throughput_pivot.columns and 'PerfOracle' in throughput_pivot.columns:
            throughput_norm[policy] = throughput_pivot[policy] / throughput_pivot['PerfOracle']
    
    # Create the plots in the style of Figure 4
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Colors for policies
    colors = {
        'Proposed': 'orange',
        'PerfOracle': 'green',
        'HotCold': 'red',
        'PdOracle': 'blue'
    }
    
    # 1. TSPD-Budget Gain (normalized to PdOracle)
    x = rho_norm.index
    width = 2.5
    
    axes[0].bar(x - width, rho_norm['Proposed'], width, color=colors['Proposed'], label='Proposed')
    axes[0].bar(x, rho_norm['PerfOracle'], width, color=colors['PerfOracle'], label='PerfOracle')
    axes[0].bar(x + width, rho_norm['HotCold'], width, color=colors['HotCold'], label='HotCold')
    axes[0].axhline(y=1, color='black', linestyle=':', linewidth=2, label='PdOracle')
    axes[0].set_title('TSPD-Budget Gain [norm]')
    axes[0].set_xlabel('Percentage of Active Cores')
    axes[0].set_ylabel('Normalized Gain')
    axes[0].set_ylim(0, 1.2)
    axes[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    axes[0].legend()
    axes[0].grid(True, axis='y')
    
    # 2. Performance Gain (normalized to PerfOracle)
    axes[1].bar(x - width, throughput_norm['Proposed'], width, color=colors['Proposed'], label='Proposed')
    axes[1].bar(x, throughput_norm['PdOracle'], width, color=colors['PdOracle'], label='PdOracle')
    axes[1].bar(x + width, throughput_norm['HotCold'], width, color=colors['HotCold'], label='HotCold')
    axes[1].axhline(y=1, color='black', linestyle=':', linewidth=2, label='PerfOracle')
    axes[1].set_title('Performance Gain [norm]')
    axes[1].set_xlabel('Percentage of Active Cores')
    axes[1].set_ylabel('Normalized Gain')
    axes[1].set_ylim(0, 2.2)
    axes[1].set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    axes[1].legend()
    axes[1].grid(True, axis='y')
    
    # 3. Number of Migrations
    x_migrations = migrations_pivot.index
    width_migrations = 1.5
    
    axes[2].bar(x_migrations - width_migrations*1.5, migrations_pivot['Proposed'], width_migrations, 
                color=colors['Proposed'], label='Proposed')
    axes[2].bar(x_migrations - width_migrations*0.5, migrations_pivot['PerfOracle'], width_migrations, 
                color=colors['PerfOracle'], label='PerfOracle')
    axes[2].bar(x_migrations + width_migrations*0.5, migrations_pivot['PdOracle'], width_migrations, 
                color=colors['PdOracle'], label='PdOracle')
    axes[2].bar(x_migrations + width_migrations*1.5, migrations_pivot['HotCold'], width_migrations, 
                color=colors['HotCold'], label='HotCold')
    axes[2].set_title('Number of Migrations')
    axes[2].set_xlabel('Percentage of Active Cores')
    axes[2].set_ylabel('Number of Migrations')
    axes[2].set_ylim(0, 16)
    axes[2].set_yticks(range(0, 16, 5))
    axes[2].legend()
    axes[2].grid(True, axis='y')
    
    plt.tight_layout()
    plt.savefig('figure4_results.png', dpi=300)
    plt.show()
    
    # Create a separate plot for absolute throughput gain
    plt.figure(figsize=(10, 6))
    x = throughput_gain_pivot.index
    
    for policy in ['Proposed', 'PdOracle', 'PerfOracle', 'HotCold']:
        if policy in throughput_gain_pivot.columns:
            plt.plot(x, throughput_gain_pivot[policy], 'o-', label=policy)
    
    plt.title('Absolute Throughput Gain')
    plt.xlabel('Percentage of Active Cores')
    plt.ylabel('Throughput Gain (iterations/second)')
    plt.legend()
    plt.grid(True)
    plt.savefig('throughput_gain.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    create_figure4_visualizations()