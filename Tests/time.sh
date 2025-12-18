#!/usr/bin/env bash

# Fail fast
set -euo pipefail

EXECUTABLE="arbuckle"
INPUT_FILE="Input.txt"
OUTPUT_FILE="mpi_time_study.txt"

# Header
echo "# MPI scaling study" > "$OUTPUT_FILE"
echo "# Command: $EXECUTABLE -np N $INPUT_FILE" >> "$OUTPUT_FILE"
echo "# Columns: NPROCS REAL_TIME_SECONDS" >> "$OUTPUT_FILE"

# Loop over process counts
for (( np=1; np<=14; np++ )); do
    echo "Running with $np process(es)..."

    # Temporarily disable 'set -e' for this command
    set +e
    REAL_TIME=$( { time $EXECUTABLE --use-hwthread-cpus -np "$np" "$INPUT_FILE" >/dev/null; } 2>&1 )
    status=$?
    set -e

    if [ $status -ne 0 ]; then
        echo "Warning: $EXECUTABLE exited with code $status" >&2
    fi

    echo "$np $REAL_TIME" >> "$OUTPUT_FILE"
done

echo "Study complete. Results written to $OUTPUT_FILE"
