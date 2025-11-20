# Usage

## Pull the Image

```bash
docker pull public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest
```

## Run the Pipeline

The pipeline is invoked using command-line arguments. You need to provide a mapping file (tab-delimited) that lists your samples and their FASTQ file paths.

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/dbs:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_PE \
  --mapping_file_path /inputs/mapping.txt \
  --primer_file_path /dbs/SARS-CoV2/artic_primer/v4_1.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

## Data Types

The pipeline supports three data types:

## Data Types

The pipeline supports three data types:

- **ARTIC_PE**: ARTIC paired-end amplicon sequencing
- **ARTIC_SE**: ARTIC single-end amplicon sequencing  
- **SGS_PE**: Shotgun paired-end sequencing
- **SGS_SE**: Shotgun single-end sequencing

## Mapping File Format

The mapping file is a tab-delimited text file that specifies sample information. The required columns depend on the data type:

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

### SGS_PE Mapping File

```
#SampleID	ForwardFastqFile_A	ReverseFastqFile_A	ForwardFastqFile_B	ReverseFastqFile_B	PrimerFile_A	PrimerFile_B
sample1	/inputs/s1_A_R1.fastq.gz	/inputs/s1_A_R2.fastq.gz	/inputs/s1_B_R1.fastq.gz	/inputs/s1_B_R2.fastq.gz	/inputs/primer_A.fa	/inputs/primer_B.fa
```

### SGS_SE Mapping File

```
#SampleID	ForwardFastqFile_A	ForwardFastqFile_B	PrimerFile_A	PrimerFile_B
sample1	/inputs/s1_A.fastq.gz	/inputs/s1_B.fastq.gz	/inputs/primer_A.fa	/inputs/primer_B.fa
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

## Example Commands

### ARTIC V4.1 Analysis

Create a mapping file `mapping.txt`:

```
#SampleID	ForwardFastqFile	ReverseFastqFile
sample1	/inputs/sample1_R1.fastq.gz	/inputs/sample1_R2.fastq.gz
sample2	/inputs/sample2_R1.fastq.gz	/inputs/sample2_R2.fastq.gz
```

Run the pipeline:

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_PE \
  --mapping_file_path /inputs/mapping.txt \
  --primer_file_path /dbs/SARS-CoV2/artic_primer/v4_1.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

### ARTIC V5.3.2 with BAM Export

Create a mapping file `mapping.txt`:

```
#SampleID	ForwardFastqFile	ReverseFastqFile
sample1	/inputs/sample1_R1.fastq.gz	/inputs/sample1_R2.fastq.gz
```

Run the pipeline:

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_PE \
  --mapping_file_path /inputs/mapping.txt \
  --primer_file_path /dbs/SARS-CoV2/artic_primer/v5_3_2_400.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs \
  --get_bam_files True
```

### NEB VarSkip Short V2a Analysis

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_PE \
  --mapping_file_path /inputs/mapping.txt \
  --primer_file_path /dbs/SARS-CoV2/artic_primer/neb_vss2a.primer.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

### ARTIC Single-End Analysis

Create a mapping file `mapping.txt`:

```
#SampleID	ForwardFastqFile
sample1	/inputs/sample1.fastq.gz
sample2	/inputs/sample2.fastq.gz
```

Run the pipeline:

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_SE \
  --mapping_file_path /inputs/mapping.txt \
  --primer_file_path /dbs/SARS-CoV2/artic_primer/v4_1.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```
  --outputs_dir_path /outputs
```

### Custom Primer Analysis

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type ARTIC_PE \
  --mapping_file_path /inputs/mapping.txt \
  --primer_file_path /inputs/custom_primers.bed \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

### Shotgun Paired-End Analysis

Create a mapping file `mapping.txt`:

```
#SampleID	ForwardFastqFile_A	ReverseFastqFile_A	ForwardFastqFile_B	ReverseFastqFile_B	PrimerFile_A	PrimerFile_B
sample1	/inputs/s1_A_R1.fastq.gz	/inputs/s1_A_R2.fastq.gz	/inputs/s1_B_R1.fastq.gz	/inputs/s1_B_R2.fastq.gz	/inputs/primer_A.fa	/inputs/primer_B.fa
```

Run the pipeline:

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type SGS_PE \
  --mapping_file_path /inputs/mapping.txt \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

### Shotgun Single-End Analysis

