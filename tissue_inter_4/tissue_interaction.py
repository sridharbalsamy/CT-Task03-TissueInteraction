import numpy as np

from material import linear_attenuation_coefficient


def ray_box_intersection(
    origin,
    direction,
    box_min,
    box_max
):

    t_min = -np.inf
    t_max = np.inf

    for axis in range(3):

        if abs(direction[axis]) < 1e-12:

            if (
                origin[axis] < box_min[axis]
                or origin[axis] > box_max[axis]
            ):
                return None

            continue

        t1 = (
            box_min[axis] - origin[axis]
        ) / direction[axis]

        t2 = (
            box_max[axis] - origin[axis]
        ) / direction[axis]

        t_near = min(t1, t2)
        t_far = max(t1, t2)

        t_min = max(t_min, t_near)
        t_max = min(t_max, t_far)

        if t_min > t_max:
            return None

    return t_min, t_max


def traverse_ray(
    origin,
    direction,
    voxel_material,
    voxel_size_mm
):

    nz, ny, nx = voxel_material.shape

    volume_size = np.array([
        nx * voxel_size_mm,
        ny * voxel_size_mm,
        nz * voxel_size_mm
    ])

    volume_min = -volume_size / 2.0
    volume_max = volume_size / 2.0

    intersection = ray_box_intersection(
        origin,
        direction,
        volume_min,
        volume_max
    )

    if intersection is None:
        return {}

    t_entry, t_exit = intersection

    if t_exit < 0:
        return {}

    t = max(t_entry, 0.0)

    point = origin + t * direction

    voxel = np.floor(
        (point - volume_min) / voxel_size_mm
    ).astype(int)

    voxel[0] = np.clip(voxel[0], 0, nx - 1)
    voxel[1] = np.clip(voxel[1], 0, ny - 1)
    voxel[2] = np.clip(voxel[2], 0, nz - 1)

    ix, iy, iz = voxel

    step_x = 1 if direction[0] > 0 else -1
    step_y = 1 if direction[1] > 0 else -1
    step_z = 1 if direction[2] > 0 else -1

    if direction[0] != 0:
        next_x = (
            volume_min[0]
            + (ix + (step_x > 0)) * voxel_size_mm
        )
        t_max_x = (
            next_x - origin[0]
        ) / direction[0]
        t_delta_x = abs(
            voxel_size_mm / direction[0]
        )
    else:
        t_max_x = np.inf
        t_delta_x = np.inf

    if direction[1] != 0:
        next_y = (
            volume_min[1]
            + (iy + (step_y > 0)) * voxel_size_mm
        )
        t_max_y = (
            next_y - origin[1]
        ) / direction[1]
        t_delta_y = abs(
            voxel_size_mm / direction[1]
        )
    else:
        t_max_y = np.inf
        t_delta_y = np.inf

    if direction[2] != 0:
        next_z = (
            volume_min[2]
            + (iz + (step_z > 0)) * voxel_size_mm
        )
        t_max_z = (
            next_z - origin[2]
        ) / direction[2]
        t_delta_z = abs(
            voxel_size_mm / direction[2]
        )
    else:
        t_max_z = np.inf
        t_delta_z = np.inf

    material_lengths = {}

    while (
        0 <= ix < nx
        and 0 <= iy < ny
        and 0 <= iz < nz
        and t <= t_exit
    ):

        material_id = int(
            voxel_material[iz, iy, ix]
        )

        next_t = min(
            t_max_x,
            t_max_y,
            t_max_z,
            t_exit
        )

        path_length = max(
            0.0,
            next_t - t
        )

        material_lengths[material_id] = (
            material_lengths.get(material_id, 0.0)
            + path_length
        )

        t = next_t

        if t >= t_exit:
            break

        if t_max_x <= t_max_y and t_max_x <= t_max_z:
            ix += step_x
            t_max_x += t_delta_x

        elif t_max_y <= t_max_x and t_max_y <= t_max_z:
            iy += step_y
            t_max_y += t_delta_y

        else:
            iz += step_z
            t_max_z += t_delta_z

    return material_lengths


def precompute_mu(
    material_ids,
    energies
):

    mu_table = {}

    for material_id in material_ids:

        mu_table[material_id] = np.array([
            linear_attenuation_coefficient(
                material_id,
                energy
            )
            for energy in energies
        ])

    return mu_table


def calculate_spectral_transmission(
    material_lengths,
    energies,
    spectrum,
    mu_table
):

    attenuation = np.zeros(
        len(energies)
    )

    for material_id, path_length in material_lengths.items():

        # Ignore background air for Phase 1
        if material_id == 0:
            continue

        attenuation += (
            mu_table[material_id]
            * path_length
        )

    transmission = np.exp(-attenuation)

    # Energy-integrating detector - produces an energy-integrated detector signal for each detector pixe
    detector_signal = np.sum(
        spectrum
        * energies
        * transmission
    )
    

    return detector_signal


def tissue_interaction(
    rays,
    voxel_material,
    voxel_size_mm,
    energies,
    spectrum
):

    num_rays = rays.shape[0]

    detector_signal = np.zeros(
        num_rays,
        dtype=np.float64
    )
         
    material_ids = np.unique(
        voxel_material
    )

    mu_table = precompute_mu(
        material_ids,
        energies
    )

    for i in range(num_rays):

        origin = rays[i, 0:3]
        direction = rays[i, 3:6]

        material_lengths = traverse_ray(
            origin,
            direction,
            voxel_material,
            voxel_size_mm
        )

        detector_signal[i] = (
            calculate_spectral_transmission(
                material_lengths,
                energies,
                spectrum,
                mu_table
            )
        )

    return detector_signal