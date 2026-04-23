# formulas.py

import math
from dataclasses import dataclass
from typing import Iterable, Dict, Any

# -------------------------
# Dataclasses for params
# -------------------------

@dataclass
class LongitudinalParams:
    pCx1: float
    pDx1: float
    pDx2: float
    pDx3: float
    pEx1: float
    pEx2: float
    pEx3: float
    pEx4: float
    pKx1: float
    pKx2: float
    pKx3: float
    pHx1: float
    pHx2: float
    pVx1: float
    pVx2: float
    rBx1: float
    rBx2: float
    rCx1: float
    rEx1: float
    rEx2: float
    rHx1: float
    # bAllowLongitudinalTyreShifts: bool

@dataclass
class overtuningParams:
    qsx1: float
    qsx2: float
    qsx3: float

@dataclass
class LateralParams:
    pCy1: float
    pDy1: float
    pDy2: float
    pDy3: float
    pEy1: float
    pEy2: float
    pEy3: float
    pEy4: float
    pKy1: float
    pKy2: float
    pKy3: float
    pHy1: float
    pHy2: float
    pHy3: float
    pVy1: float
    pVy2: float
    pVy3: float
    pVy4: float
    rBy1: float
    rBy2: float
    rBy3: float
    rCy1: float
    rEy1: float
    rEy2: float
    rHy1: float
    rHy2: float
    rVy1: float
    rVy2: float
    rVy3: float
    rVy4: float
    rVy5: float
    rVy6: float



@dataclass
class AligningParams:
    qBz1: float
    qBz2: float
    qBz3: float
    qBz4: float
    qBz5: float
    qBz9: float
    qBz10: float
    qCz1: float
    qDz1: float
    qDz2: float
    qDz3: float
    qDz4: float
    qDz6: float
    qDz7: float
    qDz8: float
    qDz9: float
    qEz1: float
    qEz2: float
    qEz3: float
    qEz4: float
    qEz5: float
    qHz1: float
    qHz2: float
    qHz3: float
    qHz4: float
    sSz1: float
    sSz2: float
    sSz3: float
    sSz4: float

@dataclass
class ScalingParams:
    lambda_FZ0: float
    lambda_CX: float
    lambda_MUX: float
    lambda_EX: float
    lambda_KX: float
    lambda_HX: float
    lambda_VX: float
    lambda_GAX: float
    lambda_CY: float
    lambda_MUY: float
    lambda_EY: float
    lambda_KY: float
    lambda_HY: float
    lambda_VY: float
    lambda_GAY: float
    lambda_T: float
    lambda_Mr: float
    lambda_GAZ: float
    lambda_Mx: float
    lambda_vMx: float
    lambda_My: float
    lambda_XAL: float
    lambda_YKA: float
    lambda_VYKA: float
    lambda_s: float


# top level parameter container
@dataclass
class TyreParams:

    Fx: LongitudinalParams
    Fy: LateralParams
    Mz: AligningParams
    Overturning: overtuningParams
    Scale: ScalingParams
    Fz0: float
    R0: float

# operating states
@dataclass
class TyreState:
    kappa: float    # longitudinal slip
    alpha: float    # slip angle
    gamma: float    # camber angle
    Fz: float       # normal load
    Vx: float       # longitudinal speed


# -------------------------
# Build dataclass from dict
# -------------------------

def params_from_internal_dict(d: Dict[str, Any]) -> TyreParams:
    Fx = LongitudinalParams(**d["Fx"])
    Fy = LateralParams(**d["Fy"])
    Mz = AligningParams(**d["Mz"])
    Scale = ScalingParams(**d["Scale"])

    # Provide default overtuningParams if missing
    if "Overturning" in d and d["Overturning"] is not None:
        Overturning = overtuningParams(**d["Overturning"])
    else:
        Overturning = overtuningParams(qsx1=0.0, qsx2=0.0, qsx3=0.0)

    return TyreParams(
        Fx=Fx,
        Fy=Fy,
        Mz=Mz,
        Scale=Scale,
        Overturning=Overturning,
        Fz0=d["Fz0"],
        R0=d["R0"],
    )

