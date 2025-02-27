# MPV-LoudNorm
Automatic and non-destructive 2-pass loudnorm audio filter generator for the MPV player (https://mpv.io/).

Rather than simply using the typical `af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0]` filter found online, this script perfoms 2 pass loudnorm to get the file's audio profile - making it more accurate than the single pass approach. The results are saved as a json file in the same directory as the file being played, therefore analysis does not need be re-run in the future.

Then based on the information in the json file, a filter string is built and passed into MPV. Typical example `af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0:measured_I=-19.5:measured_LRA=16.2:measured_TP=-1.1:measured_thresh=-30.6]`.

## Current Issues

 - When playing full-screen, after completion of analysis the player minimises.
 - The first pass of FFMPEG's loudnorm filter is very, VERY, slow... (25-35x play speed)

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
