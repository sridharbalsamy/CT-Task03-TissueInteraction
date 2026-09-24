# CT-Task03-TissueInteraction
This repo deals with the interaction of materials with the X-rays. 

# Phase 1: Deterministic X-Ray CT Tissue Interaction Pipeline

## 1. Module Overview

This Phase 1 implementation models a simplified deterministic X-ray CT
acquisition pipeline consisting of an X-ray source, rotating
source-detector geometry, a voxelized tissue phantom, ray generation,
tissue attenuation, and detector signal formation. The pipeline does
**not** use Monte Carlo photon transport or scattering. Instead, one
deterministic ray is generated for each detector element for every CT
view, and the ray is traced through the voxelized phantom.
Though the actual task is to perform tissue interaction, we need both 
the source and detector to be in sync wihch facillitates the alignment 
of phantom during rotation for each view.

The system begins by loading the CT geometry and source/detector
configuration from the JSON configuration file. A cylindrical voxel
phantom is created for the current Phase 1 test case. For each view, the
source and detector positions are calculated from the rotation angle and
table position. Detector element positions are then generated, and rays
are constructed from the source to each detector element.

Each ray is subsequently traversed through the voxel volume. The path
length accumulated in each material is used with energy-dependent linear
attenuation coefficients obtained from `xraylib`. Beer-Lambert
attenuation is applied across the generated energy spectrum, and an
energy-integrated detector signal is calculated for each detector ray.
The detector signals are reshaped into a 2D detector image and stored as
`.npy` files. Selected views are additionally exported as CSV files for
inspection.

------------------------------------------------------------------------

## 2. Inputs & Outputs

### Inputs

  -----------------------------------------------------------------------
  Input                               Description
  ----------------------------------- -----------------------------------
  `ct_config_by_team2.json`           Main configuration file containing
                                      source, detector and system
                                      geometry parameters used by the
                                      current implementation.

  Source configuration                Provides values such as `kVp`. The
                                      current code uses `kvp` from the
                                      JSON configuration.

  Detector configuration              Provides detector rows, detector
                                      channels, detector element width
                                      and detector element height.

  System configuration                Provides SID, SDD, views per
                                      rotation, total views and table
                                      feed per rotation.

  Cylindrical phantom parameters      Currently hard-coded in `main.py`:
                                      radius = `25 mm`, height = `50 mm`,
                                      voxel size = `1 mm`, density =
                                      `1.0`, material ID = `1`.

  Material database                   Material IDs are mapped to NIST
                                      material names used by `xraylib`.

  Energy spectrum parameters          Current implementation uses
                                      `kVp = 120`, tungsten atomic number
                                      `Z = 74`, filter thickness `1.5`,
                                      and energy step `0.5 keV`.
  -----------------------------------------------------------------------

### Outputs

  -----------------------------------------------------------------------
  Output                              Description
  ----------------------------------- -----------------------------------
  `view_<view_id>_detector.npy`       2D detector signal array for each
                                      processed view.

  `view_<view_id>_rays.csv`           CSV containing ray coordinates, ray
                                      directions and detector signal for
                                      selected views. Currently views 1,
                                      2 and 3 are exported.

  Detector signal                     One scalar energy-integrated
                                      attenuation value for every
                                      detector ray.

  Console information                 View number, rotation angle, table
                                      position, source position, detector
                                      position, number of rays, detector
                                      image shape and total detector
                                      signal.
  -----------------------------------------------------------------------

For the current detector configuration, the code expects:

``` text
64 rows × 888 channels = 56,832 detector rays per view
```

The actual number of rays is obtained from the generated detector pixel
array and is not hard-coded in the ray-generation loop.

------------------------------------------------------------------------

# 3. End-to-End Pipeline

The current execution flow is:

