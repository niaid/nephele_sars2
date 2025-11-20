# About Nephele SARS-CoV-2

This Docker image contains the SARS-CoV-2 analysis pipeline for the Nephele microbiome analysis platform. The pipeline assembles SARS-CoV-2 genomes and calls mutations from Illumina sequence data generated using a tiled multiplexed primers strategy.

## Features

- **Primer Support**: Compatible with multiple primer schemes including ARTIC (V1-V5.3.2), NEB VarSkip, and IDT Midnight
- **Custom Primers**: Support for user-provided custom primer designs in BED format
- **Paired-End Support**: Process both ARTIC paired-end and shotgun sequencing (SGS) paired-end data
- **Single-End Support**: Process shotgun sequencing single-end data
- **Variant Calling**: Comprehensive mutation detection and annotation
- **SNP Effect Annotation**: Functional impact analysis of variants using SnpEff
- **Quality Metrics**: Detailed quality control and coverage statistics
- **Reference Assembly**: Align reads to SARS-CoV-2 reference genome
- **BAM File Export**: Optional export of alignment files for further analysis
- **Visualization**: Generate coverage plots and variant summaries

## Tools Included

### iVar
Amplicon-based variant calling and consensus sequence generation:
- Primer trimming for amplicon data
- Variant detection with configurable frequency thresholds
- Consensus sequence generation with quality filtering
- Compatible with ARTIC and other tiled amplicon protocols

### BWA
Sequence alignment:
- BWA-MEM algorithm for accurate read mapping
- Optimized for SARS-CoV-2 genome alignment
- Support for paired-end and single-end reads

### Samtools
BAM file processing and manipulation:
- Read sorting and indexing
- Coverage calculation
- Quality filtering
- File format conversion

### SnpEff
Variant annotation and functional effect prediction:
- Genomic variant annotation
- Amino acid change prediction
- Effect classification (synonymous, missense, nonsense)
- Gene-level impact assessment

### Nextflow
Workflow management:
- Reproducible pipeline execution
- Resource management
- Error handling and logging
- Parallel processing support

## Use Cases

- SARS-CoV-2 genome assembly from amplicon sequencing
- Mutation detection and tracking
- Variant of concern identification
- Quality control for SARS-CoV-2 sequencing runs
- Comparative genomic analysis of SARS-CoV-2 samples
- Phylogenetic study preparation

## Input Requirements

- **FASTQ files**: Illumina sequencing data (paired-end or single-end)
- **Input JSON**: Sample metadata and pipeline parameters
- **Primer file**: BED format primer scheme (provided or custom)
- **Reference genome**: SARS-CoV-2 reference sequence
- **SnpEff database**: Annotation database for variant calling

## Output Highlights

- Assembled consensus sequences (FASTA)
- Variant call files (VCF) with annotations
- Quality metrics and coverage statistics
- Alignment files (BAM) - optional
- SNP effect predictions
- Summary reports and visualizations
- Coverage plots

## Links

- [GitHub Repository](https://github.com/niaid/nephele_sars2)
- [Nephele Platform](https://nephele.niaid.nih.gov/)
