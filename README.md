# barbershop
A model of spectral fission in barbershop harmony.

Presented as a 20-minute talk at <a href="https://www.scsmt.org/conferences/scsmt-2020/">SCSMT 2020</a>, where it won the Best Student Paper Award; <a href="https://www.mtmw.org/index.php/conferences/programs?year=2020/">MTMW 2020</a>; <a href="https://musictheorysoutheast.com/2020-conference-program/">MTSE 2020</a>; and <a href="http://www.musictheorymidatlantic.org/2020/OnlineConference.html">MTSMA 2020</a>. Presented as a poster at <a href="https://societymusictheory.org/meetings/ams-smt-2020">SMT 2020</a>. See <a href="https://github.com/jordan-lenchitz/barbershop/blob/master/Spectral%20Fission%20in%20Barbershop%20Harmony.pdf">paper</a> and/or <a href="https://www.youtube.com/watch?v=zJOCxsJA1LA">20-minute video</a>. 

Necessary modules: numpy, warnings, scipy, skimage, collections, operator

fission_cands is a descriptive signal processing script based on a simple rivalry ("March Madness") model of prominence that takes a .wav file of a single chord and prints top four candidate frequencies for pitches of spectral fission in frange. Starting from a 2048-point FFT yielding spectra for .004-second samples, all relative maxima in amplitude are recursively compared to their nearest neighbor relative maxima until no more than 8 remain per sample. The top four candidates are those that remain in the most samples.

Syntax: fission_cands(filename, frange = [1000, 3000], W = 2**11)
filename is the .wav of the chord in question, e.g. 'my_chord.wav'

frange is the frequency range in which candidates will be found, e.g. [1000, 3000] for 1000-3000 Hz

W is FFT size: power of 2 (minimum 2^10, maximum 2^18); smaller = faster runtime and sharper time resolution, larger = slower runtime and sharper frequency resolution