# ------------------------
#  helpers
# -------------------------

def sgn(x: float) -> float:
    """Return sign of x: 1.0, -1.0, or 0.0."""
    if x > 0.0:
        return 1.0
    if x < 0.0:
        return -1.0
    return 0.0

# -------------------------
# Formulas
# -------------------------

def longitudinal_force(state: TyreState, p: LongitudinalParams, l: ScalingParams, Fz0: float):
        

        dfz = (state.Fz - Fz0) / Fz0

        # ------ Pure slip condition ------ #

        # set up longitudinal slip parameters

        SHx =  (p.pHx1 + p.pHx2 * dfz) * l.lambda_HX  # eq (26) - horizontal shift 

        SVx =  state.Fz * (p.pVx1 + p.pVx2 * dfz) * l.lambda_MUX * l.lambda_VX # eq (27) - vertical shift 

        kappa_x = state.kappa + SHx # eq (18) - state: longitudinal slip

        gamma_x = state.gamma * l.lambda_GAX # eq (19)

        mu_x = (p.pDx1 + p.pDx2 * dfz) * (1.0 - p.pDx3 * (gamma_x**2)) * l.lambda_MUX # eq (22)

        # Pacejka Coefficients

        Cx = p.pCx1 * l.lambda_CX # eq (20)

        Dx = mu_x * state.Fz # eq (20)

        Ex = (p.pEx1 + p.pEx2 * dfz + p.pEx3 * dfz * dfz) * (1.0 - p.pEx4 * sgn(kappa_x)) * l.lambda_EX # eq (23)

        Kx = state.Fz * (p.pKx1 + p.pKx2 * dfz) * (math.exp(p.pKx3 * dfz)) * l.lambda_KX # eq (24)
 
        Bx = Kx / (Cx * Dx) if Cx * Dx != 0.0 else 0.0 # eq (25)

        # Pure slip longitudinal force

        Fx0 = Dx * math.sin(
            Cx * math.atan(
                Bx * kappa_x - Ex * (Bx * kappa_x - math.atan(Bx * kappa_x))
            )
        ) + SVx

        # ------ combined slip condition ------ #

        SHxa = p.rHx1 # eq (63)

        alpha_s = state.alpha  + SHxa # eq (58)

        # Pacejka coefficients

        Bxa = p.rBx1 * math.cos(math.atan(p.rBx2 * state.kappa )) * l.lambda_XAL # eq (59)

        Cxa = p.rCx1 # eq (60)

        Exa = p.rEx1 + p.rEx2 * dfz # eq (62)

        Dxa = (Fx0) / (math.cos(
            Cxa * math.atan(
                Bxa * SHxa - Exa * (Bxa * SHxa - math.atan(Bxa* SHxa))))) # eq (61)

        # combined slip wieghting fucntuion Gxa
        Gxa_num = math.cos(Cxa * math.atan(Bxa * alpha_s - Exa * (Bxa * alpha_s - math.atan(Bxa * alpha_s))))
        Gxa_den = math.cos(Cxa * math.atan(Bxa * SHxa - Exa * (Bxa * SHxa - math.atan(Bxa * SHxa))))
        Gxa = Gxa_num / Gxa_den # eq (64)

        # ------ Calculate Fx ------ #

        Fx = Fx0 * Gxa # eq (56)
        # the combined slip can be claulted in two ways either by multiplying the pure slip by Gxa or using the full combined slip formula (eq 57)

        return Fx, Fx0 # returns pure and combined longitudinal force

