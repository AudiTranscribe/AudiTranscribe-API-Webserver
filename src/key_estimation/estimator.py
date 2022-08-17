# IMPORTS
import numpy as np

from src.key_estimation.helpers import std_normalizer, key_dist_index_to_key


# FUNCTIONS
def estimate_key_distribution(data, model, verbose=False):
    """
    Estimate a key distribution.
    Probabilities are indexed, starting with 30 BPM and ending with 286 BPM. (wait why bpm???)
    """

    # Check that the data is of the correct shape
    assert len(data.shape) == 4, "Input data must be four dimensional. Actual shape was " + str(data.shape)
    assert data.shape[1] == 168, "Second dim of data must be 168. Actual shape was " + str(data.shape)
    assert data.shape[2] == 60, "Third dim of data must be 60. Actual shape was " + str(data.shape)
    assert data.shape[3] == 1, "Fourth dim of data must be 1. Actual shape was " + str(data.shape)

    # Normalize the data
    norm_data = std_normalizer(data)

    # Use the model to estimate the key distribution
    return model.predict(norm_data, norm_data.shape[0], verbose=verbose)


def estimate_key(data, model, verbose=False):
    """
    Estimates the pre-dominant global key.
    """

    # First estimate the key distribution
    est_key_dist = estimate_key_distribution(data, model, verbose=verbose)

    # Compute the averaged prediction distribution
    avg_est_key_dist = np.average(est_key_dist, axis=0)

    # Create an auxiliary array for sorting (in descending order)
    num_keys = len(avg_est_key_dist)
    key_and_probs = sorted([[float(avg_est_key_dist[i]), i] for i in range(num_keys)], key=lambda elem: -elem[0])

    # Organise data for returning
    keys = []
    probabilities = []
    for i in range(num_keys):
        keys.append(key_dist_index_to_key(key_and_probs[i][1]))
        probabilities.append(round(key_and_probs[i][0], 5))  # Round to 5dp to avoid floating point errors later

    return keys, probabilities
