import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

def create_figure4_visualizations():
    result_files = glob.glob("results_policies8.csv")
    if not result_files:
        print("No results files found. Run main.py first.")
        return
    
    results_file = max(result_files, key=os.path.getctime)
    print(f"Using results file: {results_file}")
    
    df = pd.read_csv(results_file)
    
    df['percent_active'] = (df['n_active'] / 52) * 100
    
    df['active_bin'] = (df['percent_active'] // 10) * 10
    
    grouped = df.groupby(['active_bin', 'policy']).agg({
        'throughput': 'mean',
        'rho': 'mean',
        'migrations': 'mean',
        'throughput_gain': 'mean'
    }).reset_index()
    
    throughput_pivot = grouped.pivot(index='active_bin', columns='policy', values='throughput')
    rho_pivot = grouped.pivot(index='active_bin', columns='policy', values='rho')
    migrations_pivot = grouped.pivot(index='active_bin', columns='policy', values='migrations')
    throughput_gain_pivot = grouped.pivot(index='active_bin', columns='policy', values='throughput_gain')
    

    rho_norm = rho_pivot.copy()
    for policy in ['Proposed', 'PerfOracle', 'HotCold']:
        if policy in rho_pivot.columns and 'PdOracle' in rho_pivot.columns:
            rho_norm[policy] = rho_pivot[policy] / rho_pivot['PdOracle']
    
    throughput_norm = throughput_pivot.copy()
    for policy in ['Proposed', 'PdOracle', 'HotCold']:
        if policy in throughput_pivot.columns and 'PerfOracle' in throughput_pivot.columns:
            throughput_norm[policy] = throughput_pivot[policy] / throughput_pivot['PerfOracle']
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # Changed from 3 to 2 subplots
    
    colors = {
        'Proposed': 'orange',
        'PerfOracle': 'green',
        'HotCold': 'red',
        'PdOracle': 'blue'
    }
    
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
    
    x_migrations = migrations_pivot.index
    width_migrations = 1.5
    
    axes[1].bar(x_migrations - width_migrations*1.5, migrations_pivot['Proposed'], width_migrations, 
                color=colors['Proposed'], label='Proposed')
    axes[1].bar(x_migrations - width_migrations*0.5, migrations_pivot['PerfOracle'], width_migrations, 
                color=colors['PerfOracle'], label='PerfOracle')
    axes[1].bar(x_migrations + width_migrations*0.5, migrations_pivot['PdOracle'], width_migrations, 
                color=colors['PdOracle'], label='PdOracle')
    axes[1].bar(x_migrations + width_migrations*1.5, migrations_pivot['HotCold'], width_migrations, 
                color=colors['HotCold'], label='HotCold')
    axes[1].set_title('Number of Migrations')
    axes[1].set_xlabel('Percentage of Active Cores')
    axes[1].set_ylabel('Number of Migrations')
    axes[1].set_ylim(0, 16)
    axes[1].set_yticks(range(0, 16, 5))
    axes[1].legend()
    axes[1].grid(True, axis='y')
    
    plt.tight_layout()
    plt.savefig('figure4_results.png', dpi=300)
    plt.show()
    
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