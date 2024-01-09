# What is the purpose of this repository template?

This repository template has been created to assist in the establishment of a new Nephele pipeline repository. It includes a collection of files and documentation essential to kickstart your Nephele pipeline.

Several key areas have been preconfigured:

- Pipeline container building and deployment: [`build-and-push.yaml`](./.github/workflows/build-and-push.yaml) GitHub Action workflow handles the building of the pipeline container and its subsequent push to the AWS ECR repository.
- Directories structure within the repository: we maintain a consistent structure across all Nephele pipeline repositories.
- Skeleton of configuration code, schema code and pipeline code: utilizing the [`nephele_pipeline_utils`](https://github.com/niaid/nephele_pipeline_utils), a dependency for all pipelines, we've provided foundational code structures that incorporate validation and I/O management capabilities. This serves to expedite initial setup without extensive documentation reading.
- Code style, formatting and local development automation: to streamline development processes, we've introduced [`Taskfile.yaml`](./Taskfile.yaml) for automating specific tasks during pipeline development, [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for automated code formatting and linting, along with a corresponding GitHub Action workflow to ensure code checks on each commit.

> [!IMPORTANT]
> **Created this repository based on [`niaid/nephele_pipeline_template`](https://github.com/niaid/nephele_pipeline_template). What now?**
>
> 1. Update this readme with your pipeline documentation.
> 2. Update [GitHub Action workflow definition](./.github/workflows/build-and-push.yaml) (replace all occurences of `nephele_pipeline_template` with `nephele_<pipeline name>`, for example `nephele_dada2`).
> 3. Register a new self-hosted GitHub runner to run the GitHub Action workflow above in `nephele-mgmt` space
>
> - `spaces materials register -space nephele -repo niaid/nephele_<pipeline_name>`
> - `spaces materials runners add -space nephele -repo niaid/nephele_<pipeline_name>`
>
> 4. Create a new AWS ECR repository in `nephele-mgmt` space to deposit containers. Name: `nephele_<pipeline name>`, for example `nephele_dada2`.
> 5. Once you're done remove everything above the line below.

---

# Nephele pipeline template repository

This document describes how to run the _PIPELINE_NAME_ pipeline.

## Running the pipeline

> [!TIP]
> You may use [`task`](https://taskfile.dev/#/) to automate the steps described below. Run `task --list` to see the available tasks. This requires `task` to be installed on your system.

### Build the pipeline container

```bash
docker build -f nephele_PIPELINE_NAME/Dockerfile --tag nephele_qc_long_reads:latest .
```

### Set environment variables

In order to run the next step, the following environment variables must be set:

- `INPUTS_MOUNT`: path to the inputs directory. The structure of this directory is dictated by the paths you provide in `inputs` section in the input JSON file.
- `OUTPUTS_MOUNT`: path to the outputs directory

For example:

```bash
export INPUTS_MOUNT=/Users/stolarczykmj/Desktop/qc_long_reads
export OUTPUTS_MOUNT=/Users/stolarczykmj/Desktop/outputs
```

### Prepare the input JSON file

The input JSON file must be present in the container. For example, you may put it in the inputs directory: `$INPUTS_MOUNT/example_input.json`.

Below is a fully functional example of the input JSON file. In order to use defaults for the pipeline arguments, you may omit some key value pais in the `pipeline_arguments` section.

```json
{
  "inputs": [
    {
      "name": "18S_combo",
      "files": [
        {
          "path": "18S_combo.fastq.gz",
          "type": "fwd"
        }
      ],
      "metadata": [
        {
          "TreatmentGroup": "18S_combo"
        }
      ],
      "type": "fastq",
      "source": "input"
    },
    {
      "name": "Mock",
      "files": [
        {
          "path": "Mock.fastq",
          "type": "fwd"
        }
      ],
      "metadata": [
        {
          "TreatmentGroup": "Mock"
        }
      ],
      "type": "fastq",
      "source": "input"
    }
  ],
  "pipeline_arguments": {
    "data_type": "qc_lr",
    "threads": 8,
    "mem_gb": 16
  },
  "outputs": [
    {
      "name": "<generated>",
      "files": [
        {
          "s3_location": "s3://test/test/x.biom",
          "path": "/home/user/job/x.biom"
        }
      ],
      "metadata": [
        {
          "TreatmentGroup": "test"
        }
      ],
      "type": "biom",
      "source": "output"
    }
  ]
}
```

Notably, you may adjust the pipeline arguments based on your analysis needs. Pipeline arguments reference:

- `data_type`

  - Type: `str`
  - Choices: `qc_lr`
  - Description: Specifies the data type to be processed.

- `threads`

  - Type: `int`
  - Default: `8`
  - Description: Number of threads to use.

- `mem_gb`

  - Type: `int`
  - Default: `16`
  - Description: Amount of memory to use in GB.

### Run the pipeline container

```bash
docker run --rm --name nephele_PIPELINE_NAME_container \
    --mount type=bind,source=$INPUTS_MOUNT,target=/inputs \
    --mount type=bind,source=$OUTPUTS_MOUNT,target=/outputs \
    nephele_PIPELINE_NAME:latest --json_file_path /inputs/example_input.json
```
