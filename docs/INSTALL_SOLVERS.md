# Install Solvers (Best Open-Source Path)

For this Windows machine, the best path is:

1. Install **WSL + Ubuntu**
2. Install Linux-native solvers inside Ubuntu:
   - OpenFOAM
   - LAMMPS
   - Quantum ESPRESSO
3. (Optional) Add SU2 and Code_Saturne via source/container if apt packages are unavailable.

## Automatic scripts included

- `scripts/setup_wsl_solvers.ps1` (Windows launcher)
- `scripts/setup_wsl_solvers.sh` (Linux installer)

## Manual steps you must do

### A) Admin step (required once)
Open **PowerShell as Administrator** and run:

```powershell
wsl --install -d Ubuntu
```

Then reboot if prompted.

### B) First Ubuntu launch
Open Ubuntu from Start Menu and finish user setup.

### C) Run installer from this repo
In normal PowerShell:

```powershell
cd C:\Users\yasva\.openclaw\workspace\p1
powershell -ExecutionPolicy Bypass -File .\scripts\setup_wsl_solvers.ps1
```

### D) Verify

```powershell
wsl -d Ubuntu bash -lc "which simpleFoam; which lmp; which pw.x"
```

## Connect to this platform

After install, API backend health should report availability for relevant commands.
If needed, set env vars:

- `P1_WSL_DISTRO` (default: `Ubuntu`)
- `LAMMPS_CMD` (default: `lmp`)
- `QE_CMD` (default: `pw.x`)
- `SU2_CMD` (default: `SU2_CFD`)
- `CS_CMD` (default: `code_saturne`)
