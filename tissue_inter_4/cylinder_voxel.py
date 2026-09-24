import numpy as np


def create_cylinder_voxel(
    radius_mm=25.0,
    height_mm=50.0,
    voxel_size_mm=1.0,
    density=1.0,
    material_id=1
):
    # cap the radius and diameter 
    nx = int(np.ceil(2 * radius_mm / voxel_size_mm))  
    ny = int(np.ceil(height_mm / voxel_size_mm))

    nz = nx   # radius is equal at all points from center 
    x = (np.arange(nx)- (nx - 1) / 2) * voxel_size_mm   # centrify 
    y = (np.arange(ny)- (ny - 1) / 2) * voxel_size_mm
    z = (np.arange(nz)- (nz - 1) / 2) * voxel_size_mm

    X, Z = np.meshgrid(x,z,indexing="xy")

    cylinder_mask_2d = (X**2 + Z**2) <= radius_mm**2

    cylinder_mask = np.repeat(cylinder_mask_2d[np.newaxis, :, :], ny,axis=0)

    voxel_density = np.zeros(
        (ny, nz, nx),
        dtype=np.float32
    )

    voxel_density[cylinder_mask] = density

    voxel_material = np.zeros(
        (ny, nz, nx),
        dtype=np.int16
    )

    voxel_material[cylinder_mask] = material_id

    return voxel_density, voxel_material