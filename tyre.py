# tyre.py
# Python 3.9 — conversión directa desde VB.NET (Magic Formula 5.2)
# Fuente original: clase VB "Tyre" (Daniel)  — mantiene unidades y signados
# Dependencias estándar únicamente (math)

from math import sin, cos, atan, exp, sqrt, pi, radians, degrees, isfinite
import numpy as np
import pandas as pd
import json
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import copy
    
    
def _sign(x):
    """
    Devuelve -1, 0 o 1 según el signo de x.
    Soporta escalar, numpy.ndarray y pandas.Series.
    """
    # Caso vectorial (NumPy/Series) con broadcasting
    if hasattr(x, "__array__"):
        x_arr = np.asarray(x, dtype=float)
        return np.where(x_arr > 0, 1, np.where(x_arr < 0, -1, 0)).astype(int)
    # Caso escalar
    try:
        xf = float(x)
    except Exception:
        # Si no es convertible, devuelve 0 como fallback neutro
        return 0
    return 1 if xf > 0 else (-1 if xf < 0 else 0)

class Tyre:
    """
    Traducción de la clase VB 'Tyre' a Python 3.9.
    Notas de sistema de referencia (ISO - rueda), unidades y fórmulas MF5.2
    """

    # -------------------------
    # CONSTANTES
    # -------------------------
    phi = (sqrt(5)-1)/2
    number_iterations = 10
    rad_to_deg = 180.0 / pi
    deg_to_rad = 1.0 / rad_to_deg
    golden_section_alpha_lo_deg = -25.0
    golden_section_alpha_hi_deg = 25.0
    angle_tol_rad = 0.01 * deg_to_rad
    golden_section_kappa_lo = 0
    golden_section_kappa_hi = 0.3
    alpha_kappa_tolerance = 0.0001
    
    PARAM_ORDER = [
        "PCX1", "PDX1", "PDX2", "PDX3",
        "PEX1", "PEX2", "PEX3", "PEX4",
        "PKX1", "PKX2", "PKX3", "PHX1",
        "PHX2", "PVX1", "PVX2", "RBX1",
        "RBX2", "RCX1", "REX1", "REX2",
        "RHX1", "PCY1", "PDY1", "PDY2",
        "PDY3", "PEY1", "PEY2", "PEY3",
        "PEY4", "PKY1", "PKY2", "PKY3",
        "PHY1", "PHY2", "PHY3", "PVY1",
        "PVY2", "PVY3", "PVY4", "RBY1",
        "RBY2", "RBY3", "RCY1", "REY1",
        "REY2", "RHY1", "RHY2", "RVY1",
        "RVY2", "RVY3", "RVY4", "RVY5",
        "RVY6", "QBZ1", "QBZ2", "QBZ3",
        "QBZ4", "QBZ5", "QBZ9", "QBZ10",
        "QCZ1", "QDZ1", "QDZ2", "QDZ3",
        "QDZ4", "QDZ6", "QDZ7", "QDZ8",
        "QDZ9", "QEZ1", "QEZ2", "QEZ3",
        "QEZ4", "QEZ5", "QHZ1", "QHZ2",
        "QHZ3", "QHZ4", "SSZ1", "SSZ2",
        "SSZ3", "SSZ4", "LFZ0", "LCX",
        "LUX", "LEX", "LKX", "LHX",
        "LVX", "LYX", "LCY", "LUY",
        "LEY", "LKY", "LHY", "LVY",
        "LYY", "LT", "LMR", "LYZ",
        "LXA", "LYKA", "LVYKA", "LS",
        "FZ0", "R0", "LR_R0", "a1",
        "a2", "a3", "b1", "b2",
        "p1", "f1", "c1", "calc_tyre_pressure_psi"
    ]

    # -------------------------
    # CONSTRUCTOR
    # -------------------------
    def __init__(self):
        self.PCX1 = self.PDX1 = self.PDX2 = self.PDX3 = 0.0
        self.PEX1 = self.PEX2 = self.PEX3 = self.PEX4 = 0.0
        self.PKX1 = self.PKX2 = self.PKX3 = 0.0
        self.PHX1 = self.PHX2 = self.PVX1 = self.PVX2 = 0.0
        self.RBX1 = self.RBX2 = self.RCX1 = self.REX1 = self.REX2 = self.RHX1 = 0.0
        self.PCY1 = self.PDY1 = self.PDY2 = self.PDY3 = 0.0
        self.PEY1 = self.PEY2 = self.PEY3 = self.PEY4 = 0.0
        self.PKY1 = self.PKY2 = self.PKY3 = 0.0
        self.PHY1 = self.PHY2 = self.PHY3 = 0.0
        self.PVY1 = self.PVY2 = self.PVY3 = self.PVY4 = 0.0
        self.RBY1 = self.RBY2 = self.RBY3 = 0.0
        self.RCY1 = self.REY1 = self.REY2 = self.RHY1 = self.RHY2 = 0.0
        self.RVY1 = self.RVY2 = self.RVY3 = self.RVY4 = self.RVY5 = self.RVY6 = 0.0
        self.QBZ1 = self.QBZ2 = self.QBZ3 = self.QBZ4 = self.QBZ5 = 0.0
        self.QBZ9 = self.QBZ10 = self.QCZ1 = 0.0
        self.QDZ1 = self.QDZ2 = self.QDZ3 = self.QDZ4 = self.QDZ6 = self.QDZ7 = 0.0
        self.QDZ8 = self.QDZ9 = 0.0
        self.QEZ1 = self.QEZ2 = self.QEZ3 = self.QEZ4 = self.QEZ5 = 0.0
        self.QHZ1 = self.QHZ2 = self.QHZ3 = self.QHZ4 = 0.0
        self.SSZ1 = self.SSZ2 = self.SSZ3 = self.SSZ4 = 0.0
        self.LFZ0 = self.LCX = self.LUX = self.LEX = self.LKX = self.LHX = self.LVX = self.LYX = 1.0
        self.LCY = self.LUY = self.LEY = self.LKY = self.LHY = self.LVY = self.LYY = 1.0
        self.LT = self.LMR = self.LYZ = self.LXA = self.LYKA = self.LVYKA = self.LS = 1.0

        self.FZ0 = self.R0 = 0.0
        self.LR_R0 = self.a1 = self.a2 = self.a3 = 0.0
        self.b1 = self.b2 = self.p1 = self.f1 = self.c1 = 0.0
        self.calc_tyre_pressure_psi = 0.0

    # -------------------------
    # INITIALIZE (igual que VB: array + flag)
    # -------------------------
    def initialize(self, data_in):

        (
            self.PCX1, self.PDX1, self.PDX2, self.PDX3,
            self.PEX1, self.PEX2, self.PEX3, self.PEX4,
            self.PKX1, self.PKX2, self.PKX3, self.PHX1,
            self.PHX2, self.PVX1, self.PVX2, self.RBX1,
            self.RBX2, self.RCX1, self.REX1, self.REX2,
            self.RHX1, self.PCY1, self.PDY1, self.PDY2,
            self.PDY3, self.PEY1, self.PEY2, self.PEY3,
            self.PEY4, self.PKY1, self.PKY2, self.PKY3,
            self.PHY1, self.PHY2, self.PHY3, self.PVY1,
            self.PVY2, self.PVY3, self.PVY4, self.RBY1,
            self.RBY2, self.RBY3, self.RCY1, self.REY1,
            self.REY2, self.RHY1, self.RHY2, self.RVY1,
            self.RVY2, self.RVY3, self.RVY4, self.RVY5,
            self.RVY6, self.QBZ1, self.QBZ2, self.QBZ3,
            self.QBZ4, self.QBZ5, self.QBZ9, self.QBZ10,
            self.QCZ1, self.QDZ1, self.QDZ2, self.QDZ3,
            self.QDZ4, self.QDZ6, self.QDZ7, self.QDZ8,
            self.QDZ9, self.QEZ1, self.QEZ2, self.QEZ3,
            self.QEZ4, self.QEZ5, self.QHZ1, self.QHZ2,
            self.QHZ3, self.QHZ4, self.SSZ1, self.SSZ2,
            self.SSZ3, self.SSZ4, self.LFZ0, self.LCX,
            self.LUX, self.LEX, self.LKX, self.LHX,
            self.LVX, self.LYX, self.LCY, self.LUY,
            self.LEY, self.LKY, self.LHY, self.LVY,
            self.LYY, self.LT, self.LMR, self.LYZ,
            self.LXA, self.LYKA, self.LVYKA, self.LS,
            self.FZ0, self.R0, self.LR_R0, self.a1,
            self.a2, self.a3, self.b1, self.b2,
            self.p1, self.f1, self.c1, self.calc_tyre_pressure_psi,
        ) = data_in[:116] 
        
        #for param_name in Tyre.PARAM_ORDER:
        #    value = getattr(self, param_name)
        #    if value == 0 or value == 0.0:
                #print(f"Parametro sin valor en JSON: {param_name}")

    # -------------------------
    # TYRE STIFFNESS
    # -------------------------
    def tyre_stiffness_n_per_mm(
        self,
        speed_kmh: float = 0.0,
        camber_angle_deg: float = 0.0,
        fy_n: float = 0.0,
        Fz_n: float = 0.1,
    ) -> float:
        """
        Fórmula 'Pirelli 2014 GP2 Loaded Radius'
        dR = (Fz / (p1*IP + a1*V2 + a2*V + a3 + c1*|Ca| + f1*Fy^2/Fz)) + b1*V2 + b2*V
        En el VB, devuelven directamente el denominador (stiffness) sin el término dR.
        """
        # En el VB: TyreStiffness_nmm = p1*IP + a1*V^2 + a2*V + a3 + c1*|Ca| + f1*Fy^2/Fz
        # (calc_tyre_pressure_psi = IP)
        return (
            self.p1 * self.calc_tyre_pressure_psi
            + self.a1 * (speed_kmh ** 2)
            + self.a2 * speed_kmh
            + self.a3
            + self.c1 * abs(camber_angle_deg)
            + (self.f1 * (fy_n ** 2) / Fz_n)
        )

    # -------------------------
    # LATERAL FORCE (Fy) y ÓPTIMO DE ALFA
    # -------------------------
    def Fy(self, alpha_rad: float, kappa: float, inclination_angle_rad: float, Fz_n: float) -> float:
        """
        Fuerza lateral absoluta (Magic Formula 5.2 simplificada).
        Se eliminan efectos de lado opuesto y sentido de giro.
        """
        if Fz_n <= 0:
            Fz_n = 0.01

        FZ0p = self.FZ0 * self.LFZ0
        dFz = (Fz_n - FZ0p) / FZ0p
        gammaY = inclination_angle_rad * self.LYY
        Muy = (self.PDY1 + self.PDY2 * dFz) * (1 - self.PDY3 * (gammaY ** 2)) * self.LUY
        Dy = Muy * Fz_n
        Cy = self.PCY1 * self.LCY
        Ky = (self.PKY1 * self.FZ0 * np.sin(2 * np.arctan(Fz_n / (self.PKY2 * self.FZ0 * self.LFZ0))) * (1 - self.PKY3 * abs(gammaY)) * self.LFZ0 * self.LKY)
        By = Ky / (Cy * Dy) if (Cy * Dy) != 0 else 0.0
        SHy = (self.PHY1 + self.PHY2 * dFz) * self.LHY + self.PHY3 * gammaY
        alphaY = alpha_rad + SHy
        Ey = (self.PEY1 + self.PEY2 * dFz) * (1 - (self.PEY3 + self.PEY4 * gammaY) * _sign(alphaY)) * self.LEY
        SVy = (
            Fz_n
            * ((self.PVY1 + self.PVY2 * dFz) * self.LVY + (self.PVY3 + self.PVY4 * dFz) * gammaY)
            * self.LUY
        )
        Fy0 = Dy * np.sin(Cy * np.arctan(By * alphaY - Ey * (By * alphaY - np.arctan(By * alphaY)))) + SVy

        SHYk = self.RHY1 + self.RHY2 * dFz
        DVYk = Muy * Fz_n * (self.RVY1 + self.RVY2 * dFz + self.RVY3 * inclination_angle_rad) * np.cos(np.arctan(self.RVY4 * alpha_rad))
        SVYk = DVYk * np.sin(self.RVY5 * np.arctan(self.RVY6 * kappa)) * self.LVYKA
        CYk = self.RCY1
        EYk = self.REY1 + self.REY2 * dFz
        BYk = self.RBY1 * np.cos(np.arctan(self.RBY2 * (alpha_rad - self.RBY3))) * self.LYKA
        denom = np.cos(CYk * np.arctan(BYk * SHYk - EYk * (BYk * SHYk - np.arctan(BYk * SHYk))))
        DYk = Fy0 / denom if denom != 0 else 0.0
        kS = kappa + SHYk
        Fy = DYk * np.cos(CYk * np.arctan(BYk * kS - EYk * (BYk * kS - np.arctan(BYk * kS)))) + SVYk

        return (Fy)*self.rGripFactor



    def optimal_alpha_deg(self, kappa, gamma_rad, Fz_n):
        """
        Busca el ángulo de deriva (α) que maximiza |Fy| sin importar el signo ni el sentido de giro.
        """
        alpha_lo = np.deg2rad(self.golden_section_alpha_lo_deg)
        alpha_hi = np.deg2rad(self.golden_section_alpha_hi_deg)
        phi = (np.sqrt(5) - 1) / 2
        tol = np.deg2rad(0.01)
        n_iter = 50

        for _ in range(n_iter):
            if abs(alpha_hi - alpha_lo) < tol:
                break
            a1 = alpha_hi - (alpha_hi - alpha_lo) * phi
            a2 = alpha_lo + (alpha_hi - alpha_lo) * phi
            fy1 = (self.Fy(a1, kappa, gamma_rad, Fz_n))
            fy2 = (self.Fy(a2, kappa, gamma_rad, Fz_n))
            if fy1 > fy2:
                alpha_hi = a2
            else:
                alpha_lo = a1

        alpha_opt = 0.5 * (alpha_lo + alpha_hi)
        return np.rad2deg(alpha_opt)

    # -------------------------
    # LONGITUDINAL FORCE (Fx) y ÓPTIMO DE KAPPA
    # -------------------------
    def Fx(self, alpha_rad: float, kappa: float, inclination_angle_rad: float, Fz_n: float) -> float:
        """
        Fuerza longitudinal (Magic Formula 5.2). Unidades y signos como en VB.
        """
        if Fz_n <= 0:
            Fz_n = 0.01

        FZ0p = self.FZ0 * self.LFZ0
        dFz = (Fz_n - FZ0p) / FZ0p
        gammaX = inclination_angle_rad * self.LYX
        Mux = (self.PDX1 + self.PDX2 * dFz) * (1 - self.PDX3 * (gammaX ** 2)) * self.LUX
        Dx = Mux * Fz_n
        Cx = self.PCX1 * self.LCX
        Kx = Fz_n * (self.PKX1 + self.PKX2 * dFz) * exp(self.PKX3 * dFz) * self.LKX
        Bx = Kx / (Cx * Dx) if (Cx * Dx) != 0 else 0.0
        SHx = (self.PHX1 + self.PHX2 * dFz) * self.LHX
        kappaX = kappa + SHx
        Ex = (self.PEX1 + self.PEX2 * dFz + self.PEX3 * (dFz ** 2)) * (1 - self.PEX4 * _sign(kappaX)) * self.LEX
        SVx = Fz_n * (self.PVX1 + self.PVX2 * dFz) * self.LVX * self.LUX
        Fx0 = Dx * sin(Cx * atan(Bx * kappaX - Ex * (Bx * kappaX - atan(Bx * kappaX)))) + SVx

        SHXa = self.RHX1
        EXa = self.REX1 + self.REX2 * dFz
        CXa = self.RCX1
        BXa = self.RBX1 * cos(atan(self.RBX2 * kappa)) * self.LXA
        alphaS = alpha_rad + SHXa
        denom = cos(CXa * atan(BXa * SHXa - EXa * (BXa * SHXa - atan(BXa * SHXa))))
        DXa = Fx0 / denom if denom != 0 else 0.0
        # Gxa calculado pero no utilizado explícitamente (igual que en VB)
        Fx = DXa * cos(CXa * atan(BXa * alphaS - EXa * (BXa * alphaS - atan(BXa * alphaS))))
        return Fx*self.rGripFactor

    def optimal_kappa(self, alpha_rad: float, gamma_rad: float, Fz_n: float, braking_bool: bool = True) -> float:
        """
        Devuelve el slip ratio (1/100) óptimo (máximo |Fx|) usando sección áurea.
        Por convenio ISO: freno -> kappa negativo; tracción -> positivo.
        """
        if braking_bool:
            k_lo = -self.golden_section_kappa_hi
            k_hi = self.golden_section_kappa_lo
        else:
            k_lo = self.golden_section_kappa_lo
            k_hi = self.golden_section_kappa_hi

        for _ in range(self.number_iterations * 2):
            if abs(k_hi - k_lo) < self.angle_tol_rad:
                break

            k1 = k_hi - (k_hi - k_lo) * self.phi
            k2 = k_lo + (k_hi - k_lo) * self.phi

            fx1 = self.Fx(alpha_rad, k1, gamma_rad, Fz_n)
            fx2 = self.Fx(alpha_rad, k2, gamma_rad, Fz_n)

            if fx1 > fx2:
                if not braking_bool:
                    k_hi = k2
                else:
                    k_lo = k1
            else:
                if not braking_bool:
                    k_lo = k1
                else:
                    k_hi = k2

        return ((k_lo + k_hi) * 0.5)
    
    
    def longitudinal(self, gamma_rad: float, alpha_deg, Fz_n: float, braking_bool: bool = True):

        kappa = self.optimal_kappa(alpha_deg*self.deg_to_rad, gamma_rad, Fz_n, braking_bool)
        Fx_max_tyre = self.Fx(alpha_deg*self.deg_to_rad, kappa, gamma_rad, Fz_n)

        return kappa, Fx_max_tyre

    @staticmethod
    def build_tyre_param_sequence(tyre_cfg: dict) -> list[float]:
        """
        Convierte la sección de un neumático del JSON (front/rear)
        en la lista de 116 parámetros que espera Tyre.initialize.
        """

        longi = tyre_cfg.get("LONGITUDINAL_COEFFICIENTS", {})
        lat   = tyre_cfg.get("LATERAL_COEFFICIENTS", {})
        align = tyre_cfg.get("ALIGNING_COEFFICIENTS", {})
        scale = tyre_cfg.get("SCALING_COEFFICIENTS", {})
        vert  = tyre_cfg.get("VERTICAL", {})
        loaded = tyre_cfg.get("radiusEquations", {}).get("loadedRadius", {})

        # Mapeos especiales porque los nombres no coinciden exactamente
        # (PCV1/PDV* en tu clase vs PCY1/PDY* en el JSON, etc.)
        special_paths = {
            # escalados verticales/radio
            "FZ0": ("VERTICAL", "FNOMIN"),
            "R0": ("root", "rUnloaded"),
            "a1": ("LOADED_RADIUS", "a1"),
            "a2": ("LOADED_RADIUS", "a2"),
            "a3": ("LOADED_RADIUS", "a3"),
            "b1": ("LOADED_RADIUS", "b1"),
            "b2": ("LOADED_RADIUS", "b2"),
            "p1": ("LOADED_RADIUS", "p1"),
            "f1": ("LOADED_RADIUS", "f1"),
            "c1": ("LOADED_RADIUS", "c1"),
        }

        def get_special(name: str):
            sect, key = special_paths[name]
            if sect == "LATERAL_COEFFICIENTS":
                return lat[key]
            if sect == "VERTICAL":
                return vert[key]
            if sect == "LOADED_RADIUS":
                return loaded[key]
            if sect == "root":
                return tyre_cfg[key]
            raise KeyError(name)

        def get_value(name: str) -> float:
            # 1) Directamente en LONGITUDINAL / ALIGNING / SCALING
            if name in longi:
                return longi[name]
            if name in lat:
                return lat[name]
            if name in align:
                return align[name]
            if name in scale:
                return scale[name]
            if name in loaded:
                return loaded[name]

            # 2) Mapeos especiales
            if name in special_paths:
                return get_special(name)

            # 3) Algunos escalados que sí coinciden con el JSON
            if name == "LFZ0":
                return scale.get("LFZ0", 1.0)
            if name == "LCX":
                return scale.get("LCX", 1.0)
            if name == "LEX":
                return scale.get("LEX", 1.0)
            if name == "LKX":
                return scale.get("LKX", 1.0)
            if name == "LHX":
                return scale.get("LHX", 0.0)
            if name == "LVX":
                return scale.get("LVX", 0.0)
            if name == "LS":
                return scale.get("LS", 1.0)

            # 4) Por defecto (si no lo tenemos en el JSON)
            #    Puedes cambiar estos defaults según tu VB original
            if name.startswith("L"):   # escalados
                return 1.0
            return 0.0

        # Construye la secuencia en el orden que espera Tyre.initialize
        values = [get_value(name) for name in Tyre.PARAM_ORDER]
        r_grip_factor = tyre_cfg.get("rGripFactor", 1.0)
        return values, r_grip_factor
    
    @classmethod
    def load_vehicle_tyres(cls, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            vehicle = json.load(f)

        tyres_cfg = vehicle["config"]["tyres"]  # front / rear / etc.

        front_cfg = tyres_cfg["front"]
        rear_cfg  = tyres_cfg["rear"]

        front_seq, front_r_grip_factor = cls.build_tyre_param_sequence(front_cfg)
        rear_seq, rear_r_grip_factor  = cls.build_tyre_param_sequence(rear_cfg)

        front_tyre = cls()
        rear_tyre  = cls()

        front_tyre.initialize(front_seq)
        rear_tyre.initialize(rear_seq)
        
        front_tyre.rGripFactor = front_r_grip_factor
        rear_tyre.rGripFactor  = rear_r_grip_factor

        return front_tyre, rear_tyre
    
    @staticmethod
    def calc_pure_slip_angle(Fl_tyre, Rl_tyre, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_front_deg, camber_rear_deg):
        df = pd.DataFrame()
        for f in Fz_range_n:
            for slip in slip_angle_range_rad:
                Fy_val_F = Fl_tyre.Fy(-slip,0,-camber_front_deg*Tyre.deg_to_rad,f)
                Fy_val_R = Rl_tyre.Fy(-slip,0,-camber_rear_deg*Tyre.deg_to_rad,f)
                new_row = pd.DataFrame([{
                "Fz": f,
                "slip_angle_deg": slip,
                "Fy_F": Fy_val_F,
                "Fy_R": Fy_val_R,
                "rMuyTyreF": Fy_val_F/f,
                "rMuyTyreR": Fy_val_R/f
                }])
                df = pd.concat([df, new_row], ignore_index=True)
        return df
    
    @staticmethod
    def calc_pure_slip_ratio(Fl_tyre, Rl_tyre, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_front_deg, camber_rear_deg):
        df = pd.DataFrame()
        for f in Fz_range_n:
            for slip in slip_ratio_range:
                Fx_val_F = Fl_tyre.Fx(0,-slip,-camber_front_deg*Tyre.deg_to_rad,f)
                Fx_val_R = Rl_tyre.Fx(0,-slip,-camber_rear_deg*Tyre.deg_to_rad,f)
                new_row = pd.DataFrame([{
                "Fz": f,
                "slip_ratio": slip,
                "Fx_F": Fx_val_F,
                "Fx_R": Fx_val_R,
                "rMuxTyreF": Fx_val_F/f,
                "rMuxTyreR": Fx_val_R/f
                }])
                df = pd.concat([df, new_row], ignore_index=True)
        return df
    
    @staticmethod
    def tyre_elipse(tyre, NBINS, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_deg):

        edges = np.linspace(-np.pi, np.pi, NBINS+1)
        best = {}

        for f in Fz_range_n:
            for slip_angle in slip_angle_range_rad:
                for slip_ratio in slip_ratio_range:

                    Fy = tyre.Fy(slip_angle, slip_ratio, -camber_deg*Tyre.deg_to_rad, f)
                    Fx = tyre.Fx(slip_angle, slip_ratio, -camber_deg*Tyre.deg_to_rad, f)

                    x = Fx / f  
                    y = Fy / f 

                    r = np.hypot(x, y)
                    theta = np.arctan2(y, x)

                    sign = +1.0 if slip_angle < 0 else -1.0
                    r_signed = r * sign

                    b = np.digitize(theta, edges) - 1
                    if b < 0: b = 0
                    if b >= NBINS: b = NBINS-1

                    key = (f, b)
                    row = {
                        "Fz": f,
                        "slip_angle_deg": slip_angle,
                        "slip_ratio": slip_ratio,
                        "Fy": Fy,
                        "Fx": Fx,
                        "rMuyTyre": y,
                        "rMuxTyre": x,
                        "r_norm": r,
                        "r_signed": r_signed,
                        "theta": theta,
                        "bin": b,
                    }

                    if key not in best or r > best[key]["r_norm"]:
                        best[key] = row

        envelope_rows = list(best.values())
        env_df = pd.DataFrame(envelope_rows)
        env_df = env_df.sort_values(["Fz", "theta"]).reset_index(drop=True)

        return env_df
    
    @staticmethod
    def graph_slip(Fl_tyre, Rl_tyre, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_front_deg, camber_rear_deg, NBINS, file_name):
        df1 = Tyre.calc_pure_slip_angle(Fl_tyre, Rl_tyre, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_front_deg, camber_rear_deg)
        df2 = Tyre.calc_pure_slip_ratio(Fl_tyre, Rl_tyre, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_front_deg, camber_rear_deg)
        env_df_F = Tyre.tyre_elipse(Fl_tyre, NBINS, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_front_deg)
        env_df_R = Tyre.tyre_elipse(Rl_tyre, NBINS, slip_angle_range_rad, slip_ratio_range, Fz_range_n, camber_rear_deg)
        
        # --- Config ---
        y_cols_slip_angle = ["Fy_F", "rMuyTyreF", "Fy_R",  "rMuyTyreR"]
        y_cols_slip_ratio = ["Fx_F", "rMuxTyreF", "Fx_R",  "rMuxTyreR"]
        df_plot_slip_angle = df1.sort_values(["Fz", "slip_angle_deg"])
        df_plot_slip_ratio = df2.sort_values(["Fz", "slip_ratio"])
        # --------------------------
        # FIGURA COMBINADA
        # --------------------------

        fig = make_subplots(
            rows=4, cols=4,
            shared_yaxes=False,
            horizontal_spacing=0.075,
            vertical_spacing=0.1,
            row_heights=[0.25, 0.25, 0.25, 0.25],
            specs=[
                [{}, {}, {}, {}],
                [{}, {}, {}, {}],
                [{"colspan": 2}, None, {"colspan": 2}, None],
                [{"colspan": 2}, None, {"colspan": 2}, None]
            ],
            subplot_titles=(y_cols_slip_angle + y_cols_slip_ratio +
                ["Curvas Fy vs Slip angle por iso Fz Front",
                 "Curvas Fy vs Slip angle por iso Fz Rear"] +
                ["Curvas Fy vs Fx por iso Fz Front",
                 "Curvas Fy vs Fx por iso Fz Rear"]
            )
        )

        color = ["red", "green", "orange", "blue"]

        # --------------------------
        # FILA 1: slip angle
        # --------------------------
        for i, y_col in enumerate(y_cols_slip_angle, start=1):
            showlegend = (i == 1)
            color_index = 0
            for fz, g in df_plot_slip_angle.groupby("Fz", sort=True):
                fig.add_trace(
                    go.Scatter(
                        x=g["slip_angle_deg"],
                        y=g[y_col],
                        legendgroup=f"Fz_{fz}",
                        showlegend=showlegend,
                        line_color=color[color_index],
                        mode="lines",
                        name=f"Fz={fz:.0f} N",
                        text=[f"{fz:.0f}"] * len(g),
                    ),
                    row=1, col=i
                )
                color_index += 1

        # --------------------------
        # FILA 2: slip ratio
        # --------------------------
        for i, y_col in enumerate(y_cols_slip_ratio, start=1):
            color_index = 0
            for fz, g in df_plot_slip_ratio.groupby("Fz", sort=True):
                fig.add_trace(
                    go.Scatter(
                        x=g["slip_ratio"],
                        y=g[y_col],
                        legendgroup=f"Fz_{fz}",
                        showlegend=False,
                        mode="lines",
                        line_color=color[color_index],
                        name=f"Fz={fz:.0f} N",
                        hovertemplate=(
                            "Fz=%{text} N<br>"
                            "Slip=%{x:.2f}<br>"
                            "Fy=%{y:.0f} N"
                        ),
                        text=[f"{fz:.0f}"] * len(g),
                    ),
                    row=2, col=i
                )
                color_index += 1

        # --------------------------
        # FILA 3: curvas rMuxTyre vs rMuyTyre (Front / Rear)
        # --------------------------
        color_index = 0
        for fz, g in env_df_F.groupby("Fz"):
            fig.add_trace(
                go.Scatter(
                    x=-g["rMuxTyre"], y=g["rMuyTyre"],
                    mode="lines",
                    legendgroup=f"Fz_{fz}",
                    showlegend=False,  
                    line_color=color[color_index],
                    name=f"Fz={fz} N",
                ),
                row=3, col=1
            )
            color_index += 1

        color_index = 0
        for fz, g in env_df_R.groupby("Fz"):
            fig.add_trace(
                go.Scatter(
                    x=-g["rMuxTyre"], y=g["rMuyTyre"],
                    mode="lines",
                    legendgroup=f"Fz_{fz}",
                    showlegend=False,
                    line_color=color[color_index],
                    name=f"Fz={fz} N",
                ),
                row=3, col=3 
            )
            color_index += 1

        # --------------------------
        # FILA 4: curvas rMuxTyre vs rMuyTyre (Front / Rear)
        # --------------------------
        color_index = 0
        for fz, g in env_df_F.groupby("Fz"):
            fig.add_trace(
                go.Scatter(
                    x=-g["Fy"], y=g["Fx"],
                    mode="lines",
                    legendgroup=f"Fz_{fz}",
                    showlegend=False,  
                    line_color=color[color_index],
                    name=f"Fz={fz} N",
                ),
                row=4, col=1
            )
            color_index += 1

        color_index = 0
        for fz, g in env_df_R.groupby("Fz"):
            fig.add_trace(
                go.Scatter(
                    x=-g["Fy"], y=g["Fx"],
                    mode="lines",
                    legendgroup=f"Fz_{fz}",
                    showlegend=False,
                    line_color=color[color_index],
                    name=f"Fz={fz} N",
                ),
                row=4, col=3 
            )
            color_index += 1

        # --------------------------
        # TÍTULOS POR COLUMNA (anotaciones)
        # --------------------------
        row_titles = [
            "Curvas Fy vs Slip Angle por iso Fz",
            "Curvas Fy vs Slip Ratio por iso Fz",
            "Curvas rMuxTyre vs rMuyTyre (Front / Rear)",
            "Curvas Fy vs Fx (Front / Rear)"
        ]

        for r, title in enumerate(row_titles, start=1):
            fig.add_annotation(
                x=0.5,                      # centrado
                y=1.05 - (r-1)*0.285,        # separaciones verticales entre filas
                xref="paper",
                yref="paper",
                text=title,
                showarrow=False,
                font=dict(size=16, color="blue")
            )

        # --------------------------
        # LAYOUT GENERAL
        # --------------------------
        large_rockwell_template = dict(layout=go.Layout())
        fig.update_layout(
            legend_tracegroupgap=10,
            legend_groupclick='togglegroup',
            template=large_rockwell_template,
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor='rgba(255,255,255,0.6)',
                font_size=10,
                font_color="black"
            ),
            height=1600,
            legend_title="Cargas Fz",
            legend=dict(orientation="h",yanchor="bottom",y=1.015,xanchor="right",x=1)
        )
        fig.update_layout(title={"text": file_name,"y": 0.985,"x": 0.02,"xanchor": "left","yanchor": "bottom"})
        fig.update_xaxes(showspikes=True,spikecolor="black",spikesnap="data",spikemode="across",
                         spikethickness=1,spikedash='solid')

        # Títulos de ejes (ajusta a tu gusto)
        fig.update_xaxes(title_text="slip_angle_deg", row=1, range=[-0.3,0.3], dtick=0.1)
        fig.update_xaxes(title_text="slip_ratio", row=2, range=[-0.3,0.3], dtick=0.1)
        fig.update_xaxes(title_text="rMuxTyre (Front)", row=3, col=1, range=[-2.25,2.25], dtick=0.25)
        fig.update_xaxes(title_text="rMuxTyre (Rear)", row=3, col=3, range=[-2.25,2.25], dtick=0.25)
        fig.update_xaxes(title_text="Fy [kN]", row=4, col=1, range=[-15000,15000], dtick=2500)
        fig.update_xaxes(title_text="Fy [kN]", row=4, col=3, range=[-15000,15000], dtick=2500)

        fig.update_yaxes(title_text="Fy [N]", row=1, col=1, range=[-15000,15000], dtick=2500)
        fig.update_yaxes(row=1, col=2, range=[-2.25,2.25], dtick=0.25)
        fig.update_yaxes(row=1, col=3, range=[-15000,15000], dtick=2500)
        fig.update_yaxes(row=1, col=4, range=[-2.25,2.25], dtick=0.25)
        
        fig.update_yaxes(title_text="Fy [N]", row=2, col=1, range=[-15000,15000], dtick=2500)
        fig.update_yaxes(row=2, col=2, range=[-2.25,2.25], dtick=0.25)
        fig.update_yaxes(row=2, col=3, range=[-15000,15000], dtick=2500)
        fig.update_yaxes(row=2, col=4, range=[-2.25,2.25], dtick=0.25)
        fig.update_yaxes(title_text="rMuyTyreF", row=3, col=1, range=[-2.25,2.25], dtick=0.25)
        fig.update_yaxes(title_text="rMuyTyreR", row=3, col=3, range=[-2.25,2.25], dtick=0.25)
        fig.update_yaxes(title_text="Fx [kN]", row=4, col=1, range=[-15000,15000], dtick=2500)
        fig.update_yaxes(row=4, col=3, range=[-15000,15000], dtick=2500)

        return df1, df2, env_df_F, env_df_R, fig
    
    
    @classmethod
    def scan_parameter_graph_slip(
        cls,
        json_path: str,
        param_name: str,
        slips_angles,
        slips_ratios,
        Fz_range_n,
        camber_front_deg: float,
        camber_rear_deg: float,
        NBINS: int,
        side: str = "front",    # "front", "rear" o "both"
        n_points: int = 10,
        span_rel: float = 0.2,  # ±20% alrededor del valor base
        explicit_values=None,   # si quieres pasar tú mismo los valores a escanear
    ):

        # 1) Cargamos neumáticos base desde el JSON
        base_front, base_rear = cls.load_vehicle_tyres(json_path)

        # 2) Elegimos de qué neumático cogemos el valor base
        if side not in ("front", "rear", "both"):
            raise ValueError("side debe ser 'front', 'rear' o 'both'.")

        if side in ("front", "both"):
            base_tyre_for_value = base_front
        else:
            base_tyre_for_value = base_rear

        # 3) Comprobamos que el parámetro existe
        if not hasattr(base_tyre_for_value, param_name):
            raise AttributeError(f"El parámetro '{param_name}' no existe en Tyre.")

        base_value = getattr(base_tyre_for_value, param_name)

        # 4) Construimos la lista de valores a escanear
        if explicit_values is not None:
            values = list(explicit_values)
        else:
            # Escaneo relativo alrededor del valor base
            if abs(base_value) > 1e-12:
                factors = np.linspace(1.0 - span_rel, 1.0 + span_rel, n_points)
                values = base_value * factors
            else:
                # Si el valor base es ~0, escaneamos en términos absolutos
                delta = span_rel if span_rel > 0 else 1.0
                values = np.linspace(-delta, delta, n_points)

        results = []

        # 5) Loop sobre cada valor del parámetro
        for v in values:
            # Clonamos ambos neumáticos para no modificar los originales
            Fl_tyre = copy.deepcopy(base_front)
            Rl_tyre = copy.deepcopy(base_rear)

            # Aplicamos el parámetro según el lado
            if side in ("front", "both"):
                setattr(Fl_tyre, param_name, float(v))
            if side in ("rear", "both"):
                setattr(Rl_tyre, param_name, float(v))

            # 6) Llamamos a tu función original graph_slip
            df1, df2, env_df_F, env_df_R, fig = cls.graph_slip(
                Fl_tyre, Rl_tyre,
                slips_angles,
                slips_ratios,
                Fz_range_n,
                camber_front_deg,
                camber_rear_deg,
                NBINS, json_path+"_"+param_name+"_"+str(v)
            )

            # 8) Guardamos todo en la lista de resultados
            results.append({
                "param_value": float(v),
                "df1": df1,
                "df2": df2,
                "env_df_F": env_df_F,
                "env_df_R": env_df_R,
                "fig": fig,
            })

        return results


    

    
   


    
    