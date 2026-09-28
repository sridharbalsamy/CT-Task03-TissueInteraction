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
    
    # make sure the distance travelled isn't -ve
    t = max(t_entry, 0.0)

    # point of entry of the ray into the material (refer LAST PAGE of NOTEBOOK)
    point = origin + t * direction

    # converts this physical position into a voxel inde
    voxel = np.floor(
        (point - volume_min) / voxel_size_mm
    ).astype(int)

    voxel[0] = np.clip(voxel[0], 0, nx - 1)
    voxel[1] = np.clip(voxel[1], 0, ny - 1)
    voxel[2] = np.clip(voxel[2], 0, nz - 1)

    # identifies current voxel
    ix, iy, iz = voxel

    step_x = 1 if direction[0] > 0 else -1
    step_y = 1 if direction[1] > 0 else -1
    step_z = 1 if direction[2] > 0 else -1

   ## -------- key part in handling voxel to voxel movement --------
   #  Difficult to understand without an example 
    ''' 
    (t_max_x,t_max_y,t_max_z) --> The next point along the ray where the ray will cross a voxel boundary in X, Y or Z.
    '''
    if direction[0] != 0:
        next_x = (
            volume_min[0]
            + (ix + (step_x > 0)) * voxel_size_mm
        )
        t_max_x = (next_x - origin[0]) / direction[0]
        t_delta_x = abs(voxel_size_mm / direction[0])  # how much t much increase to complete one voxel in that direction
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
        0 <= ix < nx  # x coordinate within range
        and 0 <= iy < ny  # y coordinate withtin the range 
        and 0 <= iz < nz # z coordinate within range
        and t <= t_exit
    ):

        material_id = int(
            voxel_material[iz, iy, ix]
        )

        # find the next boundary 
        next_t = min(
            t_max_x,
            t_max_y,
            t_max_z,
            t_exit
        )

        # path travelled by the ray
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
    
    # returns a mu_table in dict format of size 2
    ## first key gives array of 'mu' of 1st material for all energies provided (1,1.5, 2, 2.5, ...)
    ## second key gives array of 'mu' of 2nd material for all energies
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

    # Initiating total attenuation exponent of each material
    # in future we do 
  
    atten_expo = np.zeros(
        len(energies)
    )

    for material_id, path_length in material_lengths.items():
        '''
        for each material_id --> each material that is seen during a ray traversal
        for path_length --> contains the total path length of a material
                            despite encountering other materials in between
        (see the example at the bottom to understand)
        '''
        
        
        # Ignore background air for Phase 1 of implementation
        if material_id == 0:
            continue

        # A(E)=∑_m ​μ_m​(E) * L_m
        #  L_m --> path length through material m, unit: mm 
        # ​μ_m = attenuation coefficient of material m, mm⁻¹ 
        atten_expo += (
            mu_table[material_id]
            * path_length
        )

    # -------------- Here comes Beer-Lambert -------------------
    # out of loop of the materials
    # calculate the I/I0 (or) N/N0 fraction 
    transmission = np.exp(-atten_expo)

    # Energy-integrating detector - produces an energy-integrated detector signal for each detector pixel
    ##    ------- PROBLEM IDENTIFIED ----
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
    '''
    rays obtained from source.py
     --> stacked origin and directions
    '''
    

    # rays is a numpy array here 
    num_rays = rays.shape[0]
    

    detector_signal = np.zeros(
        num_rays,
        dtype=np.float64
    )
         
    material_ids = np.unique(
        voxel_material
    )

    # --- computes the mu_table using  the material_ids and energies available ----
    # given energies increase by .5kVp
    mu_table = precompute_mu(
        material_ids,
        energies
    )

    # for all the rays in one view
    for i in range(num_rays):
        
        origin = rays[i, 0:3]  # extract columns 0,1,2
        direction = rays[i, 3:6]   # extract columns 3,4,5

        material_lengths = traverse_ray(
            origin,
            direction,
            voxel_material,
            voxel_size_mm
        )

        # --- one scalar output as detector_signal[i] ---
        detector_signal[i] = calculate_spectral_transmission(material_lengths,energies,spectrum,mu_table)

    return detector_signal








### -------------------------------------------------------------------------------------------
'''
Two main functions used here are:
1. traverse_ray()
2. calculate_spectral_transmission()


**How does the traverse_ray() work ?

* for example :

    material_id = 0 --> air
    material_id = 1 --> soft_tissue
 
          |  0.8 mm |  1.0 mm |  0.6 mm |
    Ray → | Voxel 1 | Voxel 2 | Voxel 3 |
          |  Tissue |  Tissue |   Air   |
          
    code accumulates --
        material_lengths[material_id] += path_length

    the output would be --
      -- key = material_id, value = path_length --
        
        material_lengths = {
                    1: 1.8, --> 1 + 0.8 mm
                    0: 0.6
                    }   

** How does calculate_spectral_transmisson() work ?






'''