``` text
ct_config_by_team2.json
        │
        ▼
     main.py
        │
        ├── Load configuration
        │
        ├── Create cylindrical voxel phantom
        │
        ├── Load CT geometry
        │
        ├── Generate X-ray energy spectrum
        │
        ▼
   For every CT view
        │
        ├── Calculate source/detector positions
        │
        ├── Generate detector pixel positions
        │
        ├── Generate deterministic rays
        │
        ├── Traverse every ray through voxel volume
        │
        ├── Calculate material path lengths
        │
        ├── Obtain attenuation coefficients from xraylib
        │
        ├── Apply spectral Beer-Lambert attenuation
        │
        ├── Calculate detector signal
        │
        └── Save detector image
        │
        ▼
 photon_output/
```

------------------------------------------------------------------------

# 4. Project Files

``` text
Project/
│
├── main.py
├── source.py
├── detector.py
├── syncer.py
├── spectrum.py
├── material.py
├── tissue_interaction.py
├── cylinder_voxel.py
├── cylinder_voxel_tested.py
├── read_npy.py
└── ct_config_by_team2.json
```

------------------------------------------------------------------------

# 5. Module Documentation

## 5.1 `main.py`

### Purpose

`main.py` is the main execution module and connects all other modules
into a complete Phase 1 CT simulation pipeline.

It loads the configuration, creates the phantom, generates the spectrum,
loops through all CT views, creates detector pixels and deterministic
rays, performs tissue interaction, and stores detector outputs.

The main workflow is implemented in:

``` python
main()
```

### Functions

#### `save_view_rays(view_id, rays, detector_signal, output_dir="photon_output")`

Saves ray information and the corresponding detector signal to a CSV
file.

The CSV contains:

``` text
view_id
ray_id
x
y
z
dx
dy
dz
detector_signal
```

The output filename follows:

``` text
view_<view_id>_rays.csv
```

#### `main()`

Controls the complete simulation.

Major operations:

1.  Loads `ct_config_by_team2.json`.
2.  Reads source and detector configuration.
3.  Creates the cylindrical phantom.
4.  Loads CT geometry.
5.  Generates the energy spectrum.
6.  Loops over `total_views`.
7.  Calculates view geometry.
8.  Generates detector pixel positions.
9.  Generates deterministic rays.
10. Performs tissue interaction.
11. Saves selected ray data as CSV.
12. Reshapes detector signals into a 2D detector image.
13. Saves detector images as `.npy`.

### Important current Phase 1 values

The following values are currently hard-coded in `main.py`:

``` text
voxel_size_mm = 1.0
phantom_radius_mm = 25.0
phantom_height_mm = 50.0
phantom_density = 1.0
phantom_material_id = 1
```

The detector dimensions and detector element sizes are read from JSON.

------------------------------------------------------------------------

# 6. `cylinder_voxel.py`

## Purpose

Creates a 3D voxel representation of a cylindrical phantom.

The main function is:

``` python
create_cylinder_voxel()
```

It produces two arrays:

``` text
voxel_density
voxel_material
```

The density array stores the density value of occupied voxels. The
material array stores the material ID.

### `create_cylinder_voxel(radius_mm, height_mm, voxel_size_mm, density, material_id)`

#### Inputs

-   `radius_mm`: cylinder radius
-   `height_mm`: cylinder height
-   `voxel_size_mm`: voxel size
-   `density`: density assigned to occupied voxels
-   `material_id`: material ID assigned to occupied voxels

#### Outputs

``` python
voxel_density
voxel_material
```

The current implementation uses a circular cross-section and replicates
the circular mask through the third volume dimension.

### `plot_voxel_cylinder(voxel_density, voxel_size_mm=1.0)`

Creates a 3D visualization of occupied voxels using Matplotlib.

### Current implementation note

Two cylinder files are present in the supplied code:

``` text
cylinder_voxel.py
cylinder_voxel_tested.py
```

They are not identical.

The `cylinder_voxel.py` implementation creates arrays with shape:

``` text
(nz, ny, nx)
```

and constructs a circular cross-section in the X-Y plane before
replication along Z.

The other supplied implementation, `cylinder_voxel_tested.py`, uses a
different dimension construction and circular cross-section arrangement.
The active `main.py` imports:

``` python
from cylinder_voxel import create_cylinder_voxel
```

