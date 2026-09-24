import numpy as np


def load_geometry(config):
    system = config["4_system_config_team"]

    SID = system["sid_mm"]
    SDD = system["sdd_mm"]

    views_per_rotation = system["num_views_per_rotation"]
    total_views = system["total_views"]

    table_feed_per_rotation = system["table_feed_per_rotation_mm"]    

    detector_radius = SDD - SID

    angle_increment = 2.0 * np.pi / views_per_rotation

    view_indices = np.arange(total_views)

    theta = view_indices * angle_increment

    
    y_step = table_feed_per_rotation / views_per_rotation
    y_positions = view_indices * y_step

    return {
        "SID": SID,
        "SDD": SDD,
        "detector_radius": detector_radius,
        "views_per_rotation": views_per_rotation,
        "total_views": total_views,
        "view_indices": view_indices,
        "theta": theta,
        "y_positions": y_positions
    }


def get_view_geometry(geometry, view_index):

    SID = geometry["SID"]
    detector_radius = geometry["detector_radius"]

    theta = geometry["theta"][view_index]
    y = geometry["y_positions"][view_index]

    # Source rotates around Y axis
    source_position = np.array([
        SID * np.cos(theta),
        y,
        SID * np.sin(theta)
    ])

    # Detector is opposite the source
    detector_position = np.array([
        -detector_radius * np.cos(theta),
        y,
        -detector_radius * np.sin(theta)
    ])
    
    #------------------------------------------------------------
    # if     views_per_rotation = 94
    #        table_feed_per_rotation = 20.64 mm
    # then 
    #      Y movement per view = 20.64 / 94 ≈ 0.2196 mm/view
    #    but change the json file for easy computation and the values also get changed
    
    
        #     View 0:
        # θ = 0°
        # Y = 0

        # View 1:
        # θ = 3.8298°
        # Y = 0.2196 mm

        # View 2:
        # θ = 7.6596°
        # Y = 0.4391 mm

        # ...

        # View 94:
        # θ = 360°
        # Y = 20.64 mm
        
        # ----------------------------------------------------------
    

    central_direction = detector_position - source_position
    central_direction /= np.linalg.norm(central_direction)

    return source_position, detector_position, central_direction