2# CT Simulation: Structured Integration

A Python-based, phase-1 CT simulation pipeline that connects an X-ray source model, voxel-based tissue attenuation, an approximate scatter stage, and an energy-integrating detector. The project is organized into separate modules so each stage can be inspected and developed independently.

> **Scope note:** This is a simulation prototype, not a clinically validated CT simulator. Quantitative output depends on the accuracy and calibration of the source, phantom, interaction, scatter, and detector models.

## Pipeline overview

```text
system_config/ct_system_output.json
                |
                v
      Per-view CT geometry
                |
                v
       xray_source module
  spectrum + photon directions
  + energy samples + photon weights
                |
                v
    tissue_interaction module
  voxel traversal + attenuation
       (Beer-Lambert model)
                |
                v
        scattering module
   approximate scatter contribution
                |
                v
         CTdetector module
  energy integration + detector effects
                |
                v
       Detector image per view
         .npy and selected .csv
```

The main integration entry point is `tissue_interaction/main.py`. It reads the master configuration, generates the cylindrical phantom, processes the selected views, and writes detector output.

## Project structure

```text
CTsim_structured_integ/
├── CTdetector/
│   └── energy_integrating_detector.py  # Detector response model
├── photon_output/                      # Created when the pipeline runs
├── system_config/
│   ├── ct_system_output.json            # Master scanner and trajectory config
│   └── libraries_used.txt               # Recorded environment package versions
├── tissue_interaction/
│   ├── main.py                          # Integrated pipeline entry point
│   ├── config.py                        # Configuration and per-view geometry
│   ├── syncer.py                        # Detector pixel geometry
│   ├── cylinder_voxel.py                # Synthetic cylindrical phantom
│   ├── tissue_interaction.py            # Ray traversal and spectral attenuation
│   ├── material.py                      # Material attenuation coefficients
│   ├── scattering.py                    # Approximate scatter model
│   ├── energy_integrating_detector.py   # Local detector implementation/reference
│   ├── README.md                        # Tissue-interaction module notes
│   ├── units_n_dimensions.md             # Unit and array-shape notes
│   ├── changes.md                       # Change log
│   └── remaining_work.md                # Known follow-up work
└── xray_source/
    ├── main.py                          # Source-model integration API
    ├── config.py                        # Source parameters
    ├── spectrum.py                      # Spectrum and filtration
    ├── geometry.py                      # Focal spot and ray directions
    ├── weights.py                       # Photon weights and source effects
    ├── flat_field.py                    # Flat-field utilities
    ├── validate.py                      # Source validation helpers
    └── README.md                        # Source-module notes
```

`__pycache__` folders and `.pyc` files, if present, are generated Python cache artifacts and are not required source files.

## Requirements

Use Python 3.10 or newer as a practical starting point. The included environment record was produced with Python 3.13 bytecode, but the project has not been verified here against every Python version.

Core packages used by the current code include:

- `numpy`
- `scipy`
- `matplotlib`
- `xraylib`

Install them in a virtual environment from the project root:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install the dependencies:

```bash
python -m pip install numpy scipy matplotlib xraylib
```

If installation fails, check that the selected Python version and platform are supported by the relevant package wheels.

## Run the simulation

Run commands from the extracted `CTsim_structured_integ` project root, the directory containing `CTdetector`, `system_config`, `tissue_interaction`, and `xray_source`.

### 1. Run a small smoke test

```bash
python -m tissue_interaction.main --views 0
```

This processes the first configured projection. A smoke test is recommended before attempting the full trajectory.

### 2. Process a few selected views

```bash
python -m tissue_interaction.main --views 0 1 2
```

View indices are zero-based.

### 3. Process all configured views

```bash
python -m tissue_interaction.main
```

The supplied configuration declares **16,728 views**. Each view uses a **64 × 888 detector grid**, or **56,832 detector pixels/rays per view**. Processing every view can take substantial time and create a large amount of output. Start with one or a few views and check runtime and disk space first.

### 4. Use a different configuration or output folder

```bash
python -m tissue_interaction.main --config path/to/ct_system_output.json --output-dir path/to/output
```

The configuration must preserve the expected keys, including `system_config`, `trajectory.views`, `detector_config`, and the source settings used by the source module.

Optional scatter parameters are available:

```bash
python -m tissue_interaction.main --views 0 --spr 1.2 --kernel-size 21
```

Check `python -m tissue_interaction.main --help` for the command-line options available in the current code.

## Configuration

The default master configuration is `system_config/ct_system_output.json`. It contains scanner settings, detector dimensions, source parameters, volume dimensions, and the per-view trajectory.