def lateral_force(state: TyreState, p: LateralParams, l: ScalingParams, Fz0: float):
        
        dfz = (state.Fz - Fz0) / Fz0

        gamma_y = state.gamma * l.lambda_GAY # eq (31)

        # ------ Pure slip condition ------ #

        # set up longitudinal slip parameters

        SHy =  (p.pHy1 + p.pHy2 * dfz) * l.lambda_HY + p.pHy3 * gamma_y  # eq (38) - horizontal shift 

        SVy =  state.Fz * ((p.pVy1 + p.pVy2 * dfz) * l.lambda_VY + (p.pVy3 + p.pVy4 * dfz) * gamma_y ) * l.lambda_MUY # eq (39) - vertical shift 

        alpha_y = state.alpha + SHy # eq (30) - state: lateral slip

        mu_y = (p.pDy1 + p.pDy2 * dfz) * (1.0 - p.pDy3 * (gamma_y**2)) * l.lambda_MUY # eq (34)

        # Pacejka Coefficients

        Cy = p.pCy1 * l.lambda_CY # eq (32)

        Dy = mu_y * state.Fz # eq (33)
        
        Ey = (p.pEy1 + p.pEy2 * dfz) * (1.0 - (p.pEy3 + p.pEy4 * gamma_y) * sgn(alpha_y)) * l.lambda_EY # eq (35)

        Ky = (p.pKy1 * Fz0 * math.sin(
             2.0 * math.atan(
                  state.Fz/(p.pKy2 * Fz0 * l.lambda_FZ0)
                    )
                ) 
            * (1.0 - p.pKy3 * abs(gamma_y))
            * l.lambda_FZ0
            * l.lambda_KY
    )

        By = Ky / (Cy * Dy) if Cy * Dy != 0.0 else 0.0 # eq (37)

        # Pure slip longitudinal force

        Fy0 = Dy * math.sin(
            Cy * math.atan(
                By * alpha_y - Ey * (By * alpha_y - math.atan(By * alpha_y))
            )
        ) + SVy

        # ------ combined slip condition ------ #

        SHyk = p.rHy1 + p.rHy2 * dfz # eq (72)

        kappa_s = state.kappa  + SHyk # eq (67)

        # Pacejka coefficients

        Byk = p.rBy1 * math.cos(math.atan(p.rBy2 *(state.alpha - p.rBy3 ))) * l.lambda_YKA # eq (68)

        Cyk = p.rCy1 # eq (69)

        Eyk = p.rEy1 + p.rEy2 * dfz # eq (71)

        Dyk = ( (Fy0) /  # eq (70)
               (math.cos(
                     Cyk * math.atan(
                          Byk * SHyk - Eyk * (Byk * SHyk - math.atan(Byk * SHyk))
                        )
                    )
               )
            )
        
        DVyk = mu_y * state.Fz  * (p.rVy1 + p.rVy2 * dfz + p.rVy3 * state.gamma) * math.cos(math.atan(p.rVy4 * state.alpha)) # eq (74)
        
        SVyk = DVyk * math.sin(p.rVy5 * math.atan(p.rVy6 * state.kappa)) * l.lambda_VYKA # eq (73)

        # combined slip wieghting fucntuion Gxa
        Gyk_num = math.cos(Cyk * math.atan(Byk * kappa_s - Eyk * (Byk * kappa_s - math.atan(Byk * kappa_s))))
        Gyk_den = math.cos(Cyk * math.atan(Byk * SHyk - Eyk * (Byk * SHyk - math.atan(Byk * SHyk))))
        Gyk = Gyk_num / Gyk_den # eq (75)

        # ------ Calculate Fx ------ #

        Fy = Fy0 * Gyk + SVyk # eq (65)

        return Fy, Fy0 # returns pure and combined longitudinal force

def overtuning_moment(state: TyreState, p: AligningParams, l: ScalingParams, o: overtuningParams, Fz0: float, R0: float, VRef: float, params: TyreParams):

    Fy, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)

    Mx = R0 * state.Fz (o.qsx1 * l.lambda_vMx + (- o.qsx2 * state.gamma + o.qsx3 * (Fy / Fz0))) 

    return Mx

def rolling_resistance_moment(state: TyreState, p: AligningParams, l: ScalingParams, Fz0: float, R0: float, VRef: float, params: TyreParams):
    
    Fx, _ = longitudinal_force(state, params.Fx, params.Scale, params.Fz0)

    My = R0 * state.Fz (p.qsy1 * p.qsy2 * (Fx/Fz0) + p.qsy3 * math.abs(state.Vx/VRef) + p.qsy4 * (state.Vx/VRef)**4)

    return My

