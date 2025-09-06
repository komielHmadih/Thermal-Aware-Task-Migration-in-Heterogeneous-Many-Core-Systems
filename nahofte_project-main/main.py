import copy
import random
from models.policies import run_Proposed, run_PdOracle, run_PerfOracle, run_HotCold
from utils.csv_utils import save_results_csv
from config import NUM_CORES, NUM_ITERATION
from datetime import datetime
import time

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"results_policies_{timestamp}.csv"

results_all = []
start_time = time.time()

for n_active in range(2, NUM_CORES):
    progress = (n_active-1) / (NUM_CORES-2) * 100
    elapsed_time = time.time() - start_time
    estimated_total_time = elapsed_time / (progress/100) if progress > 0 else 0
    remaining_time = estimated_total_time - elapsed_time
    
    print(f"Running {n_active} active cores ({progress:.1f}% complete)")
    print(f"Elapsed: {elapsed_time/60:.1f} min, Estimated remaining: {remaining_time/60:.1f} min")
    
    for sample_id in range(NUM_ITERATION):
        print(f"  Sample {sample_id+1}/{NUM_ITERATION}")
        
        try:
            active_cores = random.sample(range(NUM_CORES), n_active)
            A0 = [0] * NUM_CORES
            
            for i in active_cores:
                A0[i] = 1

            policies = {
                "Proposed": run_Proposed,
                "PdOracle": run_PdOracle,
                "PerfOracle": run_PerfOracle,
                "HotCold": run_HotCold
            }
            
            for policy_name, policy_func in policies.items():
                try:
                    data = policy_func(copy.deepcopy(A0[:]))
                    
                    results_all.append({
                        "n_active": n_active,
                        "sample_id": sample_id,
                        "policy": policy_name,
                        "throughput": data["throughput"],
                        "rho": data["rho"],
                        "migrations": data["migrations"],
                        "throughput_gain": data["throughput_gain"]
                    })
                    
                    print(f"    {policy_name}: {data['throughput_gain']:.4f} gain, {data['migrations']} migs, rho: {data['rho']:.4f}")
                    
                except Exception as e:
                    print(f"Error running {policy_name} for n_active={n_active}, sample_id={sample_id}: {e}")
                    continue
                
        except Exception as e:
            print(f"Error running policies for n_active={n_active}, sample_id={sample_id}: {e}")
            continue

save_results_csv(OUTPUT_FILE, results_all)

total_time = time.time() - start_time
print(f" Done. Results saved to {OUTPUT_FILE} with {len(results_all)} rows.")
print(f"Total execution time: {total_time/60:.1f} minutes")