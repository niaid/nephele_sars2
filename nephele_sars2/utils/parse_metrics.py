import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

plt.style.use("ggplot")

# in out
parser = argparse.ArgumentParser(
    description="Plot coverage of full and downsampled BAM files"
)
parser.add_argument("--sample", dest="sample", required=True, help="full BAM file")
parser.add_argument(
    "--aln-stats", dest="in_aln_stats", required=True, help="full BAM file"
)
parser.add_argument(
    "--depth", dest="in_depth", required=True, help="downsampled BAM file"
)
parser.add_argument(
    "--vcf-stats", dest="in_vcf_stats", required=True, help="downsampled BAM file"
)
parser.add_argument("--out", dest="out_report", required=True, help="coverage plot")
args = parser.parse_args()

sample = args.sample
in_aln_stats = args.in_aln_stats
in_depth = args.in_depth
in_vcf_stats = args.in_vcf_stats
out_report = args.out_report

### constants
win_size = 50
cov_cutoff = 50
cov_pass_filter = 95

stats_dict = {}
stats_dict["sample"] = sample

# parse VCF for variation stats
with open(in_vcf_stats) as f:
    for line in f:
        if line.startswith("SN"):
            vals = line.rstrip().split("\t")
            if "SNPs" in line:
                stats_dict["snps"] = [vals[3]]
            if "indels" in line:
                stats_dict["indels"] = [vals[3]]

# parse mapping stats
with open(in_aln_stats) as f:
    for line in f:
        if line.startswith("PAIR"):
            vals = line.split("\t")
            stats_dict["reads"] = [vals[1]]
            stats_dict["aligned_reads"] = [vals[5]]
            stats_dict["percent_aligned"] = [float(vals[6]) * 100]
            stats_dict["read_length"] = [vals[15]]
            stats_dict["percent_pairs_aligned"] = [float(vals[17]) * 100]

        if line.startswith("UNPAIRED"):
            vals = line.split("\t")
            stats_dict["reads"] = [vals[1]]
            stats_dict["aligned_reads"] = [vals[5]]
            stats_dict["percent_aligned"] = [float(vals[6]) * 100]
            stats_dict["read_length"] = [vals[15]]
            stats_dict["percent_pairs_aligned"] = "NA"

# parse coverage
header = ["chrom", "pos", "coverage"]
df = pd.read_csv(in_depth, sep="\t", names=header)
breadth_cov = (len(df[df["coverage"] >= cov_cutoff]) / df.shape[0]) * 100
mean_cov = df["coverage"].mean()
column_cov = f"percent_genome_covered_at_{cov_cutoff}X"

stats_dict["mean_coverage"] = mean_cov
stats_dict[column_cov] = breadth_cov

out_df = pd.DataFrame.from_dict(stats_dict)
out_df.to_csv(out_report, index=False)