def self_alligning_moment(state: TyreState, p: AligningParams, m: LateralParams,l: ScalingParams, Fy0: float, Fz0: float, R0: float):

    
    #  ----------- Pure slip condition -----------

    dfz = (state.Fz - Fz0) / Fz0

    gamma_z = state.gamma * l.lambda_GAZ # eq (47)
    gamma_y = state.gamma *l.lambda_GAY

    SHt = p.qHz1 + p.qHz2 * dfz + (p.qHz3 + p.qHz4 * dfz) * gamma_z # eq (52)

    # Pbuematic Trail

    Ct = p.qCz1 # eq (49)

    Dt = state.Fz * (p.qDz1 + p.qDz2 * dfz) * (1.0 + p.qDz3 * gamma_z + p.qDz4 * gamma_z * gamma_z) * (R0 / Fz0) * l.lambda_T # eq(52)

    Bt = (p.qBz1 + p.qBz2 * dfz + p.qBz3 * dfz * dfz) * (1.0 + p.qBz4 * gamma_z + p.qBz5 * abs(gamma_z)) * (l.lambda_KY / l.lambda_MUY) # eq (48)

    alpha_t = state.alpha + SHt # eq (43)

    Et =(p.qEz1 + p.qEz2 * dfz + p.qEz3 * dfz * dfz) * (        # eq (51)
         1.0 + (p.qEz4 + p.qEz5 * gamma_z) * (2.0 / math.pi) * math.atan(
        Bt * Ct * alpha_t
            )
        )

    t = Dt * math.cos(
        Ct
        * math.atan(
            Bt * alpha_t - Et * (Bt * alpha_t - math.atan(alpha_t))
        )
    ) * math.cos(state.alpha)

    # Residual Torque

    Dr = (state.Fz * 
            ((p.qDz6 + p.qDz7 * dfz) * l.lambda_Mr + (p.qDz8 + p.qDz9 * dfz) * gamma_z)
            * R0
            * l.lambda_MUY
    ) # eq (54)

    SHy =  (m.pHy1 + m.pHy2 * dfz) * l.lambda_HY + m.pHy3 * gamma_y

    SVy =  state.Fz * ((m.pVy1 + m.pVy2 * dfz) * l.lambda_VY + (m.pVy3 + m.pVy4 * dfz) * gamma_y ) * l.lambda_MUY

    Ky = (m.pKy1 * Fz0 * math.sin(
             2.0 * math.atan(
                  state.Fz/(m.pKy2 * Fz0 * l.lambda_FZ0)
                    )
                ) 
            * (1.0 - m.pKy3 * abs(gamma_y))
            * l.lambda_FZ0
            * l.lambda_KY
    )     

    SHf = SHy + (SVy / Ky)

    alpha_r = state.alpha + SHf # eq (45)


    Cy = m.pCy1 * l.lambda_CY # eq (32)
    
    mu_y = (m.pDy1 + m.pDy2 * dfz) * (1.0 - m.pDy3 * (gamma_y**2)) * l.lambda_MUY # eq (34)

    Dy = mu_y * state.Fz # eq (33)
    

    Ky = (m.pKy1 * Fz0 * math.sin(
             2.0 * math.atan(
                  state.Fz/(m.pKy2 * Fz0 * l.lambda_FZ0)
                    )
                ) 
            * (1.0 - m.pKy3 * abs(gamma_y))
            * l.lambda_FZ0
            * l.lambda_KY
    )

    By = Ky / (Cy * Dy) if Cy * Dy != 0.0 else 0.0 # eq (37)
    
    Br = p.qBz9 * (l.lambda_KY / l.lambda_MUY) + p.qBz10 * By * Cy

    Mzr = Dr * math.cos(math.atan(Br * alpha_r)) * math.cos(state.alpha) # eq (44)


    Mz0 = - t * Fy0 + Mzr # eq (41)


    return Mz0, t





