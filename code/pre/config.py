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
