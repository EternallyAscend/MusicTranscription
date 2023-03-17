"""Functions for mixing (in the audio sense) multiple transcription examples."""

from typing import Callable, Optional, Sequence

import gin

import eventCodec
import runLengthEncoding

import numpy as np
import seqio


@gin.configurable
def mix_transcription_examples(
    data,
    sequence_length: seqio.preprocessors.SequenceLengthType,
    output_features: seqio.preprocessors.OutputFeaturesType,
    codec: eventCodec.Codec,
    inputs_feature_key: str = 'inputs',
    targets_feature_keys: Sequence[str] = ('targets',),
    max_examples_per_mix: Optional[int] = None,
    shuffle_buffer_size: int = seqio.SHUFFLE_BUFFER_SIZE
):
    """Preprocessor that mixes together "batches" of transcription examples.

    Args:
        ds: Dataset of individual transcription examples, each of which should
        have an 'inputs' field containing 1D audio samples (currently only
        audio encoders that use raw samples as an intermediate representation
        are supported), and a 'targets' field containing run-length encoded
        note events.
        sequence_length: Dictionary mapping feature key to length.
        output_features: Dictionary mapping feature key to spec.
        codec: An event_codec.Codec used to interpret the target events.
        inputs_feature_key: Feature key for inputs which will be mixed as audio.
        targets_feature_keys: List of feature keys for targets, each of which will
        be merged (separately) as run-length encoded note events.
        max_examples_per_mix: Maximum number of individual examples to mix together.
        shuffle_buffer_size: Size of shuffle buffer to use for shuffle prior to
        mixing.

    Returns:
        Dataset containing mixed examples.
    """
    if max_examples_per_mix is None:
        return data

    data = data.shuffle(
        buffer_size=shuffle_buffer_size // max_examples_per_mix
    )

    def mix_inputs(ex):
        samples = np.sum(ex[inputs_feature_key], axis=0)
        norm = np.linalg.norm(samples, ord=np.inf)
        ex[inputs_feature_key] = np.divide(samples, norm, out=np.zeros_like(samples), where=norm!=0)
        return ex
    data = data.map(mix_inputs)

    max_tokens = sequence_length['targets']
    if output_features['targets'].add_eos:
        # Leave room to insert an EOS token.
        max_tokens -= 1

    def mix_targets(ex):
        for k in targets_feature_keys:
            ex[k] = runLengthEncoding.merge_run_length_encoded_targets(
                targets=ex[k],
                codec=codec)
        return ex
    data = data.map(mix_targets)

    return data