Therefore, the `cylinder_voxel.py` implementation is the one directly
referenced by the current `main.py`.

------------------------------------------------------------------------

# 7. `syncer.py`

## Purpose

`syncer.py` handles the CT system geometry and synchronizes source
rotation with table movement.

### `load_geometry(config)`

Reads the following values from:

``` text
config["4_system_config_team"]
```

Parameters include:

-   SID
-   SDD
-   views per rotation
-   total views
-   table feed per rotation

It calculates:

``` text
detector_radius = SDD - SID

angle_increment = 2π / views_per_rotation

y_step = table_feed_per_rotation / views_per_rotation
```

It then creates:

``` text
theta
y_positions
```

for all views.

### `get_view_geometry(geometry, view_index)`

Calculates the source and detector position for one view.

The source rotates around the Y axis:

``` text
x = SID × cos(theta)
y = table position
z = SID × sin(theta)
```

The detector is placed on the opposite side of the source-detector
system.

The function returns:

``` python
source_position
detector_position
central_direction
```

------------------------------------------------------------------------

# 8. `detector.py`

## Purpose

Creates the physical position of every detector element for a particular
view.

### `detector_basis(source_position, detector_position)`

Calculates three detector basis vectors:

``` text
u = detector width direction
v = detector height direction
normal = detector normal direction
```

The current implementation fixes the detector height direction along:

``` text
Y = [0, 1, 0]
```

### `generate_detector_pixels(...)`

Generates the 3D coordinates of all detector elements.

Inputs:

``` text
detector_position
source_position
detector_rows
detector_channels
pixel_width_mm
pixel_height_mm
```

Output:

``` text
pixel_positions
```

Shape:

``` text
(number_of_detector_elements, 3)
```

For the current detector:

``` text
64 × 888 = 56,832 detector pixels
```

Therefore:

``` text
56,832 rays/view
```

are generated by the current deterministic ray model.

------------------------------------------------------------------------

# 9. `source.py`

## Purpose

`source.py` generates deterministic rays from the X-ray source to the
detector elements.

The current implementation explicitly does not perform cone sampling.

### `generate_rays(source_position, detector_pixels)`

For every detector pixel:

1.  Replicates the source position.
2.  Calculates the vector from source to detector pixel.
3.  Normalizes the direction vector.
4.  Combines origin and direction into a ray array.

Output format:

``` text
[x, y, z, dx, dy, dz]
```

where:

``` text
x, y, z     = ray origin
dx, dy, dz  = normalized ray direction
```

Output shape:

``` text
(number_of_detector_pixels, 6)
```

For the current detector configuration:

``` text
(56832, 6)
```

------------------------------------------------------------------------

# 10. `spectrum.py`

## Purpose

Generates the energy distribution used during spectral attenuation
calculations.

### `generate_spectrum(kVp=120.0, Z=74, filter_thickness=1.5, energy_step=0.5)`

The energy range is generated from:

``` text
1.0 keV
```

to:

``` text
kVp
```

with the specified energy step.

The current unfiltered spectrum is calculated using:

``` text
Z × (kVp - energy) / energy
```

A filtering/transmission term is then applied:

``` text
exp[-filter_thickness × (25 / energy)^3]
```

The resulting spectrum is:

``` text
spectrum = unfiltered × transmission
```

The function returns:

``` python
energies, spectrum
```

### Current Phase 1 spectrum configuration

``` text
kVp = 120
Z = 74
filter_thickness = 1.5
energy_step = 0.5 keV
```

------------------------------------------------------------------------

# 11. `material.py`

## Purpose

Provides material definitions and obtains attenuation properties using
`xraylib`.

The current material database contains:

    ID Material          NIST name
  ---- ----------------- ---------------------------
     0 Air               Air, Dry (near sea level)
     1 Soft Tissue       Tissue, Soft (ICRP)
     2 Cortical Bone     Bone, Cortical (ICRP)
     3 Lung              Lung (ICRP)
     4 Adipose           Adipose Tissue (ICRP)
     5 Water             Water, Liquid
     6 Skeletal Muscle   Muscle, Skeletal