Key configured values include:

| Setting           |                           Value |
| ----------------- | ------------------------------: |
| Tube potential    |                         120 kVp |
| Tube current      |                          200 mA |
| Exposure time     |      1 s per configured setting |
| Detector rows     |                              64 |
| Detector channels |                             888 |
| Detector elements |                          56,832 |
| Voxel spacing     | 1 mm (isotropic, as configured) |
| Configured views  |                          16,728 |

Edit the JSON configuration deliberately. Geometry, detector dimensions, and `source_config.n_samples` must remain consistent. The source module checks that `n_samples` equals `detector_rows × detector_channels`.

## Module responsibilities

### X-ray source: `xray_source/`

Builds a source output bundle for each view. It includes the sampled spectrum/energy grid, source-to-detector ray directions, focal-spot sampling, and photon weights. `run_source_simulation()` is called by the integration entry point.

### Tissue interaction: `tissue_interaction/`

Creates a synthetic cylindrical material-ID phantom and traces each ray through the voxel grid. Material path lengths are combined with energy-dependent linear attenuation coefficients to calculate energy-resolved primary transmission using the Beer-Lambert relationship:

\[
N(E) = N_0(E)\exp\left(-\sum_m \mu_m(E)L_m\right)
\]

where \(N_0(E)\) is the incident spectral fluence, \(\mu_m(E)\) is the linear attenuation coefficient for material \(m\), and \(L_m\) is the path length through that material. The current interaction model primarily represents attenuation of primary photons, not a full particle-transport simulation.

### Scattering: `tissue_interaction/scattering.py`

Adds an approximate scatter contribution to the transmitted detector fluence. This is not equivalent to detailed Monte Carlo modelling of Compton, photoelectric, and Rayleigh interactions. Treat results accordingly.

### Detector: `CTdetector/energy_integrating_detector.py`

Receives fluence arranged as `(detector_rows, detector_channels, number_of_energy_bins)` and returns a two-dimensional measured signal image. The model includes energy integration and configurable detector effects such as quantum efficiency, blur, gain variation, dead pixels, and noise, as implemented in the module.

## Inputs and outputs

### Source-to-tissue data contract

The source module returns a dictionary consumed by `tissue_interaction()`. Its `data_matrix` has eight columns:

```text
[x, y, z, dx, dy, dz, sampled_energy_keV, photon_weight]
```

The first three columns describe ray origins in millimetres; the next three describe direction vectors; the final columns hold sampled photon energy in keV and photon weight. `energies_grid` provides the energy grid used by the tissue, scatter, and detector stages.

### Detector input shape

After tissue interaction, fluence is reshaped to:

```text
(detector_rows, detector_channels, energy_bins)
```

For the supplied configuration, the first two dimensions are `(64, 888)`.

### Generated files

By default, output is written to `photon_output/` at the project root. The integration script saves a NumPy detector image for each processed view, named similar to:

```text
view_1_detector.npy
view_2_detector.npy
```

It also writes ray/signal CSV files for the first three processed view IDs, named similar to:

```text
view_1_rays.csv
```

The exact filenames use one-based output IDs, even though input view indices are zero-based. NumPy files contain the detector image; CSV files contain ray data and detector signal values. Inspect `save_view_rays()` in `tissue_interaction/main.py` for the exact CSV columns.

Load a detector image in Python:

```python
import numpy as np

image = np.load("photon_output/view_1_detector.npy")
print(image.shape)  # expected: (64, 888)
print(image.dtype)
```

## Troubleshooting

**`ModuleNotFoundError` for a project module**

Run the command from the project root and use `python -m tissue_interaction.main ...` rather than launching it from an unrelated working directory.

**Missing `xraylib`**

Activate the intended virtual environment, then run `python -m pip install xraylib`.

**Source sample-count mismatch**

Make `source_config.n_samples` equal `detector_config.detector_rows * detector_config.detector_channels`.

**Full run is too slow or produces too many files**

Use `--views 0` or a short list of view indices first. Full execution processes all configured views and saves an image per view.

**Unexpected signal magnitude**

Check photon-weight normalization, source calibration, attenuation units, energy-bin interpretation, and detector conversion settings. A large detector signal is not automatically evidence of a bug, but it is not physically meaningful without checking units and calibration.

## Further documentation

- `tissue_interaction/README.md`
- `tissue_interaction/units_n_dimensions.md`
- `tissue_interaction/changes.md`
- `tissue_interaction/remaining_work.md`
- `xray_source/README.md`
- `xray_source/LIBRARIES_USED.md` (if present in your checkout)
