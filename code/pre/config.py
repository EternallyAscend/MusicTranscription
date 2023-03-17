import dataclasses
from typing import Mapping, Sequence, Union
import numpy as np

import noteSequences
import vocabularies
import spectrograms

@dataclasses.dataclass
class InferEvalSplit:
  # key in dictionary containing all dataset splits
  name: str
  # task name suffix (each eval split is a separate task)
  suffix: str
  # whether or not to include in the mixture of all eval tasks
  include_in_mixture: bool = True


@dataclasses.dataclass
class DatasetConfig:
  """Configuration for a transcription dataset."""
  # dataset name
  name: str
  # mapping from split name to path
  paths: Mapping[str, str]
  # mapping from feature name to feature
  features: Mapping[str, Union[np.ndarray, np.ndarray]]
  # training split name
  train_split: str
  # training eval split name
  train_eval_split: str
  # list of infer eval split specs
  infer_eval_splits: Sequence[InferEvalSplit]
  # list of track specs to be used for metrics
  track_specs: Sequence[noteSequences.TrackSpec] = dataclasses.field(
      default_factory=list)

class Consts:
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    SYSEX = "sysex"

    SAMPLE_RATE = 44100
    TARGET_RATE = 8000 # 16000

    DEFAULT_SAMPLE_RATE = 16000
    DEFAULT_HOP_WIDTH = 128
    DEFAULT_NUM_MEL_BINS = 512

    FFT_SIZE = 2048
    MEL_LO_HZ = 20.0

    DEFAULT_VELOCITY = 100
    DEFAULT_NOTE_DURATION = 0.01

    # Quantization can result in zero-length notes; enforce a minimum duration.
    MIN_NOTE_DURATION = 0.01
    # Just use default spectrogram config.
    SPECTROGRAM_CONFIG = spectrograms.SpectrogramConfig()

    # Create two vocabulary configs, one default and one with only on-off velocity.
    VOCAB_CONFIG_FULL = vocabularies.VocabularyConfig()
    VOCAB_CONFIG_NOVELOCITY = vocabularies.VocabularyConfig(num_velocity_bins=1)

    # Split audio frame sequences into this length before the cache placeholder.
    MAX_NUM_CACHED_FRAMES = 2000

    MAESTROV1_CONFIG = DatasetConfig(
    name='maestrov1',
    paths={
        'train':
            'gs://magentadata/datasets/maestro/v1.0.0/maestro-v1.0.0_ns_wav_train.tfrecord-?????-of-00010',
        'train_subset':
            'gs://magentadata/datasets/maestro/v1.0.0/maestro-v1.0.0_ns_wav_train.tfrecord-00002-of-00010',
        'validation':
            'gs://magentadata/datasets/maestro/v1.0.0/maestro-v1.0.0_ns_wav_validation.tfrecord-?????-of-00010',
        'validation_subset':
            'gs://magentadata/datasets/maestro/v1.0.0/maestro-v1.0.0_ns_wav_validation.tfrecord-0000[06]-of-00010',
        'test':
            'gs://magentadata/datasets/maestro/v1.0.0/maestro-v1.0.0_ns_wav_test.tfrecord-?????-of-00010'
    },
    features={
        'audio': np.ndarray,
        'sequence': np.ndarray,
        'id': np.ndarray
    },
    train_split='train',
    train_eval_split='validation_subset',
    infer_eval_splits=[
        InferEvalSplit(name='train', suffix='eval_train_full',
                       include_in_mixture=False),
        InferEvalSplit(name='train_subset', suffix='eval_train'),
        InferEvalSplit(name='validation', suffix='validation_full',
                       include_in_mixture=False),
        InferEvalSplit(name='validation_subset', suffix='validation'),
        InferEvalSplit(name='test', suffix='test', include_in_mixture=False)
    ])

    MAESTROV3_CONFIG = DatasetConfig(
        name='maestrov3',
        paths={
            'train':
                'gs://magentadata/datasets/maestro/v3.0.0/  maestro-v3.0.0_ns_wav_train.tfrecord-?????    -of-00025',
            'train_subset':
                'gs://magentadata/datasets/maestro/v3.0.0/  maestro-v3.0.0_ns_wav_train.  tfrecord-00004-of-00025',
            'validation':
                'gs://magentadata/datasets/maestro/v3.0.0/  maestro-v3.0.0_ns_wav_validation.tfrecord-?   ????-of-00025',
            'validation_subset':
                'gs://magentadata/datasets/maestro/v3.0.0/  maestro-v3.0.0_ns_wav_validation. tfrecord-0002?-of-00025',
            'test':
                'gs://magentadata/datasets/maestro/v3.0.0/  maestro-v3.0.0_ns_wav_test.tfrecord-????? -of-00025'
        },
        features={
            'audio': np.ndarray,
            'sequence': np.ndarray,
            'id': np.ndarray
        },
        train_split='train',
        train_eval_split='validation_subset',
        infer_eval_splits=[
            InferEvalSplit(name='train',    suffix='eval_train_full',
                           include_in_mixture=False),
            InferEvalSplit(name='train_subset',     suffix='eval_train'),
            InferEvalSplit(name='validation',   suffix='validation_full',
                           include_in_mixture=False),
            InferEvalSplit(name='validation_subset',    suffix='validation'),
            InferEvalSplit(name='test', suffix='test',  include_in_mixture=False)
        ])
