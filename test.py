# param_optimiser.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Any

import json
import time

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

import matplotlib.pyplot as plt


# -----------------------------
# Utilities
# -----------------------------
def now_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    r = y_true - y_pred
    return float(np.sqrt(np.mean(r * r)))


# -----------------------------
# Formula interface + registry
# -----------------------------
@dataclass
class Formula:
    name: str
    # predict(x, params) -> y
    predict: Callable[[np.ndarray, Dict[str, float]], np.ndarray]
    param_defaults: Dict[str, float]
    # bounds: (lower, upper) dicts OR None
    param_bounds: Optional[Tuple[Dict[str, float], Dict[str, float]]] = None
    description: str = ""


class FormulaRegistry:
    def __init__(self) -> None:
        self._items: Dict[str, Formula] = {}

    def register(self, f: Formula) -> None:
        if f.name in self._items:
            raise ValueError(f"Formula '{f.name}' already registered.")
        self._items[f.name] = f

    def get(self, name: str) -> Formula:
        if name not in self._items:
            raise KeyError(f"Unknown formula '{name}'. Available: {sorted(self._items)}")
        return self._items[name]

    def list(self) -> List[str]:
        return sorted(self._items.keys())


FORMULAS = FormulaRegistry()


# -----------------------------
# Example predefined formulas
# -----------------------------
def _linear(x: np.ndarray, p: Dict[str, float]) -> np.ndarray:
    # y = m*x + c
    return p["m"] * x + p["c"]


FORMULAS.register(
    Formula(
        name="linear",
        predict=_linear,
        param_defaults={"m": 1.0, "c": 0.0},
        param_bounds=({"m": -np.inf, "c": -np.inf}, {"m": np.inf, "c": np.inf}),
        description="y = m*x + c",
    )
)


def _exp_decay(x: np.ndarray, p: Dict[str, float]) -> np.ndarray:
    # y = a * exp(-b*x) + c
    return p["a"] * np.exp(-p["b"] * x) + p["c"]


FORMULAS.register(
    Formula(
        name="exp_decay",
        predict=_exp_decay,
        param_defaults={"a": 1.0, "b": 1.0, "c": 0.0},
        param_bounds=({"a": -np.inf, "b": 0.0, "c": -np.inf}, {"a": np.inf, "b": np.inf, "c": np.inf}),
        description="y = a*exp(-b*x) + c, with b >= 0",
    )
)


# -----------------------------
# Fit configuration + result
# -----------------------------
@dataclass
class FitConfig:
    formula_name: str
    x_col: str
    y_col: str
    # parameters fixed at given values (not optimised)
    fixed_params: Dict[str, float]
    # starting guesses for free params (overrides defaults)
    initial_params: Dict[str, float]
    # optional bounds override for free params: {param: (lo, hi)}
    bounds: Dict[str, Tuple[float, float]]
    version_name: str
    notes: str = ""


@dataclass
class FitResult:
    best_params: Dict[str, float]
    free_param_names: List[str]
    success: bool
    message: str
    cost: float
    rmse: float
    nfev: int


# -----------------------------
# Core fitting logic
# -----------------------------
def fit_formula(
    df: pd.DataFrame,
    config: FitConfig,
    output_root: Path = Path("fit_runs"),
    store: bool = True,
    show_plot: bool = True,
) -> Tuple[FitResult, pd.DataFrame, Path]:
    """
    Returns: (FitResult, predictions_df, run_dir)
    predictions_df columns: x, y_meas, y_pred, residual
    """
    formula = FORMULAS.get(config.formula_name)

    x = df[config.x_col].to_numpy(dtype=float)
    y = df[config.y_col].to_numpy(dtype=float)

    # Determine free params
    all_defaults = dict(formula.param_defaults)
    fixed = dict(config.fixed_params)

    free_names = [k for k in all_defaults.keys() if k not in fixed]
    if not free_names:
        raise ValueError("No free parameters to optimise (everything is fixed).")

    # Initial vector
    p0 = []
    for name in free_names:
        if name in config.initial_params:
            p0.append(float(config.initial_params[name]))
        else:
            p0.append(float(all_defaults[name]))
    p0 = np.asarray(p0, dtype=float)

    # Bounds
    # Start from formula bounds if present, then override with config.bounds
    lo = np.full_like(p0, -np.inf, dtype=float)
    hi = np.full_like(p0, np.inf, dtype=float)

    if formula.param_bounds is not None:
        lo_dict, hi_dict = formula.param_bounds
        for i, name in enumerate(free_names):
            if name in lo_dict:
                lo[i] = float(lo_dict[name])
            if name in hi_dict:
                hi[i] = float(hi_dict[name])

    for i, name in enumerate(free_names):
        if name in config.bounds:
            lo[i] = float(config.bounds[name][0])
            hi[i] = float(config.bounds[name][1])

    def unpack_params(theta: np.ndarray) -> Dict[str, float]:
        p = dict(all_defaults)
        p.update(fixed)
        for i, name in enumerate(free_names):
            p[name] = float(theta[i])
        return p

    def residuals(theta: np.ndarray) -> np.ndarray:
        p = unpack_params(theta)
        yhat = formula.predict(x, p)
        return (yhat - y)

    sol = least_squares(residuals, p0, bounds=(lo, hi))

    best_params = unpack_params(sol.x)
    y_pred = formula.predict(x, best_params)

    preds = pd.DataFrame(
        {
            config.x_col: x,
            config.y_col: y,
            "y_pred": y_pred,
            "residual": y - y_pred,
        }
    )

    result = FitResult(
        best_params=best_params,
        free_param_names=free_names,
        success=bool(sol.success),
        message=str(sol.message),
        cost=float(sol.cost),
        rmse=rmse(y, y_pred),
        nfev=int(sol.nfev),
    )

    run_dir = Path("")
    if store:
        run_dir = ensure_dir(output_root / config.version_name / now_stamp())
        (run_dir / "config.json").write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
        (run_dir / "params_best.json").write_text(json.dumps(best_params, indent=2), encoding="utf-8")
        (run_dir / "report.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
        preds.to_csv(run_dir / "predictions.csv", index=False)

    # Plot raw vs fitted
    if show_plot:
        plt.figure()
        plt.scatter(x, y, label="Measured", s=12)
        # draw a line in x order for readability
        order = np.argsort(x)
        plt.plot(x[order], y_pred[order], label="Fitted")
        plt.xlabel(config.x_col)
        plt.ylabel(config.y_col)
        plt.title(f"{config.formula_name} | RMSE={result.rmse:.4g} | {config.version_name}")
        plt.legend()
        plt.tight_layout()

        if store:
            plt.savefig(run_dir / "plot.png", dpi=160)

        plt.show()

    return result, preds, run_dir


# -----------------------------
# Data loading helpers
# -----------------------------
def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_excel(path: str | Path, sheet_name: str | int = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name)


# -----------------------------
# Add your own formulas
# -----------------------------
def register_custom_formula(
    name: str,
    predict_fn: Callable[[np.ndarray, Dict[str, float]], np.ndarray],
    param_defaults: Dict[str, float],
    bounds: Optional[Tuple[Dict[str, float], Dict[str, float]]] = None,
    description: str = "",
) -> None:
    FORMULAS.register(
        Formula(
            name=name,
            predict=predict_fn,
            param_defaults=param_defaults,
            param_bounds=bounds,
            description=description,
        )
    )
