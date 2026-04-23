# aliases.py
"""Mapping from your tyre JSON structure into internal dict format."""

from typing import Dict, Any

# Longitudinal aliases
LONGITUDINAL_ALIASES = {
    "pCx1": "PCX1",
    "pDx1": "PDX1",
    "pDx2": "PDX2",
    "pDx3": "PDX3",
    "pEx1": "PEX1",
    "pEx2": "PEX2",
    "pEx3": "PEX3",
    "pEx4": "PEX4",
    "pKx1": "PKX1",
    "pKx2": "PKX2",
    "pKx3": "PKX3",
    "pHx1": "PHX1",
    "pHx2": "PHX2",
    "pVx1": "PVX1",
    "pVx2": "PVX2",
    "rBx1": "RBX1",
    "rBx2": "RBX2",
    "rCx1": "RCX1",
    "rEx1": "REX1",
    "rEx2": "REX2",
    "rHx1": "RHX1",
    # "bAllowLongitudinalTyreShifts": "bAllowLongitudinalTyreShifts"
}

LATERAL_ALIASES = {
    "pCy1": "PCY1",
    "pDy1": "PDY1",
    "pDy2": "PDY2",
    "pDy3": "PDY3",
    "pEy1": "PEY1",
    "pEy2": "PEY2",
    "pEy3": "PEY3",
    "pEy4": "PEY4",
    "pKy1": "PKY1",
    "pKy2": "PKY2",
    "pKy3": "PKY3",
    "pHy1": "PHY1",
    "pHy2": "PHY2",
    "pHy3": "PHY3",
    "pVy1": "PVY1",
    "pVy2": "PVY2",
    "pVy3": "PVY3",
    "pVy4": "PVY4",
    "rBy1": "RBY1",
    "rBy2": "RBY2",
    "rBy3": "RBY3",
    "rCy1": "RCY1",
    "rEy1": "REY1",
    "rEy2": "REY2",
    "rHy1": "RHY1",
    "rHy2": "RHY2",
    "rVy1": "RVY1",
    "rVy2": "RVY2",
    "rVy3": "RVY3",
    "rVy4": "RVY4",
    "rVy5": "RVY5",
    "rVy6": "RVY6",
}

ALIGNING_ALIASES = {
    "qBz1": "QBZ1",
    "qBz2": "QBZ2",
    "qBz3": "QBZ3",
    "qBz4": "QBZ4",
    "qBz5": "QBZ5",
    "qBz9": "QBZ9",
    "qBz10": "QBZ10",
    "qCz1": "QCZ1",
    "qDz1": "QDZ1",
    "qDz2": "QDZ2",
    "qDz3": "QDZ3",
    "qDz4": "QDZ4",
    "qDz6": "QDZ6",
    "qDz7": "QDZ7",
    "qDz8": "QDZ8",
    "qDz9": "QDZ9",
    "qEz1": "QEZ1",
    "qEz2": "QEZ2",
    "qEz3": "QEZ3",
    "qEz4": "QEZ4",
    "qEz5": "QEZ5",
    "qHz1": "QHZ1",
    "qHz2": "QHZ2",
    "qHz3": "QHZ3",
    "qHz4": "QHZ4",
    "sSz1": "SSZ1",
    "sSz2": "SSZ2",
    "sSz3": "SSZ3",
    "sSz4": "SSZ4",
}

OVERTURNING_COEFFICIENTS = {
    "qsx1": "QSX1",
    "qsx2": "QSX2",
    "qsx3": "QSX3"
    }

SCALING_ALIASES = {
    "lambda_FZ0": "LFZ0",
    "lambda_CX": "LCX",
    "lambda_MUX": "LMUX",
    "lambda_EX": "LEX",
    "lambda_KX": "LKX",
    "lambda_HX": "LHX",
    "lambda_VX": "LVX",
    "lambda_GAX": "LGAX",
    "lambda_CY": "LCY",
    "lambda_MUY": "LMUY",
    "lambda_EY": "LEY",
    "lambda_KY": "LKY",
    "lambda_HY": "LHY",
    "lambda_VY": "LVY",
    "lambda_GAY": "LGAY",
    "lambda_T": "LTR",
    "lambda_Mr": "LRES", # beware in the papers this often appears as just lambda_r 
    "lambda_GAZ": "LGAZ",
    "lambda_Mx": "LMX",
    "lambda_vMx": "LVMX",
    "lambda_My": "LMY",
    "lambda_XAL": "LXAL",
    "lambda_YKA": "LYKA",
    "lambda_VYKA": "LVYKA",
    "lambda_s": "LS",
}

def _extract_group(tyre: Dict[str, Any], block_name: str, aliases: Dict[str, str]) -> Dict[str, float]:
    if block_name not in tyre or tyre[block_name] is None:
        # If block missing, return zeros for all expected keys (or 1.0 for lambdas)
        out = {}
        for internal_name in aliases:
            if internal_name.startswith("lambda_"):
                out[internal_name] = 1.0
            else:
                out[internal_name] = 0.0
        return out
    src = tyre[block_name]
    out: Dict[str, float] = {}
    for internal_name, json_name in aliases.items():
        if json_name in src:
            out[internal_name] = float(src[json_name])
        # Default lambda values to 1 if missing
        elif internal_name.startswith("lambda_"):
            out[internal_name] = 1.0  # default scaling factor if missing

    # Special logic for bAllowLongitudinalTyreShifts in LONGITUDINAL_COEFFICIENTS
    if block_name == "LONGITUDINAL_COEFFICIENTS":
        allow_shifts = src.get("bAllowLongitudinalTyreShifts", None)
        # Accept boolean, string 'true'/'false', or missing
        if isinstance(allow_shifts, str):
            allow_shifts_bool = allow_shifts.strip().lower() == "true"
        else:
            allow_shifts_bool = bool(allow_shifts)
        if not allow_shifts_bool:
            # Set PHX1, PHX2, PVX1, PVX2, RHX1 to 0 if false, 'false', or missing
            for key in ["pHx1", "pHx2", "pVx1", "pVx2", "rHx1"]:
                out[key] = 0.0
    return out


def convert_json_to_internal(full_json: Dict[str, Any], side: str) -> Dict[str, Any]:
    tyre = full_json["config"][side]
    internal: Dict[str, Any] = {
        "Fz0": float(tyre["VERTICAL"]["FNOMIN"]),
        "R0": float(tyre["rUnloaded"]),
        "Fx": _extract_group(tyre, "LONGITUDINAL_COEFFICIENTS", LONGITUDINAL_ALIASES),
        "Fy": _extract_group(tyre, "LATERAL_COEFFICIENTS", LATERAL_ALIASES),
        "Mz": _extract_group(tyre, "ALIGNING_COEFFICIENTS", ALIGNING_ALIASES),
        "Scale": _extract_group(tyre, "SCALING_COEFFICIENTS", SCALING_ALIASES),
        "Overturning": _extract_group(tyre, "OVERTURNING_COEFFICIENTS", OVERTURNING_COEFFICIENTS),
        # Use default VRef=1.0 if missing
        "VRef": float(tyre.get("rollingResistance", {}).get("VRef", 1.0)),
    }
    return internal
