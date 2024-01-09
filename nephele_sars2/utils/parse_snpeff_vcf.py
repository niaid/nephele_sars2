# modules
import argparse
import gzip
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd

"""
pull annotated SNPs from snpEff annotated VCF files, collate
"""

# parse command line arguments
parser = argparse.ArgumentParser(
    description="Extract SNPs from snpEff annotated vcf file and output multi fasta"
)
parser.add_argument("--sample", dest="sample", required=True, help="sample name")
parser.add_argument("--in_vcf", dest="in_vcf", required=True, help="in snpeff VCF file")
parser.add_argument(
    "--out", dest="out_summary", required=True, help="output SNP effect summary"
)
args = parser.parse_args()

sample = args.sample
in_vcf = args.in_vcf
out_summary = args.out_summary


def parse_vcf(sample_file):
    with gzip.open(sample_file, "rb") as f:
        data = defaultdict(list)

        for line_bytes in f:
            line = line_bytes.decode("utf-8")
            line = line.rstrip()
            if line.startswith("#CHROM"):
                sample = line.split("\t")[9]

            if not line.startswith("#"):
                values = line.split("\t")
                chrom, coord, ref, alt, vcf_filter, info = (
                    values[0],
                    values[1],
                    values[3],
                    values[4],
                    values[6],
                    values[7],
                )

                if vcf_filter == "PASS":
                    snpeff_vals = info.split(";")

                    # first annotation
                    for index, element in enumerate(snpeff_vals):
                        if element.startswith("ANN="):
                            ann = snpeff_vals[index].split(",")[0]
                            fields = ["NA" if v is "" else v for v in ann.split("|")]
                            effect, gene, nucleotide_change, amino_acid_change = (
                                fields[1],
                                fields[3],
                                fields[9],
                                fields[10],
                            )

                            data["sample"].append(sample)
                            data["coordinate"].append(coord)
                            data["effect"].append(effect)
                            data["gene"].append(gene)
                            data["nucleotide_change"].append(nucleotide_change)
                            data["amino_acid_change"].append(amino_acid_change)

    return pd.DataFrame(data)


this_df = parse_vcf(in_vcf)
this_df.to_csv(out_summary, index=False)
