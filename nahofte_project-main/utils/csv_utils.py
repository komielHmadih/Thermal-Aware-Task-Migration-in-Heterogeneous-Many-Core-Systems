import csv

def save_results_csv(filename, results):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['n_active', 'sample_id', 'policy', 'throughput', 'rho', 'migrations', 'throughput_gain']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)