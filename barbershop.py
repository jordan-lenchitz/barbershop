import numpy as np
import warnings
from scipy.io import wavfile
from skimage import util
from scipy.signal import argrelextrema
from collections import Counter
from operator import itemgetter
from typing import List

def fission_cands(filename: str, frange: List[float] = [1000, 3000], W: int = 2**11) -> None:
    """
    function based on a rivalry model of prominence that takes a .wav file of a single chord
    and prints top four candidates for spectral fission in frangee
    
    Args:
        filename: '/path/to/file.wav' 
        frange: frequency range [min, max] in which to search for candidates
        W: FFT size = a power of 2 between 2**10 and 2**18
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rate, audio = wavfile.read(filename)

    # convert to mono if stereo
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    # ensure audio is float for signal processing
    if audio.dtype.kind != 'f':
        audio = audio.astype(np.float32) / np.iinfo(audio.dtype).max

    # window the audio data
    step = int(100 * W / 1024)
    if step < 1:
        step = 1
    
    windows = util.view_as_windows(audio, window_shape=(W,), step=step)
    win = np.hanning(W)
    windows = windows * win

    # compute FFT (rfft is efficient for real inputs)
    spectrum = np.fft.rfft(windows, n=W, axis=-1)
    
    # convert to dB
    S = np.abs(spectrum)
    max_S = np.max(S)
    if max_S > 0:
        S = 20 * np.log10(S / max_S)
    else:
        S = np.full_like(S, -120)
    S = np.clip(S, -120, None)

    # get frequencies
    freqs = np.fft.rfftfreq(W, d=1.0/rate)
    
    # frequency range masking
    min_idx, max_idx = np.searchsorted(freqs, frange)
    
    freq_counter = Counter()
    num_slices = S.shape[0]

    for i in range(num_slices):
        working = S[i, min_idx:max_idx]
        peaks = argrelextrema(working, np.greater)[0]
        
        # rivalry model = recursively filter peaks
        survivors = peaks.tolist()
        while len(survivors) > 8:
            peak_values = working[survivors]
            new_peak_indices = argrelextrema(peak_values, np.greater)[0]
            if new_peak_indices.size == 0:
                break
            survivors = [survivors[idx] for idx in new_peak_indices]
            
        for s_idx in survivors:
            freq_counter[round(freqs[min_idx + s_idx])] += 1

    # output results
    for freq, count in freq_counter.most_common(4):
        percentage = 100 * count / num_slices
        print(f"{int(freq)} Hz: {percentage:.1f}%")

def predict(upperfreqs: List[float], f_0: float, n: int = 4, fmin: float = 1000, limit: int = 16) -> None:
    """
    predicts n fission candidates above fmin by adding amplitudes of overlapping partials
    assumes harmonic spectra with amplitude 1/n for the nth partial
    """
    ratios = [1.0] + list(upperfreqs)
    results = Counter()
    
    for ratio in ratios:
        for j in range(1, limit + 1):
            results[ratio * j] += 1.0 / j
    
    candidates = [(r * f_0, amp) for r, amp in results.items() if r * f_0 > fmin]
    candidates.sort(key=itemgetter(1), reverse=True)
    
    for freq, amp in candidates[:n]:
        print(f"{int(round(freq))} Hz: {amp:.2f}")
