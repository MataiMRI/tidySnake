# #!/usr/bin/env bash

# ROOT="/media/jpmcgeown/PortableSSD/test_heudiconv"
# BIDS_OUT="/media/jpmcgeown/PortableSSD/test_heudiconv_bids"
# HEUDI_DIR="/home/jpmcgeown/github-repos/tidySnake/.snakemake/singularity"
# IMG="$HEUDI_DIR/f945b01a706cad379b15b213af30a94c.simg"

# # Loop over subject_session directories
# for TOP in "$ROOT"/*_*; do
#   [ -d "$TOP" ] || continue
#   bn=$(basename "$TOP")

#   subject="${bn%_*}"   # strip last underscore
#   session="${bn##*_}"  # last token after underscore

#   # inner "<SUBJ>_<SES> - ####" dir
#   inner=$(find "$TOP" -maxdepth 1 -type d -name "${bn} - *" | head -n 1)
#   [ -z "$inner" ] && inner="$TOP"

#   echo "==> Subject: $subject | Session: $session"
#   echo "    Input:   $inner"

#   singularity run --cleanenv \
#     --bind /media/jpmcgeown/PortableSSD \
#     "$IMG" \
#     --files "$inner"/* \
#     -s "$subject" \
#     -ss "$session" \
#     -f convertall \
#     -c none \
#     -o "$BIDS_OUT" \
#     --minmeta \
#     --overwrite
# done

#!/usr/bin/env bash
set -euo pipefail

ROOT="/media/jpmcgeown/PortableSSD/test_heudiconv"
BIDS_OUT="/media/jpmcgeown/PortableSSD/test_heudiconv_bids"
HEUDI_DIR="/home/jpmcgeown/github-repos/tidySnake/.snakemake/singularity"
IMG="$HEUDI_DIR/f945b01a706cad379b15b213af30a94c.simg"

for TOP in "$ROOT"/*_*; do
  [[ -d "$TOP" ]] || continue
  bn=$(basename "$TOP")

  subject="${bn%_*}"     # e.g., Conc_20Ntb14_Rugby_204
  session="${bn##*_}"    # e.g., B

  # inner "<SUBJ>_<SES> - ####" directory
  inner=$(find "$TOP" -maxdepth 1 -type d -name "${bn} - *" | head -n 1)
  [[ -z "$inner" ]] && inner="$TOP"

  echo "==> Subject: $subject | Session: $session"
  echo "    Container: $inner"

  # Collect ONE file from each immediate series subfolder
  files=()
  for series in "$inner"/*; do
    [[ -d "$series" ]] || continue
    # pick the first regular file in the series dir (handles no .dcm extension)
    f=$(find "$series" -maxdepth 1 -type f | head -n 1 || true)
    [[ -n "${f:-}" ]] && files+=("$f")
  done

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "    !! No DICOM files found under $inner; skipping"
    continue
  fi

  echo "    Series detected: ${#files[@]} (passing one file per series)"

  # Run heudiconv using the representative files (much faster)
  singularity run --cleanenv \
    --bind /media/jpmcgeown/PortableSSD \
    "$IMG" \
      --files "${files[@]}" \
      -s "$subject" \
      -ss "$session" \
      -f convertall \
      -c none \
      -o "$BIDS_OUT" \
      --minmeta \
      --overwrite

  echo "    Wrote dicominfo.tsv under $BIDS_OUT/.heudiconv/sub-$subject/ses-$session/info/"
done
