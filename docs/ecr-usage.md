# Usage

## Pull the Image

```bash
docker pull public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest
## apptainer
apptainer pull nephele_sars2.sif docker://public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest
```

## Download the data files

The data files have been depositied in [Zenodo](https://zenodo.org/records/21648025).  Download the zip archive SARS-CoV2.zip and unzip. Then:

```bash
mkdir dbs
mv /path/to/unzipped/SARS-CoV2 dbs/
```



## Run the Pipeline

The pipeline is invoked using command-line arguments. You need to provide a mapping file (tab-delimited) that lists your samples and their FASTQ file paths (you can substitute the name of the mapping file in these commands).

- Docker

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/dbs:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_PE \
  --mapping_file_path /path/to/mapping_file.txt \
  --primer_file_path /dbs/SARS-CoV2/artic_primer/v4_1.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

- Apptainer/Singularity

```bash
apptainer run \
    -B /path/to/input/data:/inputs -B /path/to/outputs:/outputs -B /path/to/dbs:/dbs \
    -B /path/to/tmp:/tmp \
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



## Input Data

The pipeline supports input data types:

- **ARTIC_PE**: ARTIC paired-end amplicon sequencing

- **ARTIC_SE**: ARTIC single-end amplicon sequencing  

Data should be in FASTQ format and all files should be saved in the same folder.

  

## Mapping File Format

The mapping file is a tab-delimited text file that specifies sample information.  It should be placed in the same directory as the input data. The required columns depend on the data type, and the FASTQ filenames should be prefixed with `/inputs/` to denote the path within the container:

### ARTIC_PE Mapping File

```
#SampleID	ForwardFastqFile	ReverseFastqFile
sample1	/inputs/sample1_R1.fastq.gz	/inputs/sample1_R2.fastq.gz
sample2	/inputs/sample2_R1.fastq.gz	/inputs/sample2_R2.fastq.gz
```

### ARTIC_SE Mapping File

```
#SampleID	ForwardFastqFile
sample1	/inputs/sample1.fastq.gz
sample2	/inputs/sample2.fastq.gz
```

## Required Arguments

- `--data_type`: Data type - must be `ARTIC_PE`, `ARTIC_SE`, `SGS_PE`, or `SGS_SE`
- `--mapping_file_path`: Path to tab-delimited mapping file
- `--ref_db_path`: Path to directory containing SARS-CoV-2 reference genome (will use `SARS-CoV2.fa`)
- `--snpeff_db_path`: Path to SnpEff annotation database directory
- `--primer_file_path`: Path to primer BED file (required for ARTIC_PE and ARTIC_SE data types)

## Optional Arguments

- `--outputs_dir_path`: Path to outputs directory (default: `/outputs`)
- `--get_bam_files`: Export BAM alignment files - use `True` or `False` (default: `False`)

## Primer File Options

For ARTIC_PE data type, choose from the following pre-configured primer schemes:

### ARTIC Primers

- **V1**: `/dbs/SARS-CoV2/artic_primer/v1.bed`
- **V2**: `/dbs/SARS-CoV2/artic_primer/v2.bed`
- **V3**: `/dbs/SARS-CoV2/artic_primer/v3.bed`
- **V4**: `/dbs/SARS-CoV2/artic_primer/v4.bed`
- **V4.1**: `/dbs/SARS-CoV2/artic_primer/v4_1.bed`
- **V5.0.0_400**: `/dbs/SARS-CoV2/artic_primer/v5_0_0_400.bed`
- **V5.1.0_400**: `/dbs/SARS-CoV2/artic_primer/v5_1_0_400.bed`
- **V5.2.0_400**: `/dbs/SARS-CoV2/artic_primer/v5_2_0_400.bed`
- **V5.2.0_1200**: `/dbs/SARS-CoV2/artic_primer/v5_2_0_1200.bed`
- **V5.3.2_400**: `/dbs/SARS-CoV2/artic_primer/v5_3_2_400.bed`

### NEB VarSkip Primers

- **VarSkip Short V1a**: `/dbs/SARS-CoV2/artic_primer/neb_vss1a.primer.bed`
- **VarSkip Short V2a**: `/dbs/SARS-CoV2/artic_primer/neb_vss2a.primer.bed`
- **VarSkip Long V1a**: `/dbs/SARS-CoV2/artic_primer/neb_vsl1a.primer.bed`

### IDT Primers

- **Midnight 1200**: `/dbs/SARS-CoV2/artic_primer/midnight1200.bed`

### Custom Primers

You can also provide your own primer file in BED format by mounting it into the container and specifying its path in the input JSON.

## Database Requirements

The pipeline requires the following databases to be mounted into the container:

| Database | Path | Description |
|----------|------|-------------|
| Reference Genome | `/dbs/SARS-CoV2/refs/SARS-CoV2.fa` | SARS-CoV-2 reference genome in FASTA format |
| SnpEff Database | `/dbs/SARS-CoV2/snpeff_data` | Annotation database for variant effect prediction |
| Primer Files | `/dbs/SARS-CoV2/artic_primer/*` | Pre-configured primer schemes (for ARTIC_PE) |

