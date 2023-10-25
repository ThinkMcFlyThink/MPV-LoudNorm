# MPV-LoudNorm
Automatic and non-destructive 2-pass loudnorm audio filter generator for the MPV player (https://mpv.io/).

Rather than simply using the typical `af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0]` filter found online, this script perfoms ebur128 and volumedetect to get the file's sound profile - making it more accurate. The results are saved as a txt file in the same directory as the file being played, therefore analysis does not need be re-run in the future.

Then based on the information in the txt file, a filter string is built and passed into MPV. Typical example `af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0:measured_I=-19.5:measured_LRA=16.2:measured_TP=-1.1:measured_thresh=-30.6]`.

## Current Issues

 - When playing full-screen, after completion of analysis the player minimises.
 - Some audio still has dynamic range issues. Will likely try adding in a _dynaudnorm_ filter in additional to loudnorm.

## Installation

In your MPV scripts directory, create a new folder named "real_loudnorm" and paste in the Python and LUA files.
Make sure Python is installed.
Make sure FFMPEG is on the system path.

## Usage

The HOTKEY to execute the script is 'n'.

## Notes

 - The vast majority of functionality comes from Python. The MPV lua script simply calls the python script and grabs the outputted string from the command line.
 - How long ebur128 and volumedetect takes to analyse depends on a few factors; runtime, audio channels, etc. Typically no more than 1-2mins.
 - Currently only tested on Windows 10.
 - Currently very clunky...
