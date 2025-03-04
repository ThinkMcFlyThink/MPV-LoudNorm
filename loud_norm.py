import json
import subprocess
import sys
from pathlib import Path

# if filename has some funky characters (eg unicode emoji)
sys.stdout.reconfigure(encoding="utf-8")


def strip_text(file_txt):
    #
    # strip all above and below { and }
    #
    output = file_txt.stderr.decode().split("{")[1].split("}")[0]
    output = json.loads("{" + output + "}")
    return output


def save_json(data, folder):
    #
    # save stripped output to json file
    #
    with open(folder / f"{file.stem}.json", "w") as f:
        json.dump(data, f)


def load_json(data_file):
    #
    # if json file found, load back in the data
    #
    with open(data_file, "r") as file:
        data = json.load(file)

    return data


def ffmpeg(file, folder):
    #
    # Build a FFMPEG string and execute it.
    #
    string = f'ffmpeg -i "{file}" -af loudnorm=print_format=json -map 0:a -f null NULL'
    cmd = subprocess.run(string, stderr=subprocess.PIPE)

    data = strip_text(cmd)
    save_json(data, folder)
    return data


if __name__ == "__main__":
    # parse input into folder and file
    file = Path(sys.argv[1])
    folder = file.parents[0]
    df = file.with_suffix(".json")

    # check if the .txt file exists
    if not df.is_file():
        df = ffmpeg(file, folder)
    else:
        df = load_json(df)

    # build mpv string
    loud_target = f"I=-24:TP=-1.0:LRA={df['input_lra']}:"
    loud_measured = f"measured_I={df['input_i']}:measured_LRA={df['input_lra']}:measured_TP={df['input_tp']}:measured_thresh={df['input_thresh']}:offset={df['target_offset']}"
    loundnorm = f"[loudnorm={loud_target + loud_measured}]"

    # This is the key part. Print the assembled MPVB filter to terminal, which the MPV LUA script can access.
    print(loundnorm)
