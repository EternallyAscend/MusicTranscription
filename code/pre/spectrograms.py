"""Audio spectrogram functions."""

import dataclasses
import librosa

from ddsp import spectral_ops
import numpy as np

from config import Consts

@dataclasses.dataclass
class SpectrogramConfig:
  """Spectrogram configuration parameters."""
  sample_rate: int = Consts.DEFAULT_SAMPLE_RATE
  hop_width: int = Consts.DEFAULT_HOP_WIDTH
  num_mel_bins: int = Consts.DEFAULT_NUM_MEL_BINS

  @property
  def abbrev_str(self):
    s = ''
    if self.sample_rate != Consts.DEFAULT_SAMPLE_RATE:
      s += 'sr%d' % self.sample_rate
    if self.hop_width != Consts.DEFAULT_HOP_WIDTH:
      s += 'hw%d' % self.hop_width
    if self.num_mel_bins != Consts.DEFAULT_NUM_MEL_BINS:
      s += 'mb%d' % self.num_mel_bins
    return s

  @property
  def frames_per_second(self):
    return self.sample_rate / self.hop_width


def split_audio(samples, spectrogram_config):
  """Split audio into frames."""
  return librosa.util.frame(
      samples,
      frame_length=spectrogram_config.hop_width,
      frame_step=spectrogram_config.hop_width,
      pad_end=True)


def compute_spectrogram(samples, spectrogram_config):
  """Compute a mel spectrogram."""
  overlap = 1 - (spectrogram_config.hop_width / Consts.FFT_SIZE)
  return spectral_ops.compute_logmel(
      samples,
      bins=spectrogram_config.num_mel_bins,
      lo_hz=Consts.MEL_LO_HZ,
      overlap=overlap,
      fft_size=Consts.FFT_SIZE,
      sample_rate=spectrogram_config.sample_rate)


def flatten_frames(frames):
  """Convert frames back into a flat array of samples."""
  return np.reshape(frames, [-1])


def input_depth(spectrogram_config):
  return spectrogram_config.num_mel_bins
