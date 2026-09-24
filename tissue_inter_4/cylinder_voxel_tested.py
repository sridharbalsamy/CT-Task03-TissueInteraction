# cylinder_voxel.py

import numpy as np
import matplotlib.pyplot as plt




def create_cylinder_voxel(
    radius_mm=25.0,
    height_mm=50.0,
    voxel_size_mm=1,
    density=1.0,
    material_id=1
):
    """
    Creates a 3D voxelized cylinder.

    Cylinder axis:
        Z-axis

    Parameters
    ----------
    radius_mm : float
        Cylinder radius in mm.
        Must be <= CT bore radius.

    height_mm : float
        Cylinder height in mm.

    voxel_size_mm : float
        Size of each cubic voxel in mm.

    density : float
        Uniform density assigned to all cylinder voxels.

    material_id : int
        Material identifier.

    Returns
    -------
    voxel_density : np.ndarray
        3D array containing density.
        Shape = (Z, Y, X)

    voxel_material : np.ndarray
        3D array containing material ID.
    """

    # CT bore
    bore_diameter_mm = 541.0
    bore_radius_mm = bore_diameter_mm / 2.0

    # Safety check
    if radius_mm > bore_radius_mm:
        raise ValueError(
            f"Cylinder radius ({radius_mm} mm) exceeds "
            f"CT bore radius ({bore_radius_mm} mm)."
        )

    # Number of voxels
    nx = int(np.ceil(2 * radius_mm / voxel_size_mm))
    ny = nx
    nz = int(np.ceil(height_mm / voxel_size_mm))

    # Make dimensions even/consistent
    x = (np.arange(nx) - (nx - 1) / 2) * voxel_size_mm
    y = (np.arange(ny) - (ny - 1) / 2) * voxel_size_mm
    z = (np.arange(nz) - (nz - 1) / 2) * voxel_size_mm

    # 2D circular cross-section
    X, Y = np.meshgrid(x, y, indexing="xy")

    cylinder_mask_2d = (X**2 + Y**2) <= radius_mm**2

    # Replicate along Z
    cylinder_mask = np.repeat(
        cylinder_mask_2d[np.newaxis, :, :],
        nz,
        axis=0
    )

    # Density volume
    voxel_density = np.zeros(
        (nz, ny, nx),
        dtype=np.float32
    )

    voxel_density[cylinder_mask] = density

    # Material volume
    voxel_material = np.zeros(
        (nz, ny, nx),
        dtype=np.int16
    )

    voxel_material[cylinder_mask] = material_id

    return voxel_density, voxel_material


def plot_voxel_cylinder(voxel_density, voxel_size_mm=1.0):
    """
    Plot the voxelized cylinder in 3D.
    """

    # Occupied voxels
    voxel_mask = voxel_density > 0

    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, projection="3d")

    ax.voxels(
        voxel_mask,
        edgecolor="k",
        linewidth=0.05
    )

    # Axes
    ax.set_xlabel("X voxel")
    ax.set_ylabel("Y voxel")
    ax.set_zlabel("Z voxel")

    ax.set_title("3D Voxelized Cylinder")

    # Equal aspect ratio
    ax.set_box_aspect([
        voxel_density.shape[2],
        voxel_density.shape[1],
        voxel_density.shape[0]
    ])

    plt.show()


if __name__ == "__main__":
    # changingg here cchanges the default value
    density, material = create_cylinder_voxel(
        radius_mm=25.0,
        height_mm=50.0,
        voxel_size_mm=1.0,
        density=1.0,
        material_id=1
    )

    print("Voxel density shape :", density.shape)
    print("Voxel material shape:", material.shape)

    print("Number of tissue voxels:",
          np.count_nonzero(density))

    print("Voxel density values:",
          np.unique(density))

    print("Material IDs:",
          np.unique(material))

    plot_density = density[::5, ::5, ::5]
    
    plot_voxel_cylinder(
        density,
        # plot_density,
        voxel_size_mm=2.5
    )