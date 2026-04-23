# formula_dependencies.py
"""
Maps parameters to formulas and tracks dependencies in the MF5.2 tire model.
Shows which formulas are affected when parameters change.
"""

from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class FormulaInfo:
    """Information about a formula and its dependencies."""
    name: str
    description: str
    category: str  # "Fx", "Fy", "Mz", "intermediate"
    parameters: List[str]  # Parameter codes used (e.g., ["PCX1", "PDX1"])
    equation: str  # Mathematical representation
    depends_on: List[str] = None  # Other formulas it depends on
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

# ============================================================================
# LONGITUDINAL FORCE (Fx) FORMULAS
# ============================================================================

FX_FORMULAS = {
    # Pure Slip Calculations
    "SHx": FormulaInfo(
        name="SHx", 
        description="Horizontal shift for longitudinal friction curve",
        category="Fx",
        parameters=["PHX1", "PHX2", "LHX"],
        equation="SHx = (pHx1 + pHx2 * ΔFz) * λHX",
        depends_on=[]
    ),
    "SVx": FormulaInfo(
        name="SVx",
        description="Vertical shift for longitudinal friction curve",
        category="Fx",
        parameters=["PVX1", "PVX2", "LMUX", "LVX"],
        equation="SVx = Fz(pVx1 + pVx2 * ΔFz) * λMUX * λVX",
        depends_on=[]
    ),
    "kappa_x": FormulaInfo(
        name="κₓ",
        description="Longitudinal slip with shift applied",
        category="Fx",
        parameters=[],
        equation="κₓ = κ + SHx",
        depends_on=["SHx"]
    ),
    "gamma_x": FormulaInfo(
        name="γₓ",
        description="Camber angle effect on longitudinal force",
        category="Fx",
        parameters=["LGAX"],
        equation="γₓ = γ * λGAX",
        depends_on=[]
    ),
    "mu_x": FormulaInfo(
        name="μₓ",
        description="Friction coefficient for longitudinal force",
        category="Fx",
        parameters=["PDX1", "PDX2", "PDX3", "LMUX"],
        equation="μₓ = (pDx1 + pDx2 * ΔFz)(1 - pDx3 * γₓ²) * λMUX",
        depends_on=["gamma_x"]
    ),
    "Cx": FormulaInfo(
        name="Cₓ",
        description="Shape factor for longitudinal friction curve",
        category="Fx",
        parameters=["PCX1", "LCX"],
        equation="Cₓ = pCx1 * λCX",
        depends_on=[]
    ),
    "Dx": FormulaInfo(
        name="Dₓ",
        description="Peak longitudinal friction force",
        category="Fx",
        parameters=[],
        equation="Dₓ = μₓ * Fz",
        depends_on=["mu_x"]
    ),
    "Ex": FormulaInfo(
        name="Eₓ",
        description="Curvature factor for longitudinal friction curve",
        category="Fx",
        parameters=["PEX1", "PEX2", "PEX3", "PEX4", "LEX"],
        equation="Eₓ = (pEx1 + pEx2 * ΔFz + pEx3 * ΔFz²)(1 - pEx4 * sgn(κₓ)) * λEX",
        depends_on=["kappa_x"]
    ),
    "Kx": FormulaInfo(
        name="Kₓ",
        description="Longitudinal slip stiffness",
        category="Fx",
        parameters=["PKX1", "PKX2", "PKX3", "LKX"],
        equation="Kₓ = Fz(pKx1 + pKx2 * ΔFz) * exp(pKx3 * ΔFz) * λKX",
        depends_on=[]
    ),
    "Bx": FormulaInfo(
        name="Bₓ",
        description="Stiffness factor for longitudinal friction curve",
        category="Fx",
        parameters=[],
        equation="Bₓ = Kₓ / (Cₓ * Dₓ)",
        depends_on=["Kx", "Cx", "Dx"]
    ),
    "Fx0": FormulaInfo(
        name="Fₓ₀",
        description="Pure slip longitudinal force",
        category="Fx",
        parameters=[],
        equation="Fₓ₀ = Dₓ * sin(Cₓ * arctan(Bₓ * κₓ - Eₓ(Bₓ * κₓ - arctan(Bₓ * κₓ)))) + SVx",
        depends_on=["Dx", "Cx", "Bx", "kappa_x", "Ex", "SVx"]
    ),
    
    # Combined Slip Calculations
    "SHxa": FormulaInfo(
        name="SHₓₐ",
        description="Horizontal shift for combined slip (longitudinal)",
        category="Fx",
        parameters=["RHX1"],
        equation="SHₓₐ = rHx1",
        depends_on=[]
    ),
    "alpha_s": FormulaInfo(
        name="αₛ",
        description="Slip angle with horizontal shift",
        category="Fx",
        parameters=[],
        equation="αₛ = α + SHₓₐ",
        depends_on=["SHxa"]
    ),
    "Bxa": FormulaInfo(
        name="Bₓₐ",
        description="Weighting factor for combined slip (longitudinal)",
        category="Fx",
        parameters=["RBX1", "RBX2", "LXAL"],
        equation="Bₓₐ = rBx1 * cos(arctan(rBx2 * κ)) * λXAL",
        depends_on=[]
    ),
    "Cxa": FormulaInfo(
        name="Cₓₐ",
        description="Shape factor for combined slip (longitudinal)",
        category="Fx",
        parameters=["RCX1"],
        equation="Cₓₐ = rCx1",
        depends_on=[]
    ),
    "Exa": FormulaInfo(
        name="Eₓₐ",
        description="Curvature factor for combined slip (longitudinal)",
        category="Fx",
        parameters=["REX1", "REX2"],
        equation="Eₓₐ = rEx1 + rEx2 * ΔFz",
        depends_on=[]
    ),
    "Dxa": FormulaInfo(
        name="Dₓₐ",
        description="Peak force for combined slip calculation",
        category="Fx",
        parameters=[],
        equation="Dₓ = Fₓ₀ / cos(Cₓₐ * arctan(Bₓₐ * SHₓₐ - Eₓₐ(Bₓₐ * SHₓₐ - arctan(Bₓₐ * SHₓₐ))))",
        depends_on=["Fx0", "Cxa", "Bxa", "SHxa", "Exa"]
    ),
    "Gxa": FormulaInfo(
        name="Gₓₐ",
        description="Weighting function for combined slip",
        category="Fx",
        parameters=[],
        equation="Gₓₐ = cos(Cₓₐ * arctan(Bₓₐ * αₛ - Eₓₐ(...))) / cos(Cₓₐ * arctan(Bₓₐ * SHₓₐ - Eₓₐ(...)))",
        depends_on=["Cxa", "Bxa", "alpha_s", "Exa", "SHxa"]
    ),
    "Fx": FormulaInfo(
        name="Fₓ",
        description="Final longitudinal force (combined slip)",
        category="Fx",
        parameters=[],
        equation="Fₓ = Fₓ₀ * Gₓₐ",
        depends_on=["Fx0", "Gxa"]
    ),
}

