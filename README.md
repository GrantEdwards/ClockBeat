# ClockBeat
Python app to analyze audio recordings of clock beat

## Description

This is a Python application intended to help you adjust a pendulum
clock (e.g. a grandfather clock). It processes an audio recording of
the clock's "tick-tock" sound to help you determine two things.

### 1. Beats Per Hour

If you know the movement's design BPH value, you can compare the
calculated BPH from the audio recording to determine if the pendulum
needs to be longer or shorter.  To get an accurate BPH calculation,
you probably want a recording that's at least a few minutes long (the
longer the recording, the more accurate the BPH calculation).  Once
you get it close, the audio recording method probably isn't accurate
enough for fine-tuning, and you're better off just setting the clock
from a reference and then checking/adjusting it once a day until it's
right.

### 2. In Beat vs. Out of Beat

A clock is "in beat" when the time interval from tick to tock is the
same as the time interval from tock to tick. If a clock is badly out
of beat, then it will sound like "tick tock pause tick tock pause ..."
or "tick pause tock tick pause tock tick...". If a clock is out of
beat, the escapement's little pushes on the pendulum aren't happening
at the optimal points in the pendulum's trajectory, and energy is
being wasted. Clocks that are out of beat will often run for a while
and then simply stop.

Clocks can be out of beat because they are out of plumb or because the
crutch lever needs to be adjusted. [Or both.] On many clocks, "adjusting"
simply means gently bending something.

## Usage

### Dependencies

The program requires the ffmpeg command-line utility which it uses to
apply gain and channel selection to the audio recording by invoking
ffmpeg via os.system(). This has been tested only on Linux. I don't
know enough about Windows to predict whether or not this will work,
but probably not. It might work on OS-X.

Other than the external ffmpeg utility, it uses only the Python
standard library and matplotlib.

### Recording

First, you need to make as clean an audio recording of the clock
movement's tick-tock sound as possible. If you end up with extraneous
sounds at the start or end, use an audio editing program
(e.g. Audacity) to trim the recording.  When you save the recording,
preserve as much dynamic range as possible by saving it in a format
like MP3 or AAC rather than WAV.

### Invocation

After you've saved the audio file, invoke the application like this
(examples are on Unix, and the '$' is the command prompt):

~~~
$ ./beat.py <audio-file-name>
~~~

After a few seconds, a plot window will show up. The upper subplot
shows the rectified audio data (blue), the envelope waveform
(orange) and the detected beats (green).  The lower subplot shows the 
time intervals between tick-tock and tock-tick in blue and orange.

Here's a sample plot:

![Saturday_11:54pm.m4a.png](imgs/Saturday_11:54pm.m4a.svg?raw)

Ideally there would be no space between the orange and blue lines in
the lower subplot, but this plot isn't too bad.

Zooming in shows the three waveforms more clearly:

![Saturday_11:54pm.m4a-zoomed.svg](imgs/Saturday_11:54pm.m4a-zoomed.svg?raw)

### Gain and Threshold

You'll probably have to adjust the gain and threshold values until you
find the right combination for your recording device and clock. Those
are changed using the -g/--gain and -t/--threshold command line
arguments:

~~~
$ ./beat.py -h
usage: ./beat.py [-h] [-g GAIN] [-t THRESH] [-b BPH] [-c CHAN] [-s file] filename

Show clock beats

positional arguments:
  filename

options:
  -h, --help            show this help message and exit
  -g GAIN, --gain GAIN  gain in dB (default: 20)
  -t THRESH, --threashold THRESH
                        tick detect threshold (default: 8000)
  -b BPH, --bph BPH     target BPH (default: None)
  -c CHAN, --channel CHAN
                        audio channel number from input stream (default: 0)
  -s file, --save FILE  save svg plot in <filename> (default: None)
~~~

Here's a recording where the default values don't work well:

![Saturday_7:16pm.m4a.svg](imgs/Saturday_7:16pm.m4a.svg?raw)

The gain is OK (you probably want peaks of at least a few thousand
counts above the noise floor). But the default threshold of 8000 is
too high, and only one beat was detected (at the 3s point).  You want
to pick a threshold that's a bit below the lowest orange peak
value. We'll try 4000:

 ![t4000-Saturday_7:16pm.m4a.svg](imgs/t4000-Saturday_7:16pm.m4a.svg?raw)

That produces good beat detection. The consistent separation between
the two lines in the lower subplot indicates that the clock is out of
beat. In this case, the clock was slightly off plumb.  The movement's
design BPH was 4050, so it's also running quite fast. In this case the
plumb bob was incorrectly attached resulting in a pendulum that was
too short.

Here's are recording where many beats are detected, but some aren't:

![Monday_9:33pm.m4a.svg](imgs/Monday_9:33pm.m4a.svg?raw)
 
Again, the threshold needs to be lowered (or the gain increased). In
this case, there's some garbage at the end of the recording, so we
want to choose a threshold that will ignore that garbage. We'll try a
threshold of 6000:

![t6000-Monday_9:33pm.m4a.svg](imgs/t6000-Monday_9:33pm.m4a.svg?raw)


Now beats are correctly detected, but this is that same clock that's
noticeably out of beat. When it's this bad, it's pretty easy to tell by
ear.

### Target BPH

If you provide a target BPH value using the -b/--bph command line
option, that value will be included in the plot title and a dotted
line will be drawn on the lower subplot showing the correct beat
interval for that BPH value:

![t5000-b4050-Saturday_8:12pm.m4a.svg](imgs/t5000-b4050-Saturday_8:12pm.m4a.svg?raw)

### Stereo Recordings

By default, the program will use channel 0 of a multi-channel
recording. If you want to use a different channel, you can use the
-c/--channel command line option.
