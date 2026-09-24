import numpy as np

# Accoridng to our config file ---
# detector has 64x888 elements 
# 64 x 888=56,832 detector rays/view

def detector_basis(source_position, detector_position):

    normal = source_position - detector_position
    normal = normal / np.linalg.norm(normal)

    # Detector height direction = Y
    v = np.array([0.0, 1.0, 0.0])

    # Detector width direction
    u = np.cross(v, normal)
    u = u / np.linalg.norm(u)

    return u, v, normal


def generate_detector_pixels(
    detector_position,
    source_position,
    detector_rows,
    detector_channels,
    pixel_width_mm,
    pixel_height_mm
):

    u, v, normal = detector_basis(
        source_position,
        detector_position
    )

    rows = np.arange(detector_rows)
    channels = np.arange(detector_channels)

    u_coords = (
        channels - (detector_channels - 1) / 2.0
    ) * pixel_width_mm

    v_coords = (
        rows - (detector_rows - 1) / 2.0
    ) * pixel_height_mm

    U, V = np.meshgrid(
        u_coords,
        v_coords,
        indexing="xy"
    )

    pixel_positions = (
        detector_position
        + U[..., None] * u
        + V[..., None] * v
    )

    pixel_positions = pixel_positions.reshape(-1, 3)

    return pixel_positions