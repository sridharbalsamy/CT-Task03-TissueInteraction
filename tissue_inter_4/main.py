import json
import numpy as np
import csv  # for post tisuue_inter result viewing
import os # for post tisuue_inter result viewing

from syncer import (
    load_geometry,
    get_view_geometry
)

from spectrum import generate_spectrum
from source import generate_rays
from detector import (
    generate_detector_pixels
)
from tissue_interaction import (
    tissue_interaction
)
from cylinder_voxel import (
    create_cylinder_voxel
)

CONFIG_FILE = r"tissue_inter_4\ct_config_by_team2.json"

def save_view_rays(
    view_id,
    rays,
    detector_signal,
    output_dir="photon_output"
):

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(
        output_dir,
        f"view_{view_id}_rays.csv"
    )

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "view_id",
            "ray_id",
            "x",
            "y",
            "z",
            "dx",
            "dy",
            "dz",
            "detector_signal"
        ])

        for ray_id in range(rays.shape[0]):

            writer.writerow([
                view_id,
                ray_id,
                rays[ray_id, 0],
                rays[ray_id, 1],
                rays[ray_id, 2],
                rays[ray_id, 3],
                rays[ray_id, 4],
                rays[ray_id, 5],
                detector_signal[ray_id]
            ])

    print(f"Saved: {filename}")


def main():

    # --------------------------------------------------
    # Load configuration
    # --------------------------------------------------

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    print("\n### CONFIG LOADED ###")

    source_config = config["1_source_team"]

    detector_config = config["3_detector_team"]


    # --------------------------------------------------
    # Hard-coded Phase 1 values
    # --------------------------------------------------

    voxel_size_mm = 1.0

    phantom_radius_mm = 25.0
    phantom_height_mm = 50.0

    phantom_density = 1.0
    phantom_material_id = 1


    # --------------------------------------------------
    # Detector values from JSON
    # --------------------------------------------------

    detector_rows = detector_config["detector_rows" ]
    detector_channels = detector_config["detector_channels"]
    
    pixel_width_mm = detector_config["detector_element_width_mm"]
    pixel_height_mm = detector_config["detector_element_height_mm"]


    # --------------------------------------------------
    # Create phantom
    # --------------------------------------------------

    print("\n### CREATING VOXEL PHANTOM ###")

    voxel_density, voxel_material = create_cylinder_voxel(
        radius_mm=phantom_radius_mm,
        height_mm=phantom_height_mm,
        voxel_size_mm=voxel_size_mm,
        density=phantom_density,
        material_id=phantom_material_id
    )

    print(
        "Voxel shape:",
        voxel_material.shape
    )


    # --------------------------------------------------
    # Geometry
    # --------------------------------------------------

    print("\n### LOADING GEOMETRY ###")

    geometry = load_geometry(config)

    print(
        "Views:",
        geometry["total_views"]
    )

    print(
        "Views / rotation:",
        geometry["views_per_rotation"]
    )


    # --------------------------------------------------
    # Spectrum
    # --------------------------------------------------

    energies, spectrum = generate_spectrum(
        kVp=source_config["kvp"],
        Z=74,
        filter_thickness=1.5
    )
    # it's outputs are used in tissue interaction
    print("\n### SPECTRUM GENERATED ###")


    # --------------------------------------------------
    # View loop
    # --------------------------------------------------

    for view_index in range(
        geometry["total_views"]
    ):

        print(
            f"\n### VIEW {view_index + 1}"
            f"/{geometry['total_views']} ###"
        )

        source_position, detector_position, central_direction = (
            get_view_geometry(
                geometry,
                view_index
            )
        )
        
        
        theta_deg = np.degrees(
        geometry["theta"][view_index]
        )

        y_position = geometry["y_positions"][view_index]

        print(f"Rotation angle : {theta_deg:.4f}°")
        print(f"Table position : {y_position:.4f} mm")
        print(f"Source position   : "f"({source_position[0]:.4f}, "f"{source_position[1]:.4f}, "f"{source_position[2]:.4f}) mm")

        print(f"Detector position : "f"({detector_position[0]:.4f}, "f"{detector_position[1]:.4f}, "f"{detector_position[2]:.4f}) mm")


        # --------------------------------------------------
        # Detector pixels
        # --------------------------------------------------

        detector_pixels = generate_detector_pixels(
            detector_position=detector_position,
            source_position=source_position,
            detector_rows=detector_rows,
            detector_channels=detector_channels,
            pixel_width_mm=pixel_width_mm,
            pixel_height_mm=pixel_height_mm
        )


        # --------------------------------------------------
        # Deterministic rays
        # --------------------------------------------------
        ''' Determine the source position for that view.
            Determine the detector element position.
            Draw a ray from source → detector element.
            Normalize that vector to get the ray direction.
            Generate photons along that predefined ray geometry.
            64 x 888=56,832 detector rays/view
            
            '''
        rays = generate_rays(
            source_position,
            detector_pixels
        )

        print(
            "Rays:",
            rays.shape[0]
        )


        # --------------------------------------------------
        # Tissue interaction
        # --------------------------------------------------

        detector_signal = tissue_interaction(
            rays,
            voxel_material,
            voxel_size_mm,
            energies,
            spectrum
        )
        
        # storage of detetctor signals - post tissue interaction 
        # Export rays for selected views  in csv 
        # format is view_{view_id}_rays
        view_id = view_index + 1
        if view_id in [1, 2, 3]:
            save_view_rays(
            view_id=view_id,
            rays=rays,
            detector_signal=detector_signal
            )


        # --------------------------------------------------
        # Detector image
        # --------------------------------------------------

        detector_image = detector_signal.reshape(detector_rows, detector_channels)
        np.save(
            f"photon_output/view_{view_id}_detector.npy",
            detector_image
        )

        print( "Detector image:",detector_image.shape)

        print("Total signal:",np.sum(detector_image))  


        # --------------------------------------------------
        # Rotation information
        # --------------------------------------------------

        if (
            view_index
            % geometry["views_per_rotation"]
            == 0
        ):

            print( "Source:",source_position)
            print("Detector:",detector_position)
            print("Central direction:",central_direction)


if __name__ == "__main__":
    main()