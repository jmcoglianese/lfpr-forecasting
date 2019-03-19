#!/bin/bash
#
#SBATCH -J python_script
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -p serial_requeue
#SBATCH --mem 32000
#SBATCH -t 0-12:00
#SBATCH -o logs/python_script_%A_%a_%j_%N.out
#SBATCH -e logs/python_script_%A_%a_%j_%N.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=coglianese@fas.harvard.edu

cd /n/home00/jcoglianese/Dropbox/Documents/Research/LFPR/Forecasting

module load gcc p7zip
module load python
source activate gpflow

date
res1=$(date +%s.%N)

FILEPATH='scripts/compare_gpy_gpflow.py'

python -u "$FILEPATH"

date

res2=$(date +%s.%N)

dt=$(echo "$res2 - $res1" | bc)
dd=$(echo "$dt/86400" | bc)
dt2=$(echo "$dt-86400*$dd" | bc)
dh=$(echo "$dt2/3600" | bc)
dt3=$(echo "$dt2-3600*$dh" | bc)
dm=$(echo "$dt3/60" | bc)
ds=$(echo "$dt3-60*$dm" | bc)

printf "Total runtime: %d:%02d:%02d:%02.4f\n" $dd $dh $dm $ds

echo 'Done'
