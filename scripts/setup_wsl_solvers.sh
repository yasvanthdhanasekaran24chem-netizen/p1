#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

echo "[1/6] apt update"
sudo apt-get update -y

echo "[2/6] base tools"
sudo apt-get install -y build-essential cmake gfortran git curl wget python3 python3-pip

echo "[3/6] install OpenFOAM (repo package)"
# For Ubuntu official repos; version can vary.
sudo apt-get install -y openfoam || true

echo "[4/6] install LAMMPS"
sudo apt-get install -y lammps || true

echo "[5/6] install Quantum ESPRESSO"
sudo apt-get install -y quantum-espresso || true

echo "[6/6] optional SU2/Code_Saturne notes"
echo "SU2 and Code_Saturne may not be available as straightforward apt packages on all Ubuntu versions."
echo "Use container/source builds if apt install fails."

echo "Done. Validate with: which simpleFoam lmp pw.x"