Create a mapping file `mapping.txt`:

```
#SampleID	ForwardFastqFile_A	ForwardFastqFile_B	PrimerFile_A	PrimerFile_B
sample1	/inputs/s1_A.fastq.gz	/inputs/s1_B.fastq.gz	/inputs/primer_A.fa	/inputs/primer_B.fa
sample2	/inputs/s2_A.fastq.gz	/inputs/s2_B.fastq.gz	/inputs/primer_A.fa	/inputs/primer_B.fa
```

Run the pipeline:

```bash
docker run -v /path/to/data:/inputs \
  -v /path/to/outputs:/outputs \
  -v /path/to/databases:/dbs \
  public.ecr.aws/niaid_nephele/pipeline/nephele_sars2:latest \
  --data_type SGS_SE \
  --mapping_file_path /inputs/mapping.txt \
  --ref_db_path /dbs/SARS-CoV2/refs \
  --snpeff_db_path /dbs/SARS-CoV2/snpeff_data \
  --outputs_dir_path /outputs
```

## Output Files

The pipeline generates comprehensive SARS-CoV-2 analysis results in the `/outputs` directory:

### Consensus Sequences

- **consensus_sequences/**: Assembled consensus genomes in FASTA format
  - One FASTA file per sample
  - High-quality consensus sequences

### Variant Calls

- **variants/**: Variant call files (VCF)
  - Annotated variants with genomic coordinates
  - Allele frequencies and quality scores
  - SnpEff functional effect predictions

### Quality Metrics

- **metrics/**: Quality control and coverage statistics
  - Per-sample coverage reports
  - Read mapping statistics
  - Quality score distributions
  - Depth of coverage metrics

### Alignment Files (Optional)

- **bam_files/**: BAM alignment files (if `get_bam_files: true`)
  - Sorted and indexed BAM files
  - Coverage visualization
  - Compatible with IGV and other genome browsers

### Summary Reports

- **reports/**: Pipeline execution summaries
  - Sample-level statistics
  - Variant summary tables
  - Quality control flags

### Coverage Plots

- **plots/**: Visualization of genome coverage
  - Per-sample coverage plots
  - Amplicon coverage distributions (for ARTIC_PE)
  - Depth of coverage across genome

## System Requirements

- **Minimum RAM**: 8GB
- **Recommended RAM**: 16GB or more for large datasets
- **Disk Space**: Ensure adequate space for outputs
  - Databases: ~5GB
  - Output: Varies by sample count and size
- **Docker**: Ensure your Docker container has sufficient memory allocated
- **CPU**: Multi-core processor recommended (pipeline supports multi-threading)

## Pipeline Workflow

### ARTIC_PE Workflow

1. **Read Quality Control**: Filter and trim low-quality reads
2. **Reference Alignment**: Map reads to SARS-CoV-2 reference genome using BWA
3. **Primer Trimming**: Remove primer sequences using iVar
4. **Variant Calling**: Identify variants with iVar
5. **Consensus Generation**: Generate consensus sequences
6. **Variant Annotation**: Annotate variants with SnpEff
7. **Quality Metrics**: Calculate coverage and quality statistics
8. **Visualization**: Generate coverage plots and summary reports

### SGS_PE/SGS_SE Workflow

1. **Read Quality Control**: Filter and trim low-quality reads
2. **Reference Alignment**: Map reads to SARS-CoV-2 reference genome using BWA
3. **Variant Calling**: Identify variants
4. **Consensus Generation**: Generate consensus sequences
5. **Variant Annotation**: Annotate variants with SnpEff
6. **Quality Metrics**: Calculate coverage and quality statistics
7. **Visualization**: Generate coverage plots and summary reports

## Tips

- Use ARTIC V4.1 or V5.3.2 for most current sequencing runs
- Choose the appropriate primer version matching your lab protocol
- Enable BAM export (`get_bam_files: true`) if you need to visualize alignments
- For custom primers, ensure BED format is correct (0-based coordinates)
- Check coverage metrics to ensure sufficient sequencing depth (>100X recommended)
- Review variant call quality scores to filter low-confidence variants
- SGS_PE requires paired primer files in FASTA format
- Ensure sufficient disk space for outputs, especially when exporting BAM files

For complete documentation, see the [GitHub README](https://github.com/niaid/nephele_sars2/blob/main/README.md).
