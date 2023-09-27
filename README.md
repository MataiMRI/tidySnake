# tidySnake workflow

This repository provides a Snakemake workflow for fMRI data basic cleanup.
It is meant to handle DICOM to BIDs convertion as well as simple quality control.


## Installation

*If you are using the [NeSI](https://www.nesi.org.nz) platform, please follow the [NeSI related documentation](NESI.md).*

To run this workflow on your workstation, you need to install the following softwares:

- `apptainer`, a container system (see [installation instructions](https://apptainer.org/docs/admin/main/installation.html))
- `snakemake`, the workflow management system (see [installation instructions](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html))
- `git`, the distributed version control system (see [download page](https://git-scm.com/downloads))

Clone this repository using:

```
git clone https://github.com/MataiMRI/tidySnake.git
```

Then copy the configuration file `config/config_example.yml` into `config/config.yaml`:

```
cd tidySnake
cp config/config_example.yml config/config.yaml
```

and set the following entries:

- the ethics prefix `ethics_prefix` for your input files,
- the input data folder `datadir`,
- the results folder `resultsdir`,
- the path to your `heudiconv` heuristic script (`heuristic` entry under `heudiconv` section).

You may want to edit other entries, in particular:

- for each software, compute resources (time, memory and threads) can be adjusted,
- for some software, additional command line arguments.

Once this configuration is finished, you can run `snakemake` to start the workflow.

Use a dry-run to check that installation and configuration is working:

```
snakemake -n
```

See the [Snakemake options](README.md#Useful-Snakemake-options) section for other useful options.


## Formats

The workflow assumes that input scan data are:

- folders or .zip files (you can mix both),
- stored in the `datadir` folder configured [`config/config.yml`](config/config.yml),
- they are named using the convention `<ethics_prefix>_<subject>_<session>`, where

  - `<ethics_prefix>` is set in [`config/config.yml`](config/config.yml),
  - `<session>` can be omitted, but will then be considered as `a`.

Within a input folder (or .zip file), only the parent folder of DICOM files will be kept when tidying the data.
Any other level of nesting will be ignored.

TODO describe output format

```
RESULTS_FOLDER/
└── bids/
    ├── derivatives/
    │   ├── mriqc/
    │   │   ├── logs/
    │   │   ├── sub-SUBJECT/
    │   │   │   └── ses-SESSION/
    │   │   │       └── anat/
    │   │   │           └── sub-SUBJECT_ses-SESSION_run-RUNID_T1w.json
    │   │   ├── dataset_description.json
    │   │   └── sub-SUBJECT_ses-SESSION_run-RUNID_T1w.html
    │   └── qc_status/
    │       └── sub-SUBJECT_ses-SESSION_run-RUNID_qc.yaml
    ├── sub-SUBJECT/
    │   └── ses-SESSION/
    │       ├── anat/
    │       │   ├── sub-SUBJECT_ses-SESSION_run-RUNID_T1w.json
    │       │   └── sub-SUBJECT_ses-SESSION_run-RUNID_T1w.nii.gz
    │       ├── OTHER_MODALITY/
    │       │   └── ...
    │       └── sub-SUBJECT_ses-SESSION_scans.tsv
    ├── CHANGES
    ├── dataset_description.json
    ├── README
    └── scans.json
```


## Workflow

TODO steps


## Useful Snakemake options

View steps within workflow using rulegraph:

```
snakemake --forceall --rulegraph | dot -Tpdf > rulegraph.pdf
```

Inform `snakemake` of the maximum amount of memory available on the workstation:

```
snakemake --resources mem=48GB
```

Keep incomplete files (useful for debugging) from fail jobs, instead of wiping them:

```
snakemake --keep-incomplete
```

Run the pipeline until a certain file or rule, e.g. the `bias_correction` rule:

```
snakemake --until bias_correction
```

All these options can be combined and used with a profile, for example:

```
snakemake --profile profiles/local --keep-incomplete --until bias_correction
```

Unlock the folder, in case `snakemake` had to be interrupted abruptly previously:

```
snakemake --unlock
```

*Note: This last hint will be mentioned to you by `snakemake` itself.
Use it only when recommended to to so ;-).*
