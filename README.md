# barbershop
Two models of spectral fission in barbershop harmony; for better results consider their overlap.

Presented as a 20-minute talk at <a href="https://www.scsmt.org/conferences/scsmt-2020/">SCSMT 2020</a>, where it won the Best Student Paper Award; <a href="https://www.mtmw.org/index.php/conferences/programs?year=2020/">MTMW 2020</a>; <a href="https://musictheorysoutheast.com/2020-conference-program/">MTSE 2020</a>; and <a href="http://www.musictheorymidatlantic.org/2020/OnlineConference.html">MTSMA 2020</a>. Presented as a poster at <a href="https://societymusictheory.org/meetings/ams-smt-2020">SMT 2020</a>. See <a href="https://github.com/jordan-lenchitz/barbershop/blob/master/Spectral%20Fission%20in%20Barbershop%20Harmony.pdf">paper</a> and/or <a href="https://www.youtube.com/watch?v=zJOCxsJA1LA">20-minute video</a>. 

Necessary modules: numpy, warnings, scipy, skimage, collections, operator

fission_cands is a descriptive signal processing script based on a simple rivalry ("March Madness") model of prominence that takes a .wav file of a single chord and prints top four candidate frequencies for pitches of spectral fission in a given frequency range. Starting from a 2048-point FFT yielding spectra for .004-second samples, all relative maxima in amplitude are recursively compared to their nearest neighbor relative maxima until no more than 8 remain per sample. The top four candidates are those that remain in the most samples.

Syntax: fission_cands(filename, frange = [1000, 3000], W = 2**11)

filename is the .wav of the chord in question, e.g. 'my_chord.wav'

frange is the frequency range in which candidates will be found, e.g. [1000, 3000] for 1000-3000 Hz

W is FFT size: power of 2 (minimum 2^10, maximum 2^18); smaller = faster runtime and sharper time resolution, larger = slower runtime and sharper frequency resolution

Example: predict candidate frequencies for pitches of spectral fission for 'my_chord.wav' between 800 and 4000 Hz using a 4096-point FFT 
>fission_cands('my_chord.wav', [800, 4000], 2**12)

predict is a vowel-neutral model of spectral overlap based on a simple model of vocal timbre (harmonic spectra with amplitude 1/n for the nth partial). Working from the sung fundamental frequencies of each quartet member it predicts frequencies in a given range that will have the most amplitude, assuming formants tuned to partials are tuned to frequencies of maximal spectra overlap.

Syntax: predict(upperfreqs, f_0, n=4, fmin=1000, limit=16)

upperfreqs is a list of the upper pitches' frequencies as vertical just intonation ratios relative to the lowest being 1/1; a major triad could thus be either [3/2, 2, 5/2] or [5/2, 4, 6] or [5/4, 3/2, 2] depending on spacing

f_0 is the frequency of the lowest pitch (= 1/1)

n is the number of fission candidates above fmin to be generated

fmin is the frequency above which candidates will be calculated

limit is the highest partial to include in the calculation

Example: predict 6 candidates above 800 Hz for a C major chord in close spacing (root 3rd 5th root all within one octave) and lowest pitch 262 Hz and including 15 partials above the fundamentals
>predict([5/4, 3/2, 2], 262, 6, 800, 16)
