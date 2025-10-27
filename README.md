# MPV-LoudNorm
Automatic and non-destructive 2-pass loudnorm audio filter generator for the MPV player (https://mpv.io/).

Rather than simply using the typical `[loudnorm=I=-16.0:TP=-1.5:LRA=11.0]` filter found online, this script perfoms 2 pass loudnorm to get the file's audio profile - making it more accurate than the single pass approach. The results are saved as a json file in the same directory as the file being played, therefore analysis does not need be re-run in the future.

Then based on the information in the json file, a filter is generated and passed to MPV. Typical example is: `[loudnorm=I=-16.0:TP=-1.5:LRA=11.0:measured_I=-19.5:measured_LRA=16.2:measured_TP=-1.1:measured_thresh=-30.6]`.

## Current Issues
 - The loudnorm filter upsamples audio to 192kHz. Currently the script detects the sample rate prior to applying loudnorm so it can downsample the output. This is less than ideal and adds overhead.

## Installation
In your MPV scripts directory, create a new folder named "real_loudnorm" and paste in the Python and LUA files.
Make sure Python is installed.
Make sure FFMPEG is on the system path.

## Usage
The HOTKEY to execute the script is 'n'.

## Upcoming Features
 - Adding ETA so user has some idea how long analysis will take.
 - Use MPV's FFMPEG rather than the system.

## Notes
 - How long loudnorm takes to analyse depends on a few factors; duration, audio channel count, etc.
 - Currently only tested on Linux (though should work on all OS).
