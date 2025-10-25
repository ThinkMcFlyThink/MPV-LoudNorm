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
        "-filter_complex", "ebur128",
        "-f", "null", "-"
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
        "input_tp": r"LRA high:\s*([-0-9.]+)",  # no real TP, placeholder for compatibility
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
    Save parsed output to a JSON file.
    """
    with open(folder / f"{file.stem}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(data_file):
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    file = Path(sys.argv[1])
    folder = file.parent
    json_path = file.with_suffix(".json")

    if not json_path.exists():
        print(f"Analyzing loudness for: {file.name}", file=sys.stderr)
        output = analyze_ebur128(file)
        data = parse_ebur128_output(output)
        save_json(data, folder, file)
    else:
        data = load_json(json_path)

    # Approximate target offset (since ebur128 doesn't provide it)
    I_target = -16.0
    I_measured = data.get("input_i", -23.0)
    target_offset = float(I_target) - float(I_measured)

    # Build MPV loudnorm filter string (for Lua)
    loud_target = f"I={I_target}:TP=-1.0:LRA={data.get('input_lra', 7)}:"
    loud_measured = (
        f"measured_I={data.get('input_i')}:"
        f"measured_LRA={data.get('input_lra')}:"
        f"measured_TP={data.get('input_tp')}:"
        f"measured_thresh={data.get('input_thresh')}:"
        f"offset={target_offset:.2f}"
    )
    loudnorm = f"[loudnorm={loud_target + loud_measured}]"

    print(loudnorm)
