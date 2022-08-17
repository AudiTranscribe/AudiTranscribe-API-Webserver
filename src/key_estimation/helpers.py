# IMPORTS
import librosa
import numpy as np


# FUNCTIONS
def std_normalizer(data):
    """
    Normalizes data to zero mean and unit variance.
    """

    # Cast data as 64-bit float to avoid numpy warnings
    data = data.astype(np.float64)

    # Get existing mean and standard deviation of data
    mean = np.mean(data)
    std = np.std(data)

    # Normalize data
    if std != 0.:
        data = (data - mean) / std

    # Now cast data back to 16-bit floats and return
    return data.astype(np.float16)


def key_dist_index_to_key(key_dist_index):
    """
    Helper function that converts the index of the key distribution into a tonic and scale.
    """

    # Determine if the key is in minor or major mode
    is_minor = key_dist_index >= 12

    # Determine midi value of the key
    key_midi_val = key_dist_index + 12 if not is_minor else key_dist_index

    # Get the tonic and mode
    tonic = librosa.midi_to_note(midi=key_midi_val, octave=False)
    mode = "Minor" if is_minor else "Major"

    # Concat and return
    return f"{tonic} {mode}"
