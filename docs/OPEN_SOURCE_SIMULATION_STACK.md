# Open-Source Simulation Stack (Recommended)

## CFD / continuum

1. **OpenFOAM**
   - General-purpose CFD, multiphase, reacting flow, turbulence
2. **SU2**
   - Strong for aerodynamics + adjoint optimization
3. **Code_Saturne**
   - Industrial CFD (robust RANS/LES workflows)
4. **Elmer / FEniCS (PDE/multiphysics side)**
   - Flexible PDE/finite element workflows

## Atomic / molecular / quantum

1. **LAMMPS**
   - Classical molecular dynamics, materials workflows
2. **GROMACS**
   - Fast MD (bio/soft matter focused)
3. **Quantum ESPRESSO**
   - DFT / electronic-structure calculations
4. **CP2K**
   - DFT + MD hybrid and large-scale atomistic simulation
5. **ASE (Atomic Simulation Environment)**
   - Python orchestration layer across atomistic backends

## Platform strategy for this repository

- Use adapters to unify all engines under one cognitive API.
- Keep solver-specific complexity in backend adapters.
- Keep planner/objective/constraint/memory UI-agnostic.

## Why not build a CFD/DFT solver from scratch?

Building a production-grade solver from scratch is possible but very high effort and risk.
A better path is:
- reuse validated open-source solvers,
- build a strong cognitive orchestration + UI + optimization layer (this repo’s mission).
