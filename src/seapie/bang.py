"""
bang handler stuff
"""

import sys
import traceback


def print_tb(num_frames_to_hide):
    """Number of frames to exclude is how much seapie occupies"""
    exc_type, exc_val, exc_tb = sys.exc_info()  # Get the traceback
    tb_frames = traceback.extract_tb(exc_tb)

    filtered_tb_frames = tb_frames[num_frames_to_hide:]  # Hide seapie frames
    formatted_traceback = "".join(traceback.format_list(filtered_tb_frames))

    print("Traceback (most recent call last):")  # Print header.
    print(formatted_traceback, end="")  # Print traceback,
    print(f"{exc_type.__name__}: {exc_val}")  # Print the error itself.
