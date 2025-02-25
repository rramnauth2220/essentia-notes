# essentia
import essentia # as es
from essentia.standard import *
import essentia.standard as es

# librosa
import librosa
import librosa.display

# file support
import os
from os import listdir
from os.path import isfile, join, basename, splitext

# analysis
import IPython
import numpy as np
import pandas as pd
import scipy
import sklearn

# plots
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("ticks")
sns.set_palette("bright")

##################################################
#             PARSING WITH ESSENTIA              #
##################################################
def extract_essentia_features(audio):
    spectral_df = pd.DataFrame()
    try:
        features, feature_frames = es.MusicExtractor(
            lowlevelStats=['mean', 'stdev', 'var', 'median', 'skew', 'kurt', 'dmean', 'dvar', 'dmean2', 'dvar2', 'cov', 'icov'],
            rhythmStats=['mean', 'stdev', 'var', 'median', 'skew', 'kurt', 'dmean', 'dvar', 'dmean2', 'dvar2', 'cov', 'icov'],
            tonalStats=['mean', 'stdev', 'var', 'median', 'skew', 'kurt', 'dmean', 'dvar', 'dmean2', 'dvar2', 'cov', 'icov'])(audio)
    except Exception as ex:
        print(ex)
        return 'silent'    
    
    feature_vals = []
    
    for feature in features.descriptorNames():
        if isinstance(features[feature], (float, int)):
            spectral_df[feature] = 0.
            feature_vals.append(features[feature])
        else: break
            
    spectral_df.loc[0] = feature_vals
    ''' # HANDLING ERROR USING PLACEHOLDER AUDIO
    except Exception as ex:
        features, _ = es.MusicExtractor(
        lowlevelStats=['mean', 'stdev', 'var', 'median', 'skew', 'kurt', 'dmean', 'dvar', 'dmean2', 'dvar2', 'cov', 'icov'],
        rhythmStats=['mean', 'stdev', 'var', 'median', 'skew', 'kurt', 'dmean', 'dvar', 'dmean2', 'dvar2', 'cov', 'icov'],
        tonalStats=['mean', 'stdev', 'var', 'median', 'skew', 'kurt', 'dmean', 'dvar', 'dmean2', 'dvar2', 'cov', 'icov'])("recordings/placeholder.wav")
        
        # fill column with feature names and cells with 0
        for feature in features.descriptorNames():
            if isinstance(features[feature], (float, int)):
                spectral_df[feature] = 0.
            else: break
                
        # spectral_df.loc[0] = feature_vals
        print("Trying to estimate tuning from empty frequency set. Using placeholder audio instead to get feature names.")
    '''
    return spectral_df.fillna(spectral_df.mean())

##################################################
#             PARSING WITH LIBROSA               #
##################################################

def create_chroma_df(chroma):
    chroma_mean = np.mean(chroma, axis = 1)
    chroma_std = np.std(chroma, axis = 1)
    
    chroma_df = pd.DataFrame()
    for i in range(0,12):
        chroma_df['chroma ' + str(i) + ' mean'] = chroma_mean[i]
        chroma_df['chroma ' + str(i) + ' std'] = chroma_std[i]
    chroma_df.loc[0] = np.concatenate((chroma_mean, chroma_std), axis = 0)

    return chroma_df

def create_mfccs_df(mfccs):
    mfccs_mean = np.mean(mfccs, axis = 1)
    mfccs_std = np.std(mfccs, axis = 1)
   
    mfccs_df = pd.DataFrame()
    for i in range(0,13):
        mfccs_df['mfccs ' + str(i) + ' mean'] = mfccs_mean[i]
        mfccs_df['mfccs ' + str(i) + ' std'] = mfccs_std[i]
    mfccs_df.loc[0] = np.concatenate((mfccs_mean, mfccs_std), axis = 0)
    
    return mfccs_df

def create_rms_df(rms):
    rms_mean = np.mean(rms)
    rms_std = np.std(rms)
    rms_skew = scipy.stats.skew(rms, axis = 1)[0]
    
    rms_df = pd.DataFrame()
    rms_df['rms mean'] = rms_mean
    rms_df['rms std'] = rms_std
    rms_df['rms skew'] = rms_skew
    rms_df.loc[0] = np.concatenate((rms_mean, rms_std, rms_skew), axis = 0)
    
    return rms_df

