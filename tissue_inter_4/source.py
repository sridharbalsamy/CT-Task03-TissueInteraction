# No cone sampling

import numpy as np


def generate_rays(
    source_position,
    detector_pixels
):

    num_rays = detector_pixels.shape[0]

    origins = np.repeat(
        source_position[np.newaxis, :],
        num_rays,
        axis=0
    )

    directions = detector_pixels - origins    # vector subtraction for direction finding 

    norms = np.linalg.norm(
        directions,
        axis=1,
        keepdims=True
    )

    directions /= norms

    rays = np.column_stack(
        (
            origins,
            directions
        )
    )

    return rays