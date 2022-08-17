# IMPORTS
import struct

import numpy as np


# FUNCTIONS
def bytes_to_int(bytes_: bytes):
    return int.from_bytes(bytes_, "big")


def bytes_to_double(bytes_: bytes):
    # We use big endian in Java, so we need to specify it here
    return struct.unpack(">d", bytes_)[0]  # Returns a 1-element tuple, so we take 0th element


def bytes_to_3d_array(bytes_: bytes):
    # Get bytes that represent the lengths
    num_subarrays_bytes = bytes_[:4]
    num_sub_subarrays_bytes = bytes_[4:8]
    sub_subarray_length_bytes = bytes_[8:12]

    # Retrieve the lengths from the bytes
    num_subarrays = bytes_to_int(num_subarrays_bytes)
    num_sub_subarrays = bytes_to_int(num_sub_subarrays_bytes)
    sub_subarray_length = bytes_to_int(sub_subarray_length_bytes)

    # Create the array to return
    array = np.zeros((num_subarrays, num_sub_subarrays, sub_subarray_length))
    for i in range(num_subarrays):
        for j in range(num_sub_subarrays):
            for k in range(sub_subarray_length):
                # Get the bytes that represent the current element
                start = 12 + 8 * i * (num_sub_subarrays * sub_subarray_length) + 8 * j * sub_subarray_length + 8 * k
                elem = bytes_[start:start + 8]

                # Convert the bytes into a double and place into the array
                array[i][j][k] = bytes_to_double(elem)

    return array
