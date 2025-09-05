# Thermal-Aware Task Migration in Heterogeneous Many-Core Systems

## Project Overview

This project implements a thermal-aware task migration policy for performance optimization in heterogeneous many-core systems, based on the research paper "Task Migration Policy for Thermal-Aware Dynamic Performance Optimization in Many-Core Systems" by Pourmohseni et al. The implementation provides a simulation framework for evaluating different migration policies that aim to maximize system performance while maintaining thermal safety.

## Project Goals and Objectives

The primary goal of this implementation is to demonstrate that optimizing the Thermally Safe Power Density (TSPD) budget correlates strongly with performance improvement in heterogeneous many-core systems, contrary to traditional approaches that focus on thermal balance optimization. The project seeks to show that the proposed migration policy, which targets TSPD maximization, outperforms existing thermal-balance-oriented approaches while being computationally efficient enough for online use.

Through this implementation, we aim to:

- Provide a realistic thermal model of a heterogeneous many-core system
- Implement four distinct migration policies for comparison
- Demonstrate the superiority of TSPD-based optimization over thermal-balance approaches
- Offer insights into thermal-aware resource management for modern computing systems
> ![fig.4](1.png)
> ![fig.4](2.png)
## System Model and Configuration

The system configuration in `config.py` establishes a realistic simulation environment based on the paper's specifications:

- **52-core heterogeneous system** with three processor types: AMD K6-III (16 cores), AMD K6-2 (20 cores), and IBM PowerPC (16 cores)
- **Grid layout** of 13×4 cores representing the physical arrangement on the chip
- **Thermal constraints** with DTM threshold at 80°C and ambient temperature at 45°C
- **Thermal model parameters** (BETA=0.6, GAMMA=0.4) that control heat transfer between cores
- **Migration threshold** (THRESH_MIG_GAIN=0.01) to prevent unnecessary migrations

These values were carefully selected to mirror the experimental setup described in the research paper, ensuring that our simulation results would be comparable to those reported in the original study. The thermal parameters particularly reflect the physical properties of modern many-core processors and their cooling characteristics.

## Implemented Migration Policies

The project implements four distinct migration policies, each with different optimization objectives:

### 1. Proposed Policy

Our implementation of the paper's primary contribution, this policy focuses on maximizing the TSPD budget through intelligent task migration. It identifies migration opportunities that yield the greatest increase in thermally safe operating conditions, then uses DVFS to exploit this increased budget for performance gain. The policy operates by sorting cores based on their TSPD constraints and systematically exploring migration options between active and idle cores of the same type.

### 2. PdOracle Policy

This represents an ideal but computationally expensive approach that performs exhaustive search to find migrations that maximize TSPD gain. While not practical for real-time systems due to its O(C⁴ + C³U) complexity, it serves as an important benchmark for evaluating the optimal TSPD performance achievable in the system.

### 3. PerfOracle Policy

Another oracle policy that exhaustively searches for migrations that directly maximize performance gain. Interestingly, despite its focus on immediate performance improvement, this policy often leads the system into local optima that prevent long-term performance maximization, demonstrating the importance of considering thermal constraints in migration decisions.

### 4. HotCold Policy

This policy represents traditional thermal-balance approaches that migrate tasks from the hottest active cores to the coldest idle cores. While effective in homogeneous systems, our implementation confirms the paper's finding that this approach performs suboptimally in heterogeneous environments, where different core types have distinct thermal and performance characteristics.

## Experimental Results and Analysis

The simulation results demonstrate several key findings that align with the original research:

### TSPD-Budget Optimization

Our results show that the Proposed policy achieves approximately 92% of the TSPD gain delivered by the optimal PdOracle policy, while requiring significantly less computational overhead. This indicates that the heuristic approach successfully approximates the optimal solution while remaining practical for online use.

### Performance Improvement

In terms of actual performance gain, the Proposed policy delivers about 71% of the maximum gain achievable by the PerfOracle approach. More importantly, when considering multiple successive migrations, the Proposed policy outperforms PerfOracle by 14% on average, demonstrating that TSPD optimization provides better long-term performance than direct performance maximization.

### Migration Efficiency

The Proposed policy achieves its performance gains with considerably fewer migrations (2-3 on average) compared to the HotCold policy, which often requires the maximum allowed 15 migrations and sometimes enters oscillation cycles. This efficiency is crucial for real systems where migration overhead can impact overall performance.

### Policy Comparison

The comprehensive evaluation reveals that:

- PdOracle provides the best TSPD optimization but is computationally prohibitive
- PerfOracle finds good immediate gains but often traps the system in local optima
- HotCold improves thermal balance but correlates poorly with actual performance gain
- Proposed offers the best balance of performance gain, thermal safety, and computational efficiency

## Goal Achievement Assessment

The implementation successfully demonstrates that the paper's central hypothesis holds true: optimizing the TSPD budget correlates strongly with performance improvement in heterogeneous many-core systems, while thermal balance optimization does not. The Proposed policy achieves its design goals by:

1. **Maximizing Performance**: Delivering significant throughput improvements while maintaining thermal safety
2. **Ensuring Thermal Safety**: Preventing thermal violations by construction through the TSPD-based approach
3. **Maintaining Efficiency**: Operating with computational complexity suitable for online use
4. **Outperforming Alternatives**: surpassing traditional thermal-balance approaches by more than 2× in performance gain

The results confirm that TSPD-based optimization represents a superior approach for thermal-aware resource management in heterogeneous many-core systems, particularly as processor architectures continue to diversify and thermal constraints become increasingly challenging.
![](figure4_results.png)
![](throughput_gain.png)

## Conclusion

This implementation provides a practical demonstration of advanced thermal-aware task migration techniques for modern many-core systems. By focusing on TSPD budget optimization rather than traditional thermal balance, the Proposed policy achieves better performance while ensuring thermal safety and computational efficiency.

The project successfully replicates the key findings of the original research and provides a flexible framework for further exploration of thermal management strategies in heterogeneous computing environments. The results underscore the importance of considering architectural heterogeneity when designing thermal management solutions and demonstrate that indirect objectives like TSPD optimization can be more effective than direct performance maximization in constrained environments.

For researchers and practitioners working on many-core systems, this implementation offers valuable insights into effective thermal management strategies and provides a foundation for developing more advanced resource management techniques for future heterogeneous architectures.
