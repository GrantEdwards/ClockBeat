#!/usr/bin/python

import sys, os, struct, wave, tempfile, argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    description='Show clock beats',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('filename')
parser.add_argument('-g', '--gain', dest='gain', type=int, default=20, help='gain in dB')
parser.add_argument('-t', '--threashold', dest='thresh', type=int, default=8000, help='tick detect threshold')
parser.add_argument('-b', '--bph', dest='bph', type=float, default=None, help='target BPH')
parser.add_argument('-c', '--channel', dest='chan', type=int, default=0, help='audio channel number from input stream')
parser.add_argument('-s', '--save', metavar='file', dest='save', type=str, default=None, help='save svg plot in <filename>')

args = parser.parse_args()

# windowed average
def average(data, width):
    window = [0] * width;
    def f(v):
        nonlocal window
        window.pop(0)
        window.append(abs(v))
        return sum(window)/width
    return [f(v) for v in data]

# windowed peak detect
def peak(data, width):
    window = [0] * width
    def f(v):
        nonlocal window
        window.pop(0)
        window.append(abs(v))
        return max(window)
    return [f(v) for v in data]

# pulse at threshold
def pulse(data):
    thcount = 0
    def f(v):
        nonlocal thcount
        if v > args.thresh:
            thcount = 10000
        if thcount:
            thcount -= 1
            return args.thresh
        return 0
    return [f(v) for v in data]

# use ffmpeg to convert input audio file to mono wav format, then read
# wav file into list of ints

with tempfile.TemporaryDirectory() as tmpdir:
    outfile = f'{tmpdir}/{args.filename}.wav'
    if os.system(f'ffmpeg -loglevel error -stats -i {args.filename} -af "pan=mono|c0=c{args.chan}, volume={args.gain}dB" {outfile}'):
        print("ffmpeg error")
        sys.exit(1)
    with wave.open(outfile,'rb') as w:
        nchannels, sampwidth, framerate, nframes, comptype, compname = w.getparams()
        assert nchannels == 1
        assert sampwidth == 2
        data = struct.unpack(f'{nframes}h',w.readframes(nframes))
        
absdata = [abs(v) for v in data]
envdata = average(peak(absdata,10),30)
pulsedata = pulse(envdata)

edges = [i for i in range(1,len(pulsedata)) if pulsedata[i] > 0 and pulsedata[i-1] == 0]

if len(edges) < 2:
    bphstr = "beats not detected"
    deltas = []
else:    
    deltas = [edges[i]-edges[i-1] for i in range(1,len(edges))]

    # convert deltas from sample periods to seconds
    deltas = [v/framerate for v in deltas]

    # calculate bph based on total delta T and number of beats, but we always want an even number of beats
    # so that we don't have an error due to assymetry.
    if len(edges) % 2:
        del edges[-1]
    bph = 3600/(((edges[-1] - edges[0])/(len(edges)-1))/framerate)
    bphstr  = f'{bph:0.1f} BPH'

# now plot the raw/processed data and the tic/tok delta T values

           
fig,sub = plt.subplots(2, figsize=(8,8))

title = f'{args.filename} -- {bphstr}'
subtitle =  f'gain: {args.gain}dB, threshold: {args.thresh}'
if args.bph is not None:
    subtitle += f', target: {args.bph} BPH'

fig.suptitle(f'{title} \n {subtitle}')

xvals = [i/framerate for i in range(len(absdata))]

# plot absolute value, envelope, and pulses at threshold crossing

sub[0].plot(xvals,absdata)
sub[0].plot(xvals,envdata)
sub[0].plot(xvals,pulsedata)

if deltas:
    # plot tic-tok and tok-tic deltas in seconds
    #
    # if target bph was provided, center y axis there (and draw dotted
    # line at target bph), otherwise center y axis on actual bph

    if args.bph is None:
        center = 3600/bph
    else:
        center = 3600/args.bph
    sub[1].set_ylim(center*0.8, center*1.2)
    if args.bph is not None:
        sub[1].axhline(y=center, linestyle=':')
    sub[1].plot(deltas[0::2])
    sub[1].plot(deltas[1::2])

if args.save is not None:
    plt.savefig(args.save, format='svg')
        
try:
    plt.show()
except KeyboardInterrupt:
    pass