# ============================================================================
# LATERAL FORCE (Fy) FORMULAS
# ============================================================================

FY_FORMULAS = {
    # Pure Slip Calculations
    "gamma_y": FormulaInfo(
        name="γᵧ",
        description="Camber angle effect on lateral force",
        category="Fy",
        parameters=["LGAY"],
        equation="γᵧ = γ * λGAY",
        depends_on=[]
    ),
    "SHy": FormulaInfo(
        name="SHᵧ",
        description="Horizontal shift for lateral friction curve",
        category="Fy",
        parameters=["PHY1", "PHY2", "PHY3", "LHY"],
        equation="SHᵧ = (pHy1 + pHy2 * ΔFz) * λHY + pHy3 * γᵧ",
        depends_on=["gamma_y"]
    ),
    "SVy": FormulaInfo(
        name="SVᵧ",
        description="Vertical shift for lateral friction curve",
        category="Fy",
        parameters=["PVY1", "PVY2", "PVY3", "PVY4", "LMUY", "LVY"],
        equation="SVᵧ = Fz[(pVy1 + pVy2 * ΔFz) * λVY + (pVy3 + pVy4 * ΔFz) * γᵧ] * λMUY",
        depends_on=["gamma_y"]
    ),
    "alpha_y": FormulaInfo(
        name="αᵧ",
        description="Slip angle with shift applied",
        category="Fy",
        parameters=[],
        equation="αᵧ = α + SHᵧ",
        depends_on=["SHy"]
    ),
    "mu_y": FormulaInfo(
        name="μᵧ",
        description="Friction coefficient for lateral force",
        category="Fy",
        parameters=["PDY1", "PDY2", "PDY3", "LMUY"],
        equation="μᵧ = (pDy1 + pDy2 * ΔFz)(1 - pDy3 * γᵧ²) * λMUY",
        depends_on=["gamma_y"]
    ),
    "Cy": FormulaInfo(
        name="Cᵧ",
        description="Shape factor for lateral friction curve",
        category="Fy",
        parameters=["PCY1", "LCY"],
        equation="Cᵧ = pCy1 * λCY",
        depends_on=[]
    ),
    "Dy": FormulaInfo(
        name="Dᵧ",
        description="Peak lateral friction force",
        category="Fy",
        parameters=[],
        equation="Dᵧ = μᵧ * Fz",
        depends_on=["mu_y"]
    ),
    "Ey": FormulaInfo(
        name="Eᵧ",
        description="Curvature factor for lateral friction curve",
        category="Fy",
        parameters=["PEY1", "PEY2", "PEY3", "PEY4", "LEY"],
        equation="Eᵧ = (pEy1 + pEy2 * ΔFz)(1 - (pEy3 + pEy4 * γᵧ) * sgn(αᵧ)) * λEY",
        depends_on=["gamma_y", "alpha_y"]
    ),
    "Ky": FormulaInfo(
        name="Kᵧ",
        description="Cornering stiffness",
        category="Fy",
        parameters=["PKY1", "PKY2", "PKY3", "LFZ0", "LKY"],
        equation="Kᵧ = pKy1 * Fz0 * sin(2 * arctan(Fz / (pKy2 * Fz0 * λFZ0)))(1 - pKy3 * |γᵧ|) * λFZ0 * λKY",
        depends_on=["gamma_y"]
    ),
    "By": FormulaInfo(
        name="Bᵧ",
        description="Stiffness factor for lateral friction curve",
        category="Fy",
        parameters=[],
        equation="Bᵧ = Kᵧ / (Cᵧ * Dᵧ)",
        depends_on=["Ky", "Cy", "Dy"]
    ),
    "Fy0": FormulaInfo(
        name="Fᵧ₀",
        description="Pure slip lateral force",
        category="Fy",
        parameters=[],
        equation="Fᵧ₀ = Dᵧ * sin(Cᵧ * arctan(Bᵧ * αᵧ - Eᵧ(Bᵧ * αᵧ - arctan(Bᵧ * αᵧ)))) + SVᵧ",
        depends_on=["Dy", "Cy", "By", "alpha_y", "Ey", "SVy"]
    ),
    
    # Combined Slip Calculations
    "SHyk": FormulaInfo(
        name="SHᵧₖ",
        description="Horizontal shift for combined slip (lateral)",
        category="Fy",
        parameters=["PHY1", "PHY2"],
        equation="SHᵧₖ = pHy1 + pHy2 * ΔFz",
        depends_on=[]
    ),
    "kappa_s": FormulaInfo(
        name="κₛ",
        description="Longitudinal slip with shift",
        category="Fy",
        parameters=[],
        equation="κₛ = κ + SHᵧₖ",
        depends_on=["SHyk"]
    ),
    "Byk": FormulaInfo(
        name="Bᵧₖ",
        description="Weighting factor for combined slip (lateral)",
        category="Fy",
        parameters=["RBY1", "RBY2", "RBY3", "LYKA"],
        equation="Bᵧₖ = rBy1 * cos(arctan(rBy2(α - rBy3))) * λYKA",
        depends_on=[]
    ),
    "Cyk": FormulaInfo(
        name="Cᵧₖ",
        description="Shape factor for combined slip (lateral)",
        category="Fy",
        parameters=["RCY1"],
        equation="Cᵧₖ = rCy1",
        depends_on=[]
    ),
    "Eyk": FormulaInfo(
        name="Eᵧₖ",
        description="Curvature factor for combined slip (lateral)",
        category="Fy",
        parameters=["REY1", "REY2"],
        equation="Eᵧₖ = rEy1 + rEy2 * ΔFz",
        depends_on=[]
    ),
    "Dyk": FormulaInfo(
        name="Dᵧₖ",
        description="Peak force for combined slip calculation",
        category="Fy",
        parameters=[],
        equation="Dᵧₖ = Fᵧ₀ / cos(Cᵧₖ * arctan(Bᵧₖ * SHᵧₖ - Eᵧₖ(...)))",
        depends_on=["Fy0", "Cyk", "Byk", "SHyk", "Eyk"]
    ),
    "SVyk": FormulaInfo(
        name="SVᵧₖ",
        description="Vertical shift for combined slip",
        category="Fy",
        parameters=["PVY5", "PVY6", "LVYKA"],
        equation="SVᵧₖ = DVᵧₖ * sin(pVy5 * arctan(pVy6 * κ)) * λVYKA",
        depends_on=[]
    ),
    "Gyk": FormulaInfo(
        name="Gᵧₖ",
        description="Weighting function for combined slip",
        category="Fy",
        parameters=[],
        equation="Gᵧₖ = cos(Cᵧₖ * arctan(Bᵧₖ * κₛ - Eᵧₖ(...))) / cos(Cᵧₖ * arctan(Bᵧₖ * SHᵧₖ - Eᵧₖ(...)))",
        depends_on=["Cyk", "Byk", "kappa_s", "Eyk", "SHyk"]
    ),
    "Fy": FormulaInfo(
        name="Fᵧ",
        description="Final lateral force (combined slip)",
        category="Fy",
        parameters=[],
        equation="Fᵧ = Fᵧ₀ * Gᵧₖ + SVᵧₖ",
        depends_on=["Fy0", "Gyk", "SVyk"]
    ),
}

