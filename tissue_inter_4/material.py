import numpy as np
import xraylib


# ==============================================================
# MATERIAL DEFINITIONS
# ==============================================================

MATERIALS = {

    # ----------------------------------------------------------
    # 0 = Air
    # ----------------------------------------------------------
    0: {
        "name": "Air",
        "nist_name": "Air, Dry (near sea level)",
    },

    # ----------------------------------------------------------
    # 1 = Soft tissue
    # ----------------------------------------------------------
    1: {
        "name": "Soft Tissue",
        "nist_name": "Tissue, Soft (ICRP)",
    },

    # ----------------------------------------------------------
    # 2 = Bone
    # ----------------------------------------------------------
    2: {
        "name": "Cortical Bone",
        "nist_name": "Bone, Cortical (ICRP)",
    },

    # ----------------------------------------------------------
    # 3 = Lung
    # ----------------------------------------------------------
    3: {
        "name": "Lung",
        "nist_name": "Lung (ICRP)",
    },

    # ----------------------------------------------------------
    # 4 = Adipose
    # ----------------------------------------------------------
    4: {
        "name": "Adipose",
        "nist_name": "Adipose Tissue (ICRP)",
    },

    # ----------------------------------------------------------
    # 5 = Water
    # ----------------------------------------------------------
    5: {
        "name": "Water",
        "nist_name": "Water, Liquid",
    },

    # ----------------------------------------------------------
    # 6 = Skeletal muscle
    # ----------------------------------------------------------
    6: {
        "name": "Skeletal Muscle",
        "nist_name": "Muscle, Skeletal",
    },
}


# ==============================================================
# MATERIAL INFORMATION
# ==============================================================

def get_material_info(material_id):
    """
    Returns material information.
    """

    if material_id not in MATERIALS:
        raise ValueError(
            f"Unknown material ID: {material_id}"
        )

    return MATERIALS[material_id]


# ==============================================================
# MASS ATTENUATION COEFFICIENT
# ==============================================================

def mass_attenuation_coefficient(
    material_id,
    energy_keV
):
    """
    Returns mass attenuation coefficient.

    Units:
        cm^2 / g

    Uses xraylib NIST compound data.
    """

    material = get_material_info(
        material_id
    )

    value = xraylib.CS_Total_CP(
        material["nist_name"],
        float(energy_keV)
    )

    return value


# ==============================================================
# DENSITY
# ==============================================================

def material_density(material_id):
    """
    Returns material density.

    Units:
        g / cm^3
    """

    material = get_material_info(
        material_id
    )

    data = xraylib.GetCompoundDataNISTByName(
        material["nist_name"]
    )

    return data["density"]


# ==============================================================
# LINEAR ATTENUATION COEFFICIENT
# ==============================================================

def linear_attenuation_coefficient(
    material_id,
    energy_keV
):
    """
    Returns linear attenuation coefficient.

    μ = (μ/rho) * rho

    xraylib:
        μ/rho -> cm^2/g
        rho   -> g/cm^3

    Therefore:
        μ -> cm^-1

    Converted to:
        mm^-1
    """

    mu_over_rho = mass_attenuation_coefficient(
        material_id,
        energy_keV
    )

    rho = material_density(
        material_id
    )

    mu_cm = mu_over_rho * rho

    mu_mm = mu_cm / 10.0

    return mu_mm


# ==============================================================
# DEBUG / INFORMATION
# ==============================================================

def print_material_database():

    print("\nMaterial database")
    print("-" * 60)

    for material_id, material in MATERIALS.items():

        density = material_density(
            material_id
        )

        print(
            f"{material_id}: "
            f"{material['name']:20s} "
            f"density = {density:.4f} g/cm^3"
        )