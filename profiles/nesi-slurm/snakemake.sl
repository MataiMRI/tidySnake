#!/usr/bin/env bash
#SBATCH --time=00-02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4GB
#SBATCH --output=logs/%j-%x.out
#SBATCH --error=logs/%j-%x.out

# exit on errors, undefined variables and errors in pipes
set -euo pipefail

# load environment modules
module purge 2> /dev/null
module load Apptainer/1.2.2
module load Python/3.11.6-foss-2023a #Python/3.11.6-gimkl-2022a
source ~/00_nesi_projects/uoa04671/jmcg465/venvs/snakemake-9.7/bin/activate

# parent folder for cache directories
NOBACKUPDIR="/nesi/nobackup/uoa04671"

# configure apptainer build and cache directories
export APPTAINER_CACHEDIR="$NOBACKUPDIR/$USER/apptainer_cachedir"
export APPTAINER_TMPDIR="$NOBACKUPDIR/$USER/apptainer_tmpdir"
mkdir -p "$APPTAINER_CACHEDIR" "$APPTAINER_TMPDIR"
setfacl -b "$APPTAINER_TMPDIR"  # avoid apptainer issues due to ACLs set on this folder

# run snakemake using the NeSI profile
snakemake \
    --profile profiles/nesi-slurm \
    --workflow-profile profiles/nesi-slurm \
    --config account="uoa04671" \
    "$@"