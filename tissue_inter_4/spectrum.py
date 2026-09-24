import numpy as np


def generate_spectrum(
    kVp=120.0,
    Z=74,
    filter_thickness=1.5,
    energy_step=0.5
):
    print("\n --- Inside energy spectrum generation ---")
    energies = np.arange(
        1.0,
        kVp + energy_step,
        energy_step
    )

    unfiltered = Z* (kVp - energies)/ energies  # This is the assumed bremsstrahlung-like spectral distribution.

    unfiltered = np.maximum(
        unfiltered,
        0
    )

    transmission = np.exp(
        -filter_thickness
        * (25.0 / energies) ** 3
    )

    spectrum = (
        unfiltered
        * transmission
    )

    return energies, spectrum