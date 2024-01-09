#!/bin/bash
trimmomatic -version | awk '{{print "Trimmomatic", $1}}'
bwa 2>&1 >/dev/null | head -n3 | tail -n1 | sed 's/Version: /bwa /'
echo Picard
gatk --version 2>&1 >/dev/null | head -n1
samtools version | head -n1
bcftools  2>&1 >/dev/null | head -n4 | tail -n1 | sed 's/Version:/bcftools/'
deeptools --version
pilon | head -n1 | sed 's/\(Pilon version [0-9.]*\).*/\1/'
bedtools --version
pip list | grep pysam | sed 's/\s\+/ /'
pip list | grep pypairix | sed 's/\s\+/ /'
java -jar /usr/local/src/snpEff/snpEff.jar 2>&1 >/dev/null | head -n1
ivar version | head -n1