### `get_material_info(material_id)`

Returns the material information associated with the material ID.

### `mass_attenuation_coefficient(material_id, energy_keV)`

Uses:

``` python
xraylib.CS_Total_CP()
```

to obtain the mass attenuation coefficient.

Units:

``` text
cm²/g
```

### `material_density(material_id)`

Uses:

``` python
xraylib.GetCompoundDataNISTByName()
```

to obtain material density.

Units:

``` text
g/cm³
```

### `linear_attenuation_coefficient(material_id, energy_keV)`

Calculates:

``` text
μ = (μ/ρ) × ρ
```

and converts the resulting value from:

``` text
cm⁻¹
```

to:

``` text
mm⁻¹
```

### `print_material_database()`

Prints material names and densities for the defined material database.

------------------------------------------------------------------------

# 12. `tissue_interaction.py`

## Purpose

`tissue_interaction.py` performs the actual deterministic ray tracing
and X-ray attenuation calculation.

It is the main tissue interaction module of the current Phase 1
implementation.

The module performs:

``` text
Ray → voxel traversal → material path length → attenuation → detector signal
```

------------------------------------------------------------------------

## `ray_box_intersection(origin, direction, box_min, box_max)`

Determines where a ray enters and exits the bounding box containing the
voxel volume.

It uses a slab-based ray-box intersection calculation.

Returns:

``` python
(t_entry, t_exit)
```

or:

``` python
None
```

when there is no intersection.

------------------------------------------------------------------------

## `traverse_ray(origin, direction, voxel_material, voxel_size_mm)`

Traverses a ray through the voxel volume.

The function:

1.  Determines the voxel volume dimensions.
2.  Constructs the bounding box.
3.  Finds ray entry and exit points.
4.  Determines the initial voxel.
5.  Calculates voxel boundary crossing parameters.
6.  Moves through the voxel grid.
7.  Accumulates path length for each material.

Output:

``` python
material_lengths
```

Example structure:

``` text
{
    material_id: total_path_length_mm
}
```

The traversal uses the voxel material array rather than performing
stochastic particle transport.

------------------------------------------------------------------------

## `precompute_mu(material_ids, energies)`

Precomputes the linear attenuation coefficient for every material and
energy.

Output structure:

``` text
mu_table[material_id]
```

Each entry contains the attenuation coefficient across the complete
energy array.

This avoids recalculating the material attenuation coefficient
separately for every ray.

------------------------------------------------------------------------

## `calculate_spectral_transmission(material_lengths, energies, spectrum, mu_table)`

Calculates spectral attenuation using the accumulated material path
lengths.

For each material:

``` text
attenuation += μ(E) × path_length
```

The transmission is then calculated as:

``` text
T(E) = exp(-attenuation)
```

Air is ignored during the current Phase 1 attenuation calculation.

The detector signal is calculated as an energy-integrated quantity:

``` text
detector_signal =
Σ [spectrum(E) × E × transmission(E)]
```

The function returns one scalar detector signal.

------------------------------------------------------------------------

## `tissue_interaction(rays, voxel_material, voxel_size_mm, energies, spectrum)`

Processes all rays.

For every ray:

1.  Extracts the origin.
2.  Extracts the direction.
3.  Traverses the voxel volume.
4.  Obtains material path lengths.
5.  Calculates spectral transmission.
6.  Stores the resulting detector signal.

Output:

``` text
detector_signal
```

Shape:

``` text
(number_of_rays,)
```

For the current detector:

``` text
(56832,)
```

------------------------------------------------------------------------

# 13. `read_npy.py`

## Purpose

Provides a simple post-processing and visualization method for the saved
detector `.npy` output.

The current script loads:

``` text
photon_output/view_2_detector.npy
```

and obtains its dimensions.

It also contains a cross-check against the CSV ray output by comparing a
selected detector value with the flattened ray ordering.

Finally, it visualizes the detector image using:

``` python
plt.imshow()
```

with a colorbar and detector row/channel labels.