# ============================================================================
# ALIGNING MOMENT (Mz) FORMULAS
# ============================================================================

MZ_FORMULAS = {
    # Pneumatic Trail Calculations
    "gamma_z": FormulaInfo(
        name="γᶻ",
        description="Camber angle effect on aligning moment",
        category="Mz",
        parameters=["LGAZ"],
        equation="γᶻ = γ * λGAZ",
        depends_on=[]
    ),
    "SHt": FormulaInfo(
        name="SHₜ",
        description="Horizontal shift for pneumatic trail",
        category="Mz",
        parameters=["QHZ1", "QHZ2", "QHZ3", "QHZ4"],
        equation="SHₜ = pHz1 + pHz2 * ΔFz + (pHz3 + pHz4 * ΔFz) * γᶻ",
        depends_on=["gamma_z"]
    ),
    "Ct": FormulaInfo(
        name="Cₜ",
        description="Shape factor for pneumatic trail",
        category="Mz",
        parameters=["QCZ1"],
        equation="Cₜ = pCz1",
        depends_on=[]
    ),
    "Dt": FormulaInfo(
        name="Dₜ",
        description="Peak pneumatic trail",
        category="Mz",
        parameters=["QDZ1", "QDZ2", "QDZ3", "QDZ4", "LTR"],
        equation="Dₜ = Fz(pDz1 + pDz2 * ΔFz)(1 + pDz3 * γᶻ + pDz4 * γᶻ²) * (R₀/Fz0) * λT",
        depends_on=["gamma_z"]
    ),
    "Bt": FormulaInfo(
        name="Bₜ",
        description="Stiffness factor for pneumatic trail",
        category="Mz",
        parameters=["QBZ1", "QBZ2", "QBZ3", "QBZ4", "QBZ5"],
        equation="Bₜ = (pBz1 + pBz2 * ΔFz + pBz3 * ΔFz²)(1 + pBz4 * γᶻ + pBz5 * |γᶻ|) * (λKY/λMUY)",
        depends_on=["gamma_z"]
    ),
    "alpha_t": FormulaInfo(
        name="αₜ",
        description="Slip angle with shift for trail",
        category="Mz",
        parameters=[],
        equation="αₜ = α + SHₜ",
        depends_on=["SHt"]
    ),
    "Et": FormulaInfo(
        name="Eₜ",
        description="Curvature factor for pneumatic trail",
        category="Mz",
        parameters=["QEZ1", "QEZ2", "QEZ3", "QEZ4", "QEZ5"],
        equation="Eₜ = (pEz1 + pEz2 * ΔFz + pEz3 * ΔFz²)(1 + (pEz4 + pEz5 * γᶻ) * (2/π) * arctan(Bₜ * Cₜ * αₜ))",
        depends_on=["gamma_z", "alpha_t", "Bt", "Ct"]
    ),
    "t": FormulaInfo(
        name="t",
        description="Pneumatic trail",
        category="Mz",
        parameters=[],
        equation="t = Dₜ * cos(Cₜ * arctan(Bₜ * αₜ - Eₜ(Bₜ * αₜ - arctan(αₜ)))) * cos(α)",
        depends_on=["Dt", "Ct", "Bt", "alpha_t", "Et"]
    ),
    
    # Residual Torque Calculations
    "Dr": FormulaInfo(
        name="Dᵣ",
        description="Residual torque coefficient",
        category="Mz",
        parameters=["QDZ6", "QDZ7", "QDZ8", "QDZ9"],
        equation="Dᵣ = Fz[(pDz6 + pDz7 * ΔFz) * λMr + (pDz8 + pDz9 * ΔFz) * γᶻ] * R₀ * λMUY",
        depends_on=["gamma_z"]
    ),
    "SHf": FormulaInfo(
        name="SHf",
        description="Horizontal shift for reference slip angle",
        category="Mz",
        parameters=[],
        equation="SHf = SHᵧ + SVᵧ/Kᵧ",
        depends_on=[]  # Depends on Fy calculations
    ),
    "alpha_r": FormulaInfo(
        name="αᵣ",
        description="Reference slip angle for residual torque",
        category="Mz",
        parameters=[],
        equation="αᵣ = α + SHf",
        depends_on=["SHf"]
    ),
    "Br": FormulaInfo(
        name="Bᵣ",
        description="Stiffness factor for residual torque",
        category="Mz",
        parameters=["QBZ9", "QBZ10"],
        equation="Bᵣ = pBz9 * (λKY/λMUY) + pBz10 * Bᵧ * Cᵧ",
        depends_on=[]
    ),
    "Mzr": FormulaInfo(
        name="Mᶻʳ",
        description="Residual aligning torque",
        category="Mz",
        parameters=[],
        equation="Mᶻʳ = Dᵣ * cos(arctan(Bᵣ * αᵣ)) * cos(α)",
        depends_on=["Dr", "Br", "alpha_r"]
    ),
    
    # Final Aligning Moment
    "Mz": FormulaInfo(
        name="Mᶻ",
        description="Self-aligning moment (total)",
        category="Mz",
        parameters=[],
        equation="Mᶻ = -t * Fᵧ₀ + Mᶻʳ",
        depends_on=["t", "Fy0", "Mzr"]
    ),
}