def create_spectral_df(cent, contrast, rolloff, flatness):
    
    # spectral centroids values
    cent_mean = np.mean(cent)
    cent_std = np.std(cent)
    cent_skew = scipy.stats.skew(cent, axis = 1)[0]

    # spectral contrasts values
    contrast_mean = np.mean(contrast, axis = 1)
    contrast_std = np.std(contrast, axis = 1)
    
    # spectral rolloff points values
    rolloff_mean = np.mean(rolloff)
    rolloff_std = np.std(rolloff)
    rolloff_skew = scipy.stats.skew(rolloff, axis = 1)[0]
    
    # spectral flatness values
    flat_mean = np.mean(flatness)
    flat_std = np.std(flatness)
    flat_skew = scipy.stats.skew(flatness, axis = 1)[0]

    spectral_df = pd.DataFrame()
    collist = ['cent mean','cent std','cent skew',
               'flat mean', 'flat std', 'flat skew',
               'rolloff mean', 'rolloff std', 'rolloff skew']
    for i in range(0,7):
        collist.append('contrast ' + str(i) + ' mean')
        collist.append('contrast ' + str(i) + ' std')
    
    for c in collist:
        spectral_df[c] = 0
    data = np.concatenate((
        [cent_mean, cent_std, cent_skew], 
        [flat_mean, flat_std, flat_skew],
        [rolloff_mean, rolloff_std, rolloff_skew], 
        contrast_mean, contrast_std),
        axis = 0)
    spectral_df.loc[0] = data
    
    return spectral_df

def create_zrate_df(zrate):
    zrate_mean = np.mean(zrate)
    zrate_std = np.std(zrate)
    zrate_skew = scipy.stats.skew(zrate, axis = 1)[0]

    zrate_df = pd.DataFrame()
    zrate_df['zrate mean'] = 0
    zrate_df['zrate std'] = 0
    zrate_df['zrate skew'] = 0
    zrate_df.loc[0]=[zrate_mean, zrate_std, zrate_skew]
    
    return zrate_df

def create_beat_df(tempo):
    beat_df = pd.DataFrame()
    beat_df['tempo'] = tempo
    beat_df.loc[0] = tempo
    return beat_df

def extract_librosa_features(audio):
    y, sr = librosa.load(audio, sr=44100)
    y_harmonic = y
    #y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    tempo, beat_frames = librosa.beat.beat_track(y=y_harmonic, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    beat_time_diff = np.ediff1d(beat_times)
    beat_nums = np.arange(1, np.size(beat_times))
    
    chroma = librosa.feature.chroma_cens(y=y_harmonic, sr=sr)
    
    mfccs = librosa.feature.mfcc(y=y_harmonic, sr=sr, n_mfcc=13)
    
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    
    flatness = librosa.feature.spectral_flatness(y=y)
    
    contrast = librosa.feature.spectral_contrast(y=y_harmonic,sr=sr)
    
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    
    zrate = librosa.feature.zero_crossing_rate(y_harmonic)
    
    chroma_df = create_chroma_df(chroma)
    
    mfccs_df = create_mfccs_df(mfccs)
    
    spectral_df = create_spectral_df(cent, contrast, rolloff, flatness)
    
    zrate_df = create_zrate_df(zrate)
    
    beat_df = create_beat_df(tempo)
    
    final_df = pd.concat((chroma_df, mfccs_df, spectral_df, zrate_df, beat_df), axis = 1)
    
    return final_df

##################################################
#               QUANTIFYING HUMS                 #
##################################################

# dependencies
# import essentia.standard as es
import numpy as np
import matplotlib.pyplot as plt
# from essentia import Pool
# from essentia import db2amp
from IPython.display import Audio 

# an auxiliar function for plotting spectrograms
def spectrogram(audio, frameSize=1024, hopSize=512, db=True):
    eps = np.finfo(np.float32).eps
    window = es.Windowing(size=frameSize)
    spectrum = es.PowerSpectrum(size=frameSize)
    pool = Pool()
    for frame in es.FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize, startFromZero=True):
        pool.add('spectrogram', spectrum(window(frame)))

    if db:
        return 10 * np.log10(pool['spectrogram'].T + eps)
    else:
        return pool['spectrogram'].T   

def generate_hum_plots(audio, matrices, quantiles):
    f, ax = plt.subplots(len(matrices), figsize=(15, 12))
    f0 = 0
    fn = 1000
    fs = 44100.
    out_fs = 2000
    
    for i in range(0, len(matrices)):
        ax[i].imshow(matrices[i], aspect='auto', origin='lower', extent=[0 , matrices[i].shape[1] * .2, f0, fn])
        ax[i].set_title('Q0 = ' + str(quantiles[i][0]) + ', Q1 = ' + str(quantiles[i][1]))
    
    return plt

