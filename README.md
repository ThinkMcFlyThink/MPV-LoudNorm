# MPV-LoudNorm
Automatic and non-destructive 2-pass loudnorm audio filter for the MPV player (https://mpv.io/).

Rather than simply using the typical `af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0]` filter found online in the mpv.conf, this script perfoms ebur128 and volumedetect to get the file's sound profile - making it more accurate. The results are saved as a txt file in the same directory as the file being played, therefore analysis does not need be re-run in the future.

Then based on the information in the txt file, a filter string is built and passed into mpv. Typical example `af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0:measured_I=-19.5:measured_LRA=16.2:measured_TP=-1.1:measured_thresh=-30.6]`.

The HOTKEY to execute the script is 'n'.

NOTES:
 - The vast majority of functionality comes from Python. The MPV lua script simply calls the python script and grabs the outputted string from the command line.
 - How long it takes to analyse depends on a few factors; runtime, channels, etc. Typically no more than 2mins.
 - Currently only tested on Windows 10.
 - Currently very clunky...