# ============================================================================
# COMBINED DICTIONARY
# ============================================================================

ALL_FORMULAS = {
    **FX_FORMULAS,
    **FY_FORMULAS,
    **MZ_FORMULAS,
}

# ============================================================================
# PARAMETER TO FORMULA MAPPING
# ============================================================================

def build_parameter_to_formulas_map() -> Dict[str, List[str]]:
    """
    Build a reverse mapping: parameter code -> list of formula names that use it.
    Returns: {parameter_code: [formula_names]}
    """
    param_to_formulas = {}
    
    for formula_name, formula_info in ALL_FORMULAS.items():
        for param in formula_info.parameters:
            if param not in param_to_formulas:
                param_to_formulas[param] = []
            param_to_formulas[param].append(formula_name)
    
    return param_to_formulas


def get_affected_formulas(parameter_code: str) -> Dict[str, any]:
    """
    Get all formulas affected by a parameter change.
    Returns: {
        'direct': [formula names that directly use this parameter],
        'indirect': [formula names affected through dependencies],
        'details': {formula_name: FormulaInfo}
    }
    """
    param_to_formulas = build_parameter_to_formulas_map()
    
    direct_formulas = param_to_formulas.get(parameter_code, [])
    indirect_formulas = set()
    
    # Find all formulas that depend on the directly affected ones
    def find_dependents(formula_names: List[str]) -> Set[str]:
        dependents = set()
        for formula_name in formula_names:
            for other_name, other_info in ALL_FORMULAS.items():
                if formula_name in other_info.depends_on:
                    dependents.add(other_name)
        return dependents
    
    # Recursively find all dependents
    current_level = set(direct_formulas)
    seen = set(direct_formulas)
    
    while current_level:
        next_level = find_dependents(list(current_level))
        new_formulas = next_level - seen
        indirect_formulas.update(new_formulas)
        seen.update(new_formulas)
        current_level = new_formulas
    
    # Gather details
    details = {}
    all_affected = set(direct_formulas) | indirect_formulas
    for formula_name in all_affected:
        if formula_name in ALL_FORMULAS:
            details[formula_name] = ALL_FORMULAS[formula_name]
    
    return {
        "direct": direct_formulas,
        "indirect": list(indirect_formulas),
        "details": details,
    }