# hum = discontinuities of frequencies [22.5, 400)
def calculate_hum(audio, quantiles):
    audio_with_hum = es.MonoLoader(filename=audio)()
    quantile_ratios = []
    frequencies = []
    saliences = []
    hum_starts = []
    hum_ends = []
    
    for quantile in quantiles: 
        # try:
        r, freq, sal, starts, ends = es.HumDetector(Q0=quantile[0], Q1=quantile[1])(audio_with_hum)
        quantile_ratios.append(r)
        frequencies.append(freq)
        saliences.append(sal)
        hum_starts.append(starts)
        hum_ends.append(ends)
        '''
        except Exception as ex:
            print("Issue calculating hum:", type(ex))
            quantile_ratios.append(0)
            frequencies.append(0)
            saliences.append(0)
            hum_starts.append([])
            hum_ends.append([])
        '''
    return quantile_ratios, frequencies, saliences, hum_starts, hum_ends

def calculate_hum_features(quantiles, ratios, frequencies, saliences, starts, ends):
    features = ['length', 'frequency', 'salience']
    hum_metrics = []
    hum_quartile_vals = []
    
    for q, f, s, ss, es in zip(quantiles, frequencies, saliences, starts, ends):
        # generate dataframe column names
        hum_metrics.append('hum_(Q0='+str(q[0])+',Q1='+str(q[1])+')_instances')
        for feature in features: # per statistical feature
            q_descriptor = 'hum_(Q0='+str(q[0])+',Q1='+str(q[1])+')_'+feature+'.'
            hum_metrics.extend(q_descriptor + metric for metric in ['mean', 'stdev', 'skew'])
        
        # compute statistical features on hum lengths
        hum_lengths = []
        zip_stamps = zip(ss, es)
        q_count = len(ss)
        for start, end in zip_stamps:
            hum_lengths.append(end-start)
        q_length_mean = np.mean(hum_lengths)
        q_length_stdev = np.std(hum_lengths)
        q_length_skew = scipy.stats.skew(hum_lengths)
        
        # compute statistical features on hum frequencies
        q_freq_mean = np.mean(f)
        q_freq_stdev = np.std(f)
        q_freq_skew = scipy.stats.skew(f)
        
        # compute statistical features on hum saliences
        q_sal_mean = np.mean(s)
        q_sal_stdev = np.std(s)
        q_sal_skew = scipy.stats.skew(s)
        
        # add metrics to vector
        hum_quartile_vals.extend((
            q_count, 
            q_length_mean, q_length_stdev, q_length_skew,
            q_freq_mean, q_freq_stdev, q_freq_skew,
            q_sal_mean, q_sal_stdev, q_sal_skew
        ))
        
    hum_dict = dict(zip(hum_metrics, hum_quartile_vals)) # pair column names and values as a dictionary
    hum_df = pd.DataFrame(hum_dict, index=[0]) # convert to data frame
    return hum_df

def extract_hum_features(audio, quantiles):
    rs, freqs, sals, starts, ends = calculate_hum(audio, quantiles)
    #generate_hum_plots(audio, rs, quantiles)
    hum_df = calculate_hum_features(quantiles, rs, freqs, sals, starts, ends).fillna(0)
    return hum_df

##################################################
#           DETECTING DISCONTINUITIES            #
##################################################

# dependencies
# import essentia.standard as es
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio 
# from essentia import array as esarr

# a stand-alone detector method
def compute_discontinuities(audio, frame_size=1024, hop_size=512, **kwargs):
    x = es.MonoLoader(filename=audio)()
    discontinuityDetector = es.DiscontinuityDetector(frameSize=frame_size, hopSize=hop_size, **kwargs)
    locs = []
    amps = []
    for idx, frame in enumerate(es.FrameGenerator(x, frameSize=frame_size, hopSize=hop_size, startFromZero=True)):
        frame_locs, frame_ampls = discontinuityDetector(frame)

        for l in frame_locs:
            locs.append((l + hop_size * idx) / 44100.)
        for a in frame_ampls:
            amps.append(a)

    return locs, amps

def generate_discontinuity_plot(locs, audio):
    fs = 44100.
    x = es.MonoLoader(filename=audio)()
    fig, ax = plt.subplots(len(locs))
    plt.subplots_adjust(hspace=.4)
    times = np.linspace(0, len(x) / fs, len(x))
    for idx, point in enumerate(locs):
        ax[idx].axvline(locs[idx], color='black', alpha=.25)
        ax[idx].plot(times, x)
        ax[idx].set_xlim([point-.001, point+.001])
        ax[idx].set_title('Click located at {:.2f}s'.format(point))
    
    return plt

