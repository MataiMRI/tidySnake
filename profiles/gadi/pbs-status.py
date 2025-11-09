#!/usr/bin/env python3
# Reports one of: running | success | failed
import os, re, subprocess as sp, sys, time  # CHANGED: add os,time for tiny E-retries

jobid = sys.argv[1]

DBG = os.environ.get("SNAKEMAKE_PBS_DEBUG", "0") == "1"

def dbg(*a):
    if DBG:
        sys.stderr.write("pbs-status jobid: " + " ".join(map(str, a)) + "\n")
        sys.stderr.flush()

dbg(jobid)

def out(s: str):
    # CHANGED: write+flush to guarantee a single clean token on stdout
    sys.stdout.write(s + "\n")
    sys.stdout.flush()
    sys.exit(0)

# CHANGED: small knobs to smooth the E->F/X race without blocking for long
E_RETRIES = int(os.environ.get("PBS_STATUS_E_RETRIES", "20"))   # try a few quick rechecks
E_SLEEP   = float(os.environ.get("PBS_STATUS_E_SLEEP", "1")) # seconds between rechecks

def qxf(jid: str) -> str:
    return sp.check_output(["qstat", "-xf", jid], text=True, stderr=sp.STDOUT)

try:
    txt = qxf(jobid)
except sp.CalledProcessError as e:
    # CHANGED: case-insensitive match and a couple of common variants
    msg = (e.output or "").strip().lower()
    # On Gadi, completed jobs can age out quickly:
    if ("unknown job id" in msg or "job has finished" in msg
            or "cannot locate job" in msg or "unknown job id error" in msg):
        out("success")
    # If qstat itself failed for another reason, be conservative:
    out("running")

# Parse PBS extended output
m_state = re.search(r'^\s*job_state\s*=\s*(\w)', txt, re.M | re.I)
state = (m_state.group(1).upper() if m_state else "")

# CHANGED: special handling for E (exiting) to collapse the race quickly
if state == "E":
    # Fast retry loop: try to see F/X or age-out within a short window
    for _ in range(E_RETRIES):
        time.sleep(E_SLEEP)
        try:
            txt = qxf(jobid)
        except sp.CalledProcessError as e:
            msg = (e.output or "").strip().lower()
            if ("unknown job id" in msg or "job has finished" in msg
                    or "cannot locate job" in msg or "unknown job id error" in msg):
                out("success")
            out("running")
        m_state = re.search(r'^\s*job_state\s*=\s*(\w)', txt, re.M | re.I)
        state = (m_state.group(1).upper() if m_state else "")
        if state in {"F","X"}:
            break
    # Fall through to the F/X block if it flipped; otherwise keep polling
    if state != "F" and state != "X":
        out("running")

# Still in system
if state in {"Q","H","R","W"} or not state:  # CHANGED: treat empty as running defensively
    out("running")

# Finished or subjob completed/deleted
if state in {"F","X"}:
    # case-insensitive key
    m_exit = re.search(r'^\s*exit_status\s*=\s*(-?\d+)', txt, re.M | re.I)
    if not m_exit:
        # CHANGED: assume success if final but exit_status lagged/aged-out
        out("success")
    exitc = int(m_exit.group(1))
    out("success" if exitc == 0 else "failed")

# Fallback (rare): keep polling
# out("running")


# #!/usr/bin/env python3
# # Reports one of: running | success | failed
# import re, subprocess as sp, sys

# jobid = sys.argv[1]
# # print(jobid)

# def out(s: str):
#     print(s)
#     sys.exit(0)

# try:
#     txt = sp.check_output(["qstat", "-xf", jobid], text=True, stderr=sp.STDOUT)
# except sp.CalledProcessError as e:
#     msg = e.output.strip()
#     # On Gadi, completed jobs can age out quickly:
#     if "Unknown Job Id" in msg or "Job has finished" in msg:
#         out("success")
#     # If qstat itself failed for another reason, be conservative:
#     out("running")

# # Parse PBS extended output
# m_state = re.search(r'^\s*job_state\s*=\s*(\w)', txt, re.M | re.I)
# # print("m_state: ", m_state)
# state = (m_state.group(1).upper() if m_state else "")
# # print("state: ", state)

# # Still in system
# if state in {"Q","H","R","W"}:
#     # print("state")	
#     out("running")

# # Finished or subjob completed/deleted
# if state in {"F","X"}:
#     # print("state: ", state)	
#     m_exit = re.search(r'^\s*Exit_status\s*=\s*(-?\d+)', txt, re.M | re.I)
#     # print("m_exit", m_exit)
#     if not m_exit:
#         # Exit_status can lag behind state=F/X; assume success to avoid false negatives
#         out("success")
# 	# print("unsuccessful")
#     exitc = int(m_exit.group(1))
#     out("success" if exitc == 0 else "failed")

# # Fallback (rare): keep polling
# out("running")