This file is a post-processing utility and is not part of the main
simulation execution chain.

------------------------------------------------------------------------

# 14. Data Shapes

The important array dimensions in the current implementation are:

### Voxel volume

The active `cylinder_voxel.py` returns:

``` text
voxel_density : (nz, ny, nx)
voxel_material: (nz, ny, nx)
```

For the current phantom:

``` text
radius = 25 mm
height = 50 mm
voxel size = 1 mm
```

the dimensions are based on the voxelized cylinder construction in
`cylinder_voxel.py`.

### Detector pixels

``` text
(detector_rows × detector_channels, 3)
```

Current detector:

``` text
64 × 888 = 56,832
```

therefore:

``` text
detector_pixels.shape = (56832, 3)
```

### Rays

``` text
(56832, 6)
```

with:

``` text
[x, y, z, dx, dy, dz]
```

### Detector signal

``` text
(56832,)
```

### Detector image

After reshaping:

``` text
(64, 888)
```

------------------------------------------------------------------------

# 15. Current Progress

-   [x] Created a 3D voxelized cylindrical phantom.
-   [x] Implemented source-detector CT geometry.
-   [x] Implemented source rotation around the Y axis.
-   [x] Implemented table translation per view.
-   [x] Implemented detector basis calculation.
-   [x] Implemented detector pixel generation.
-   [x] Implemented deterministic source-to-detector rays.
-   [x] Implemented ray-box intersection.
-   [x] Implemented voxel-by-voxel ray traversal.
-   [x] Implemented material path-length accumulation.
-   [x] Added material definitions using NIST material names.
-   [x] Added energy-dependent attenuation coefficients through
    `xraylib`.
-   [x] Implemented spectral Beer-Lambert attenuation.
-   [x] Implemented energy-integrated detector signal calculation.
-   [x] Implemented detector image generation.
-   [x] Implemented `.npy` detector output.
-   [x] Implemented CSV output for selected views.
-   [x] Implemented basic detector-output visualization.
-   [ ] Full medical/physical validation of the complete pipeline is
    still ongoing.

------------------------------------------------------------------------

# 16. Validation Approach

The current implementation can be validated at multiple stages.

## Geometry Validation

Check:

-   Number of views.
-   Views per rotation.
-   Rotation angle.
-   Table position.
-   Source position.
-   Detector position.
-   Source-detector orientation.

The code prints the geometry information during execution.

## Detector Validation

Check:

``` text
detector_rows × detector_channels
```

and confirm:

``` text
64 × 888 = 56,832
```

detector elements for the current configuration.

## Ray Validation

Check:

``` text
rays.shape
```

Expected current structure:

``` text
(56832, 6)
```

Each direction vector should represent the normalized direction from
source to its corresponding detector pixel.

## Tissue Traversal Validation

Check that:

-   Rays intersecting the phantom accumulate material path length.
-   Rays missing the phantom produce no tissue attenuation path.
-   Material path lengths are non-negative.
-   Ray traversal remains within the voxel volume.

## Attenuation Validation

Check that:

-   Attenuation coefficients are obtained for the requested energies.
-   Transmission follows the implemented Beer-Lambert expression.
-   Transmission values remain physically non-negative.
-   Increasing tissue path length produces lower transmitted signal in
    the implemented model.

## Detector Output Validation

Check:

``` text
detector_image.shape
```

Expected:

``` text
(64, 888)
```

Also check:

``` text
np.sum(detector_image)
```

and inspect the detector image visually using `read_npy.py`.

------------------------------------------------------------------------

# 17. Current Phase 1 Assumptions and Limitations

The following are part of the **current implementation**, not proposed
corrections:

1.  **Deterministic ray tracing is used.** Monte Carlo photon transport
    is not implemented.

2.  **No scattering is modeled.** The current interaction is limited to
    attenuation.

3.  **One deterministic ray is generated for every detector element.**

4.  **The current phantom is a homogeneous cylindrical phantom.**

5.  **The phantom radius, height, voxel size, density and material ID
    are currently hard-coded in `main.py`.**