def calculate_discontinuity_features(locs, amps):
    dis_metrics = {
        'discontinuity_instances': len(locs), 
        'discontinuity_locations.mean': np.mean(locs),
        'discontinuity_locations.stdev': np.std(locs),
        'discontinuity_locations.skew': scipy.stats.skew(locs),
        'discontinuity_amplitudes.mean': np.mean(amps),
        'discontinuity_amplitudes.stdev': np.std(amps),
        'discontinuity_amplitudes.skew': scipy.stats.skew(amps)
    }
    
    dis_df = pd.DataFrame(dis_metrics, index=[0]) # convert to data frame
    return dis_df

def extract_discontinuity_features(audio):
    locs, amps = compute_discontinuities(audio)
    dis_df = calculate_discontinuity_features(locs, amps).fillna(0)
    return dis_df

##################################################
#               QUANTIFYING CLICKS               #
##################################################

# dependencies
# import essentia.standard as es
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio 
# from essentia import array as esarr

# a stand-alone detector method
def compute_clicks(audio, frame_size=1024, hop_size=512, **kwargs):
    x = es.MonoLoader(filename=audio)()
    clickDetector = es.ClickDetector(frameSize=frame_size, hopSize=hop_size, **kwargs)
    ends = []
    starts = []
    for frame in es.FrameGenerator(x, frameSize=frame_size,
                                   hopSize=hop_size, startFromZero=True):
        frame_starts, frame_ends = clickDetector(frame)

        for s in frame_starts:
            starts.append(s)
        for e in frame_ends:
            ends.append(e)

    return starts, ends

def generate_clicks_plot(starts, ends, audio):
    fs = 44100.
    x = es.MonoLoader(filename=audio)()

    times = np.linspace(0, len(x) / fs, len(x))
    plt.plot(times, x)
    for point_s, point_e in zip(starts, ends):
        #l1 = plt.axvline(point_s, color='red', alpha=.5)
        #l2 = plt.axvline(point_e, color='blue', alpha=.5)
        l1 = plt.axvspan(point_s, point_e, alpha=0.5, color='red')

    l1.set_label('Click locations')
    #l1.set_label('Click starts')
    #l2.set_label('Click ends')
    plt.legend()
    return plt

def calculate_clicks_features(starts, ends):
    durations = []
    for s, e in zip(starts, ends):
        duration = e - s
        durations.append(duration)
        
    clicks_metrics = {
        'clicks_instances': len(starts), 
        'clicks_starts.mean': np.mean(starts),
        'clicks_starts.stdev': np.std(starts),
        'clicks_starts.skew': scipy.stats.skew(starts),
        'clicks_durations.mean': np.mean(durations),
        'clicks_durations.stdev': np.std(durations),
        'clicks_durations.skew': scipy.stats.skew(durations)
    }
    
    clicks_df = pd.DataFrame(clicks_metrics, index=[0]) # convert to data frame
    return clicks_df

def extract_clicks_features(audio):
    starts, ends = compute_clicks(audio)
    clicks_df = calculate_clicks_features(starts, ends).fillna(0)
    return clicks_df

##################################################
#           CALCULATING ENERGY BALANCE           #
##################################################

# output the ebm calculation for a single file as a dataframe (e.g., column: 'ebm')
def extract_ebm_features(audio):
    
    ebm_metrics = {
        'ebm.value': float(audio), 
        'ebm.lower_bound': 20,
        'ebm.upper_bound': 250
    }
    
    ebm_df = pd.DataFrame(ebm_metrics, index=[0])
    return ebm_df

##################################################
#         EXTRACTING BY FREQUENCY BANDS          #
##################################################

from scipy.signal import freqz, butter, lfilter
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def plot_order_frequency_reponses(lowcut, highcut, fs, orders):
    plt.clf()
    for order in orders:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000)
        plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')
    return plt

def plot_effect(original, filtered, fs):
    plt.figure(figsize=(15, 5))
    librosa.display.waveplot(original, sr=fs, alpha=0.25)
    librosa.display.waveplot(filtered, sr=fs, color='red', alpha=0.5)
    plt.title("Original + Filtered Signals")
    return plt

def filter_signal(signal, lowcut, highcut, write_output = '', fs=44100.0):
    y = butter_bandpass_filter(signal, lowcut, highcut, fs, order=2)
    if write_output: 
        try: 
            sf.write(write_output, y, fs)
        except Exception as e:
            print("Cannot write to", write_output, ". Invalid file name passed.")
    return y
    
def extract_freq_band(inputAudio, lowcut, highcut, outputDir):
    original, fs = librosa.load(inputAudio)
    filtered = filter_signal(original, lowcut, highcut, outputDir, fs)
    return filtered

