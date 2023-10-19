# MPV-LoudNorm
Automatic and non-destructive 2-pass loudnorm audio filter.

Rather than simply using the typical "af=lavfi=[loudnorm=I=-16.0:TP=-1.5:LRA=11.0]" filter found online in the mpv.conf, this script perfoms ebur128 and volumedetect to get the file's sound profile. The results are saved (to the same directory as the file being played) in a txt file, so analysis need not be re-run in the future.

Then based on the information in the txt file, a filter string is built and passed into mpv. Typical example "af=lavfi=[loudnorm=I=-5.0:TP=-2.0:LRA=11.0:measured_I=-19.5:measured_LRA=16.2:measured_TP=1:measured_thresh=-30.6]".

The HOTKEY to run this is 'n'.

NOTES:
The vast majority of functionality comes from Python. The MPV lua script simply calls the python script and grabs the outputted string from the command line.
Currently only tested on Windows 10.
