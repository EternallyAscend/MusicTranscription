import math
import matplotlib.pyplot as plt
import note_seq
import numpy as np
import librosa

SAMPLE_RATE = 44100
TARGET_RATE = 8000 # 16000

def read_wave(absolute_path, sample_rate):
    with open(absolute_path, "rb") as f:
        return note_seq.audio_io.wav_data_to_samples_librosa(f.read(), sample_rate=sample_rate)

def resample_wave(absolute_path, sample_rate, new_rate):
    file, _ = librosa.load(absolute_path, sr=sample_rate)
    new_file = librosa.resample(y=file, orig_sr=sample_rate, target_sr=new_rate)
    return new_file

def splite_wave_into_pieces(numpy_ndarray, sample_rate, gap):
    wave_length = math.ceil(len(numpy_ndarray) / sample_rate)
    frame_length = math.ceil(wave_length / gap)
    # print(wave_length, frame_length, math.ceil(wave_length), math.ceil(frame_length))
    fragments = []
    cursor = 1
    size = sample_rate * gap
    base = 0
    while cursor < frame_length:
        # for i in range(size):
        #     base + i
        fragments.append(numpy_ndarray[base:base+size])
        cursor += 1
        base += size
    fragments.append(numpy_ndarray[base:]) # TODO 是否选择在末尾补0
    print(len(numpy_ndarray[base:]))
    # print(size, len(fragments), len(fragments[0]))
    return fragments

def transfer_wave_fragments(fragments, sample_rate, n_fft):
    fft_fragments = []
    for f in fragments:
        fft_fragments.append(librosa.amplitude_to_db(np.abs(librosa.stft(y=f, n_fft=n_fft)), ref=np.max))
    return fft_fragments

def draw_wave_spectral_diagram(absolute_path, sample_rate, n_fft):
    file, _ = librosa.load(absolute_path, sr=sample_rate)
    plt.figure()
    data = librosa.amplitude_to_db(np.abs(librosa.stft(file, n_fft=n_fft)), ref=np.max)
    plt.subplot(2, 1, 1)
    librosa.display.specshow(data, y_axis='linear')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Linear-frequency power spectrogram')

    plt.subplot(2, 1, 2)
    librosa.display.specshow(data, y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log-frequency power spectrogram')
    plt.show()

def wave_audio_transcribe():
    pass

if "__main__" == __name__:
    audio = read_wave("../data/test6.wav", SAMPLE_RATE)
    print(type(audio), len(audio))
    print(audio)
    print()
    resample_wave("../data/test6.wav", SAMPLE_RATE, TARGET_RATE)
    fragments = splite_wave_into_pieces(audio, SAMPLE_RATE, gap=2)
    fft_fragments = transfer_wave_fragments(fragments, SAMPLE_RATE, n_fft=512)
    print(len(fft_fragments), len(fft_fragments[0]), fft_fragments[0])
    note_seq.play_sequence(audio, sample_rate=SAMPLE_RATE, colab_ephemeral=True)
