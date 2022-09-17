import numpy as np
import warnings
from scipy.io import wavfile
from skimage import util
from scipy.signal import argrelextrema
from collections import Counter
from operator import itemgetter

'''linked list setup'''
class Node:
    def __init__(self, data):
        self.item = data
        self.ref = None

class LinkedList:
    def __init__(self):
        self.start_node = None

    def traverse(self):
        if self.start_node is None:
            print('List has no elements')
            return
        else:
            n = self.start_node
            while n is not None:
                print(n.item , " ")
                n = n.ref
                
    def insert_at_start(self, data):
        new_node = Node(data)
        new_node.ref = self.start_node
        self.start_node= new_node

    def insert_at_end(self, data):
        new_node = Node(data)
        if self.start_node is None:
            self.start_node = new_node
            return
        n = self.start_node
        while n.ref is not None:
            n= n.ref
        n.ref = new_node

    def get_count(self):
        if self.start_node is None:
            return 0
        n = self.start_node
        count = 0
        while n is not None:
            count += 1
            n = n.ref
        return count

'''helper function that gets column indices for frequency range'''
def col_indices(array, minf, maxf):
    j = 0
    while j<1:
        for q in range(len(array[0])):
            if array[0,q] > minf:
                min_index = q-1
                j += 1
                break
    j = 0
    while j<1:
        for q in range(len(array[0])):
            if array[0,q] > maxf:
                max_index = q
                j += 1
                break
    return (min_index, max_index)

'''function based on a rivalry model of prominence that takes a .wav file of a single chord
and prints top four candidates for spectral fission in frange
W is FFT size, a power of 2 between 2**10 and 2**18
larger W gives sharper frequency resolution at the expense of time resolution'''
def fission_cands(filename, frange = [1000, 3000], W = 2**11):
    #read wav file and get sample rate in frames per second plus an array of its audio frames
    #ignore WavFileWarning because most wav files have harmless metadata that can't be removed
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  
        rate, audio = wavfile.read(filename)

    #average stereo channels to mono; does nothing if wav file is already mono
    audio = np.mean(audio, axis=1)

    #determine number of frames of audio
    N = audio.shape[0]

    #length in seconds = number of frames / frames per second
    L = N / rate

    #window the audio data using a Hann [aka raised cosine] window
    windows = util.view_as_windows(audio, window_shape=(W,), step=int(100 * W/(2**10)))
    win = np.hanning(W + 1)[:-1]
    windows = windows * win

    #transpose windows from rows to columns
    windows = windows.T

    #apply the DFT to each window of audio, slicing out the positive frequencies
    spectrum = np.fft.fft(windows, axis=0)[:W // 2 + 1:-1]

    #normalize data and convert to dB
    S = np.abs(spectrum)
    S = 20 * np.log10(S / np.max(S))
    S = np.clip(S, -120, None)

    #tranpose array so frequency is columns and time is rows
    S = S.T

    #get number of slices
    time_slices, freq_slices = S.shape

    #insert frequencies (in Hz) as 0th row of array
    S = np.insert(S, 0, [(i+1)*rate/(2*freq_slices) for i in range(freq_slices)], 0)

    #insert times (in seconds) as 0th column of array
    S = np.insert(S, 0, [i * L/time_slices for i in range(time_slices+1)], 1)

    #get column indices for frequency range and create frequency counter
    a,b = col_indices(S, frange[0], frange[1])
    freq_counter = Counter()

    #in each time slice, recursively compare relative maxima in gain
    #add results (up to 8 winners) to the frequency counter (rounded to the nearest Hz)
    for number in range(1, len(S[:,0])):
        working = S[number][a:b]
        j = argrelextrema(working, np.greater)[0]
        lll = []
        for thing in np.nditer(j):
            exec('ll_' + str(thing) + ' = ' + 'LinkedList()')
            exec('ll_' + str(thing) + '.insert_at_start(' + str(thing) + ')')
            exec('lll.append(ll_' + str(thing) + ')')
        while len(lll) > 8: 
            j = argrelextrema(np.array([working[thing] for thing in np.nditer(j)]), np.greater)[0]
            if j.shape[0] == 0:
                break
            else:
                for thing in np.nditer(j):
                        exec('lll[' + str(thing) + '].insert_at_end(' + str(thing) + ')')
                maxlength = max([thing.get_count() for thing in lll])
                for thing in lll[:]:
                    if thing.get_count() < maxlength:
                        lll.remove(thing)
        for thing in lll:
            freq_counter[round(S[0,(thing.start_node.item+a)],0)] += 1

    #print the four frequences that win in the most time slices
    #and the percentage of time slices in which they win
    for thing in freq_counter.most_common(4):
        print(int(thing[0]), ' Hz: ', round(100*thing[1]/time_slices, 1), '%', sep='')
        
'''function that predicts n fission candidates above fmin by adding amplitudes of overlapping partials
assumes harmonic spectra with amplitude 1/n for the nth partial
upperfreqs is a list of the upper pitches' frequencies as ratios relative to the lowest being 1/1
(so a major triad might be either [3/2, 2, 5/2] or [5/2, 4, 6] depending on spacing)
f_0 is the frequency of the lowest pitch (= 1/1)
limit is the highest partial to include in the calculation'''
def predict(upperfreqs, f_0, n=4, fmin=1000, limit=16):
    frac, partials = [1], []
    for thing in upperfreqs:
        frac.append(thing)
    for thing in frac:
        for j in range(1, limit+1):
            partials.append((j*thing, 1/j))
    results = Counter()
    for thing in partials:
        results[thing[0]] += thing[1]
    candidates = [(thing, results[thing]) for thing in results if thing*f_0 > fmin]
    for thing in sorted(candidates, key = itemgetter(1), reverse = True)[:n]:
        print(int(thing[0]*f_0), ' Hz: ', "{0:.2f}".format(thing[1]), sep='')
