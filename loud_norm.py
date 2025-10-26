#!/usr/bin/env python

import json
import subprocess
import sys
import re
from pathlib import Path

# handle UTF-8 filenames
sys.stdout.reconfigure(encoding="utf-8")


def analyze_ebur128(file):
    """
    Run ffmpeg with ebur128 and return stderr text output.
    """
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats",
        "-i", str(file),
        "-vn", "-sn", "-dn", # disable video, subtitles, data
        "-map", "0:a", # select only audio
        "-filter_complex", "[0:a]ebur128=peak=sample", # use filter_complex
        "-f", "null", "-" # discard output, read logs from stderr
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    return result.stderr


def parse_ebur128_output(output):
    """
    Parse ebur128 summary section into a dictionary.
    """
    summary_pattern = re.compile(r"Summary:\s*(.*?)\Z", re.S)
    match = summary_pattern.search(output)
    if not match:
        raise ValueError("No ebur128 summary found in ffmpeg output")

    section = match.group(1)
    patterns = {
        "input_i": r"I:\s*([-0-9.]+)",
        "input_thresh": r"Threshold:\s*([-0-9.]+)",
        "input_lra": r"LRA:\s*([-0-9.]+)",
        "input_tp": r"Peak:\s*([-0-9.]+)", # no real TP, placeholder for compatibility
        "input_lra_low": r"LRA low:\s*([-0-9.]+)",
        "input_lra_high": r"LRA high:\s*([-0-9.]+)",
    }

    data = {}
    for key, pat in patterns.items():
        m = re.search(pat, section)
        data[key] = float(m.group(1)) if m else None

    return data


def save_json(data, folder, file):
    """
    Save parsed output to a JSON file
    """
    with open(folder / f"{file.stem}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(data_file):
    """
    Load pre-calculated JSON file
    """
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    file = Path(sys.argv[1])
    folder = file.parent
    # currently make assumption that the json file is in the same directory as the file
    json_path = file.with_suffix(".json")

    if not json_path.exists():
        print(f"Analyzing loudness for: {file.name}", file=sys.stderr)
        output = analyze_ebur128(file)
        data = parse_ebur128_output(output)
        save_json(data, folder, file)
    else:
        data = load_json(json_path)

    # approximate target offset (since ebur128 doesn't provide it)
    I_target = -16.0 # desired loudness target
    TP_limit = -1.0 # don't exceed this true peak
    I_measured = data.get('input_i', -23.0)
    TP_measured = data.get('input_tp', -3.0)

    # compute safe offset
    gain_LU = I_target - I_measured
    gain_TP = TP_limit - TP_measured
    safe_gain = min(gain_LU, gain_TP)

    # approximate target offset as static safe gain
    target_offset = safe_gain

    # build MPV loudnorm filter string (for Lua)
    loud_target = (
        f"I={I_target}:"
        f"TP={TP_limit}:"
        f"LRA={data.get('input_lra', 7)}:"
    )
    loud_measured = (
        f"measured_I={data.get('input_i')}:"
        f"measured_LRA={data.get('input_lra')}:"
        f"measured_TP={data.get('input_tp')}:"
        f"measured_thresh={data.get('input_thresh')}:"
        f"offset={target_offset:.2f}"
    )
    loudnorm = f"[loudnorm={loud_target + loud_measured}]"

    # print loudnorm to terminal for lua to grab
    print(loudnorm)
