# Local run

### Pull image
Pull the image from outside of VPN (use the hash of the latest image or of the image version you want to pull or use the latest tag); VPN can cause certificate problem while pulling the image from ECR registry public domain.
```
docker pull public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest
docker image tag public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest nephele_sars2_container
```

### Run image
1. Enter the repo root folder, and do some setup.
```
mkdir nephele_sars2_local_test
cd nephele_sars2_local_test
mkdir -p inputs
mkdir -p outputs
mkdir -p dbs
```

2. Put the mapping file, and .fastq.gz files within `$(pwd)/inputs` directory. For running the image directly, the mapping file has to be tab delimited csv, and the file names in the csv has to have input directory as prefix, such as, /inputs/example-A_S27_L001_R1_001.fastq.gz .

3. Pull db files.
```
aws s3 cp s3://nephele-db-files/SARS-CoV2/refs/ dbs/SARS-CoV2/refs/ --recursive --profile nephele-workspace-mgmt-readonly
aws s3 cp s3://nephele-db-files/SARS-CoV2/SARS-CoV2/snpeff_data/ dbs/SARS-CoV2/snpeff_data/ --recursive --profile nephele-workspace-mgmt-readonly
aws s3 cp s3://nephele-db-files/SARS-CoV2/artic_primer/v1.bed dbs/SARS-CoV2/artic_primer/ --profile nephele-workspace-mgmt-readonly
```
Note: The doc will be updated with appropriate profile role instead of nephele-workspace-mgmt-readonly.

4. Make some update to the project code.

5. Clear the outputs directory if it is subsequent runs.
```
rm -r outputs/*
```

6. Run the image with the project code mounted in the volume `-v $(pwd)/../nephele_sars2:/pipeline`.
```
docker run --rm -it -v $(pwd)/../nephele_sars2:/pipeline -v $(pwd)/inputs:/inputs -v $(pwd)/outputs:/outputs -v $(pwd)/dbs:/dbs nephele_sars2_container --mapping_file_path /inputs/mapping_file.csv --data_type=ARTIC_PE --primer_file_path=/dbs/SARS-CoV2/artic_primer/v1.bed --ref_db_path=/dbs/SARS-CoV2/refs --snpeff_db_path=/dbs/SARS-CoV2/snpeff_data
```

To get help about the pipeline
```
docker run nephele_sars2_container --help
```