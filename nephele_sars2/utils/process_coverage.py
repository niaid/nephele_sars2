import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

plt.style.use("ggplot")

# in out
parser = argparse.ArgumentParser(
    description="Plot coverage of full and downsampled BAM files"
)
parser.add_argument("--sample", dest="sample", required=True, help="full BAM file")
parser.add_argument("--full", dest="in_full", required=True, help="full BAM file")
parser.add_argument(
    "--down", dest="in_down", required=True, help="downsampled BAM file"
)
parser.add_argument("--out1", dest="cov_plot_pdf", required=True, help="coverage plot")
parser.add_argument("--out2", dest="cov_plot_png", required=True, help="coverage plot")
args = parser.parse_args()

sample = args.sample
in_full = args.in_full
in_down = args.in_down
cov_plot_pdf = args.cov_plot_pdf
cov_plot_png = args.cov_plot_png

# constants
win_size = 50
cov_cutoff = 50
cov_pass_filter = 95

# coverage data
raw_header = ["chrom", "pos", "raw_coverage"]
down_header = ["chrom", "pos", "down_coverage"]

df = pd.read_csv(in_full, sep="\t", names=raw_header)
down_df = pd.read_csv(in_down, sep="\t", names=down_header)

df = df.merge(down_df, on=["chrom", "pos"])
df["sample"] = sample

# clean
columns = ["sample", "pos", "raw_coverage", "down_coverage"]
df = df[columns]

# rolling window mean
df["raw_win_cov"] = (
    df["raw_coverage"].rolling(window=win_size, min_periods=2, center=True).mean()
)
df["down_win_cov"] = (
    df["down_coverage"].rolling(window=win_size, min_periods=2, center=True).mean()
)

# initialize the coverage results df
cov_df = pd.DataFrame(data={"sample": [sample]})

# stats
cov_df["cov_mean"] = df["raw_coverage"].mean()
cov_df["cov_median"] = df["raw_coverage"].median()

column_cov = "cov_{}X".format(cov_cutoff)
column_filt = "filt_{}X".format(cov_cutoff)
cov_df[column_cov] = (len(df[df["raw_coverage"] >= cov_cutoff]) / df.shape[0]) * 100
cov_df[column_filt] = np.where(cov_df[column_cov] >= cov_pass_filter, "PASS", "FAIL")

# plotting coverage
coverage_string = (
    f"percent genome covered at {cov_cutoff}X: {cov_df[column_cov].values[0]:.2f}"
)

fig, ax = plt.subplots(2, 1, figsize=(12, 5), sharex=True)
for i, cov, title in zip(
    range(2), ["raw_win_cov", "down_win_cov"], ["Raw Coverage", "Downsampled Coverage"]
):
    sns.lineplot(
        ax=ax[i], x=df["pos"], y=df[cov], data=df[::win_size], color="steelblue"
    ).set_title(title)
    ax[i].fill_between(df["pos"].values, df[cov].values, color="steelblue")
    ax[i].margins(x=0)
    ax[i].set(ylim=(10, df[cov].max() * 1.5))
    ax[i].set(ylabel="")
    ax[i].set(xlabel="Position")

# genome coverage
# ax[0].text(0.60, 0.90, coverage_string, transform=ax[0].transAxes, verticalalignment='top', fontsize=14)

fig.savefig(cov_plot_pdf)
fig.savefig(cov_plot_png)
