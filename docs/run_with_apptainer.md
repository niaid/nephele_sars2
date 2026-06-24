# Run with apptainer

1. Create a `nephele_sars2` directory and enter the directory. And, within `nephele_sars2` directory, create inputs, outputs, and dbs directories.
```
mkdir nephele_sars2
cd nephele_sars2

mkdir -p inputs
mkdir -p outputs
mkdir -p dbs
mkdir -p tmp
```

2. Put the mapping file, and .fastq.gz files within `$(pwd)/inputs` directory. For running the image directly, the mapping file has to be tab delimited csv, the name of the sample id field has to be #SampleID, and the file names in the csv has to have input directory as prefix, such as, /inputs/22057_S2_R1_subsample.fastq.gz. Put the dbs within the dbs directory.

3. From within the previously created `nephele_sars2` directory, pull image.
```
apptainer pull nephele_sars2.sif docker://public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest
```

4. From within the previously created `nephele_sars2` directory, run image.
```
apptainer run \
    -B $(pwd)/inputs:/inputs -B $(pwd)/outputs:/outputs -B $(pwd)/dbs:/dbs \
    -B $(pwd)/tmp:/tmp \
    --contain --cleanenv --pwd /pipeline \
    --writable-tmpfs \
    nephele_sars2.sif \
    --data_type ARTIC_PE \
    --ref_db_path /dbs/SARS-CoV2/refs \
    --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
    --get_bam_files True \
    --primer_file_path /dbs/SARS-CoV2/artic_primer/neb_vss1a.primer.bed \
    --mapping_file_path /inputs/mapping_file.txt \
    --outputs_dir_path /outputs
```
