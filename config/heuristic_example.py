import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
    allowed template fields - follow python string module:
    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    t1w = create_key(
        'sub-{subject}/{session}/anat/sub-{subject}_{session}_run-00{item:01d}_T1w'
    )
    dwi = create_key(
        'sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-00{item:01d}_dwi'
    )

    info = {t1w: [], dwi: []}

    for idx, s in enumerate(seqinfo):
        if (s.dim1 == 512) and (s.dim2 == 512) and ('BRAVO' in s.sequence_name):
            info[t1w].append(s.series_id)
        if (s.dim1 == 128) and (s.dim2 == 128) and ('epi2' in s.sequence_name):
            info[dwi].append(s.series_id)

    return info