6.  **The current phantom uses material ID `1`, corresponding to Soft
    Tissue.**

7.  **Air path contribution is ignored during the Phase 1 attenuation
    calculation.**

8.  **The spectrum is generated using the implemented
    bremsstrahlung-like expression in `spectrum.py`.**

9.  **The detector calculation is energy-integrating.**

10. **The detector signal is calculated from the weighted spectral sum
    used in `calculate_spectral_transmission()`.**

11. **Only views 1, 2 and 3 are exported as CSV ray files by the current
    `main.py`.**

12. **All detector views are saved as `.npy` detector images.**

13. **The current implementation is intended as a Phase 1 deterministic
    attenuation model rather than a complete clinical CT simulation.**

------------------------------------------------------------------------

# 18. Libraries Used

## NumPy

Used throughout the pipeline for numerical operations and array
manipulation.

Important functions used include:

``` text
np.array()
np.arange()
np.ceil()
np.meshgrid()
np.repeat()
np.zeros()
np.ones / array construction where applicable
np.linalg.norm()
np.cross()
np.column_stack()
np.reshape()
np.floor()
np.clip()
np.unique()
np.exp()
np.maximum()
np.sum()
np.degrees()
np.save()
np.load()
np.count_nonzero()
```

## xraylib

Used for material attenuation data.

Important functions used:

``` python
xraylib.CS_Total_CP()
xraylib.GetCompoundDataNISTByName()
```

## Matplotlib

Used for visualization.

Important functions used include:

``` python
plt.figure()
plt.imshow()
plt.colorbar()
plt.xlabel()
plt.ylabel()
plt.title()
plt.show()
```

and 3D voxel plotting through:

``` python
ax.voxels()
```

## Python Standard Library

### `json`

Used to read the CT configuration:

``` python
json.load()
```

### `csv`

Used to save selected ray and detector data:

``` python
csv.writer()
```

### `os`

Used for output directory and file handling:

``` python
os.makedirs()
os.path.join()
os.environ
```

### `sys`

Used in the current `read_npy.py` environment setup.

------------------------------------------------------------------------

# 19. Configuration Dependency

The current `main.py` reads:

``` text
tissue_inter_4\ct_config_by_team2.json
```

The system geometry is obtained specifically from:

``` text
4_system_config_team
```

The detector values are obtained from:

``` text
3_detector_team
```

The source `kVp` is obtained from:

``` text
1_source_team
```

The current Phase 1 phantom parameters remain hard-coded in `main.py`.

------------------------------------------------------------------------

# 20. Output Directory

The simulation writes output to:

``` text
photon_output/
```

Typical output structure:

``` text
photon_output/
│
├── view_1_detector.npy
├── view_1_rays.csv
│
├── view_2_detector.npy
├── view_2_rays.csv
│
├── view_3_detector.npy
├── view_3_rays.csv
│
├── view_4_detector.npy
├── view_5_detector.npy
└── ...
```

CSV ray files are currently generated only for:

``` text
view 1
view 2
view 3
```

This is just to verify that it's working.
Detector `.npy` files are generated for every processed view.

------------------------------------------------------------------------

# 21. Execution

The main simulation is started through:

``` bash
python main.py
```

The execution follows:

``` text
Configuration
    ↓
Voxel phantom
    ↓
CT geometry
    ↓
X-ray spectrum
    ↓
View loop
    ↓
Detector pixels
    ↓
Deterministic rays
    ↓
Ray traversal
    ↓
Material attenuation
    ↓
Detector signal
    ↓
Detector image
    ↓
.npy / CSV output
```

------------------------------------------------------------------------

# 22. Phase 1 Scope

The current Phase 1 implementation focuses on establishing the
deterministic computational chain:

``` text
Source
  ↓
Detector geometry
  ↓
Ray generation
  ↓
Voxelized tissue
  ↓
Ray traversal
  ↓
X-ray attenuation
  ↓
Detector signal
```

The present implementation therefore provides the foundation for
producing detector-domain attenuation data from a rotating X-ray source
and voxelized tissue model.
