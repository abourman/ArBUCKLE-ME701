# ME701-ArBUCKLE
ArBUCKLE is a wrapper for Garfield++, an open source tool for simulating gas-filled radiation detectors.

Run
```bash
bash setupGarfieldEnv.sh
```
to build a conda enviroment with the necessary packages (ROOT, mpi4py, cmake) and install Garfield++ from source. The Garfield++ installation path is 
is contained in the conda environment folder. Environment activation and deactivation scripts are appended to add and remove Garfield++ evironment variables, respectively.

Parallelization is built in with MPI. To specify the number of processes, use the MPI flag -np:
```bash
arbuckle -np 1 Input.txt
```
