from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass

import yaml
import pandas as pd
from snakemake.io import glob_wildcards


@dataclass
class RunList:
    """Store information about runs as a structure of arrays"""

    subjects: list[str]
    sessions: list[str]
    entities: list[str]

    def append(self, subject: str, session: str, entity: str):
        self.subjects.append(subject)
        self.sessions.append(session)
        self.entities.append(entity)

    def __len__(self):
        return len(self.subjects)

    def __iter__(self):
        return zip(self.subjects, self.sessions, self.entities)


def list_valid_runs(
    resultsdir: str, suffix: str
) -> tuple[RunList, dict[str, dict[str, str]]]:
    """list all valid runs from every subjects, based on QC status files

    :param resultsdir: folder containings a 'bids' folder with mriqc derivatives
    :param suffix: suffix used to filter runs to return
    :returns: list of valid runs and mapping of T1w templates for each subject/session
    """

    qc_file_pattern = (
        f"{resultsdir}/bids/derivatives/mriqc/sub-{{subject}}_ses-{{session}}_qc.yaml"
    )
    subjects, sessions = glob_wildcards(qc_file_pattern)

    runs = RunList([], [], [])
    templates = defaultdict(dict)

    for subject, session in zip(subjects, sessions):
        qc_file = Path(qc_file_pattern.format(subject=subject, session=session))
        qc_data = yaml.safe_load(qc_file.read_text())

        # skip if there is no anatomical template
        if "anat_template" not in qc_data:
            continue

        # check that T1w is valid, if from the same subject/session
        anat_template = qc_data["anat_template"]
        if anat_template.startswith(f"sub-{subject}_ses-{session}"):
            anat_entry = anat_template.removeprefix(f"sub-{subject}_ses-{session}_")
            if not qc_data[anat_entry + "_T1w"]:
                continue

        templates[subject][session] = anat_template

        # list all valid runs
        for entry in qc_data:
            if not entry.endswith(suffix) or not qc_data[entry]:
                continue

            entity, _ = entry.rsplit("_", maxsplit=1)
            runs.append(subject, session, entity)

    return runs, templates


def summarise_qc(resultsdir: str) -> pd.DataFrame:
    """aggregate QC information from all found QC files into one dataset"""

    qc_file_pattern = (
        f"{resultsdir}/bids/derivatives/mriqc/sub-{{subject}}_ses-{{session}}_qc.yaml"
    )
    subjects, sessions = glob_wildcards(qc_file_pattern)

    runs = []
    for subject, session in zip(subjects, sessions):
        qc_file = Path(qc_file_pattern.format(subject=subject, session=session))
        qc_data = yaml.safe_load(qc_file.read_text())

        anat_template = qc_data.get("anat_template")
        for entry in qc_data:
            if entry == "anat_template":
                continue
            run = (subject, session, entry, qc_data[entry], anat_template)
            runs.append(run)

    dset = pd.DataFrame(
        runs, columns=["subject", "session", "run", "qc", "anat_template"]
    )
    dset = dset.sort_values(["subject", "session", "run"])

    return dset
