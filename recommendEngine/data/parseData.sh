#!/bin/zsh

# Define input file and an array of output file names
input_file="vehiclesCleaned.csv"
output_files=("years" "makes" "models" "bodies" "doors" "extColors" "intColors" "engineCylinders" "transmissions" "mileage" "price" "engineBlocks" "engineDescs" "driveTrain" "fuels" "cityMileage" "highwayMileage" "mktClasses" "capacity")

# Check if the input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: Input file '$input_file' does not exist."
    exit 1
fi

# Loop through column numbers and corresponding output files
for i in {3..21}; do
    index=$((i - 2))                        # Index for output_files array
    output_file="${output_files[index]}.csv"  # Construct output filename
    tail -n +2 "$input_file" | csvcut -c "$i"| sort -u > "./featuresLib/$output_file"
done




