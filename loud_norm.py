#!/usr/bin/env python
import json
import re
import subprocess
import sys
from pathlib import Path

# handle UTF-8 filenames (for Windows terminals etc.)
sys.stdout.reconfigure(encoding="utf-8")


def detect_samplerate(file: Path) -> int:
    """
    Detect the original input sample rate with ffprobe.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=sample_rate",
        "-of",
        "default=nw=1:nk=1",
        str(file),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return int(out)


def analyze_ebur128(file: Path) -> str:
    """
    Run ffmpeg with ebur128 and return stderr text output.
    Use true-peak for TP measurement compatibility with loudnorm.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        str(file),
        "-vn",
        "-sn",
        "-dn",
        "-map",
        "0:a",
        "-filter_complex",
        "[0:a]ebur128=peak=sample:framelog=verbose",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    return result.stderr


def parse_ebur128_output(output: str) -> dict:
    """
    Parse the 'Summary:' section in a tolerant way.
    Works across minor formatting differences.
    """
    msum = re.search(r"Summary:\s*(.*)\Z", output, re.S)
    if not msum:
        raise ValueError("No ebur128 summary found in ffmpeg output")
    section = msum.group(1)

    def find_float(pattern: str):
        m = re.search(pattern, section)
        return float(m.group(1)) if m else None

    data = {
        # Try both verbose ("Integrated loudness: I:  -21.4") and compact ("I: -21.4")
        "input_i": find_float(
            r"(?:Integrated loudness:\s*I|I):\s*([+-]?\d+(?:\.\d+)?)"
        ),
        "input_thresh": find_float(r"Threshold:\s*([+-]?\d+(?:\.\d+)?)"),
        "input_lra": find_float(
            r"(?:Loudness range:\s*LRA|LRA):\s*([+-]?\d+(?:\.\d+)?)"
        ),
        "input_tp": find_float(r"(?:True peak:\s*Peak|Peak):\s*([+-]?\d+(?:\.\d+)?)"),
        "input_lra_low": find_float(r"LRA low:\s*([+-]?\d+(?:\.\d+)?)"),
        "input_lra_high": find_float(r"LRA high:\s*([+-]?\d+(?:\.\d+)?)"),
    }
    return data


def save_json(data: dict, folder: Path, file: Path):
    with open(folder / f"{file.stem}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(data_file: Path) -> dict:
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    file = Path(sys.argv[1])
    folder = file.parent
    json_path = file.with_suffix(".json")

    # If no JSON yet, measure and write it
    if not json_path.exists():
        print(f"Analyzing loudness for: {file.name}", file=sys.stderr)
        output = analyze_ebur128(file)
        data = parse_ebur128_output(output)
        save_json(data, folder, file)

    # Load measured values
    data = load_json(json_path)

    # Detect source sample rate to force graph back to it after loudnorm
    try:
        sr = detect_samplerate(file)
    except Exception:
        sr = 0  # if detection fails, omit aresample
    # Targets (adjust if you like)
    I_target = -16.0  # LUFS
    TP_limit = -1.0  # dBTP
    LRA_tgt = 7.0

    I_meas = float(data.get("input_i", -23.0))
    LRA_meas = float(data.get("input_lra", 7.0))
    TP_meas = float(data.get("input_tp", -3.0))
    thr_meas = float(data.get("input_thresh", -30.0))

    # LU offset in dB/LU
    gain_LU = I_target - I_meas

    # If you want 'safe static gain' when running linear mode (no limiter),
    # you can clamp by TP headroom:
    gain_TP = TP_limit - TP_meas
    offset_db = min(gain_LU, gain_TP)  # static safe gain
    # If you'd rather let loudnorm (dynamic) handle TP, use:
    # offset_db = gain_LU
    # Choose whether you want linear or dynamic behavior:
    #  - linear=true  => constant gain; loudnorm won't upsample; add limiter if you need TP safety.
    #  - linear=false => default dynamic behavior; may upsample to 192 kHz internally; respects TP.
    linear = False

    loud_target = f"I={I_target}:TP={TP_limit}:LRA={LRA_tgt}:"
    loud_measured = (
        f"measured_I={I_meas}:"
        f"measured_LRA={LRA_meas}:"
        f"measured_TP={TP_meas}:"
        f"measured_thresh={thr_meas}:"
        # f"offset={offset_db:.2f}:"
        f"linear={'true' if linear else 'false'}"
    )

    # Final lavfi string for mpv (Lua will do: af set @ln:lavfi=<this>)
    if sr > 0:
        out = f"[loudnorm={loud_target + loud_measured}],aresample={sr}"
    else:
        out = f"[loudnorm={loud_target + loud_measured}]"

    print(out)