def get_parameter_info(parameter_code: str) -> Dict[str, any]:
    """
    Get comprehensive information about a parameter's role in formulas.
    """
    affected = get_affected_formulas(parameter_code)
    
    # Group by category
    by_category = {}
    for formula_name in affected["direct"] + affected["indirect"]:
        if formula_name in ALL_FORMULAS:
            formula = ALL_FORMULAS[formula_name]
            cat = formula.category
            if cat not in by_category:
                by_category[cat] = {"direct": [], "indirect": []}
            
            if formula_name in affected["direct"]:
                by_category[cat]["direct"].append(formula_name)
            else:
                by_category[cat]["indirect"].append(formula_name)
    
    return {
        "parameter": parameter_code,
        "affected_formulas": affected,
        "by_category": by_category,
    }


if __name__ == "__main__":
    # Test the system
    print("Testing formula dependencies...")
    print("\nParameter PCX1 affects:")
    result = get_parameter_info("PCX1")
    print(f"  Direct: {result['affected_formulas']['direct']}")
    print(f"  Indirect: {result['affected_formulas']['indirect']}")
    
    print("\nParameter PDX1 affects:")
    result = get_parameter_info("PDX1")
    print(f"  Direct: {result['affected_formulas']['direct']}")
    print(f"  Indirect: {result['affected_formulas']['indirect']}")
