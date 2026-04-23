
import plotly.graph_objects as go
import numpy as np
import math
from formulas import TyreParams, TyreState, lateral_force, self_alligning_moment, longitudinal_force

# -------------------------
# Plotting functions
# -------------------------

def add_original_trace(fig: go.Figure, params_orig: TyreParams, plot_type: str, Fz: float, gamma_deg: float, 
                       alpha_range_deg: np.ndarray = None, kappa_range: np.ndarray = None, 
                       alpha_deg: float = 0, gamma_range_deg: np.ndarray = None) -> go.Figure:
    """Helper function to add original parameter overlay to any plot."""
    
    if plot_type == "mz_vs_slip_angle":
        mz_values_orig = []
        for alpha in alpha_range_deg:
            state = TyreState(kappa=0.0, alpha=math.radians(alpha), gamma=math.radians(gamma_deg), Fz=Fz, Vx=30.0)
            fy0, _ = lateral_force(state, params_orig.Fy, params_orig.Scale, params_orig.Fz0)
            mz0, _ = self_alligning_moment(state, params_orig.Mz, params_orig.Fy, params_orig.Scale, fy0, params_orig.Fz0, params_orig.R0)
            mz_values_orig.append(mz0)
        fig.add_trace(go.Scatter(x=alpha_range_deg, y=mz_values_orig, mode='lines', name='Mz (Original)', 
                                 line=dict(color='gray', width=2, dash='dash')))
    
    elif plot_type == "pneumatic_trail":
        trail_values_orig = []
        for alpha in alpha_range_deg:
            state = TyreState(kappa=0.0, alpha=math.radians(alpha), gamma=math.radians(gamma_deg), Fz=Fz, Vx=30.0)
            fy0, _ = lateral_force(state, params_orig.Fy, params_orig.Scale, params_orig.Fz0)
            _, t = self_alligning_moment(state, params_orig.Mz, params_orig.Fy, params_orig.Scale, fy0, params_orig.Fz0, params_orig.R0)
            trail_values_orig.append(t)
        fig.add_trace(go.Scatter(x=alpha_range_deg, y=trail_values_orig, mode='lines', name='Pneumatic Trail (Original)',
                                 line=dict(color='gray', width=2, dash='dash')))
    
    elif plot_type == "fy_vs_slip_angle":
        fy_values_orig = []
        for alpha in alpha_range_deg:
            state = TyreState(kappa=0.0, alpha=math.radians(alpha), gamma=math.radians(gamma_deg), Fz=Fz, Vx=30.0)
            fy0, _ = lateral_force(state, params_orig.Fy, params_orig.Scale, params_orig.Fz0)
            fy_values_orig.append(fy0)
        fig.add_trace(go.Scatter(x=alpha_range_deg, y=fy_values_orig, mode='lines', name='Fy (Original)',
                                 line=dict(color='gray', width=2, dash='dash')))
    
    elif plot_type == "fx_vs_longitudinal_slip":
        fx_values_orig = []
        for kappa in kappa_range:
            state = TyreState(kappa=kappa, alpha=math.radians(alpha_deg), gamma=math.radians(gamma_deg), Fz=Fz, Vx=30.0)
            fx0, _ = longitudinal_force(state, params_orig.Fx, params_orig.Scale, params_orig.Fz0)
            fx_values_orig.append(fx0)
        fig.add_trace(go.Scatter(x=kappa_range, y=fx_values_orig, mode='lines', name='Fx (Original)',
                                 line=dict(color='gray', width=2, dash='dash')))
    
    elif plot_type == "mz_vs_camber":
        mz_values_orig = []
        for gamma in gamma_range_deg:
            state = TyreState(kappa=0.0, alpha=math.radians(alpha_deg), gamma=math.radians(gamma), Fz=Fz, Vx=30.0)
            fy0, _ = lateral_force(state, params_orig.Fy, params_orig.Scale, params_orig.Fz0)
            mz0, _ = self_alligning_moment(state, params_orig.Mz, params_orig.Fy, params_orig.Scale, fy0, params_orig.Fz0, params_orig.R0)
            mz_values_orig.append(mz0)
        fig.add_trace(go.Scatter(x=gamma_range_deg, y=mz_values_orig, mode='lines', name='Mz (Original)',
                                 line=dict(color='gray', width=2, dash='dash')))
    
    elif plot_type == "fy_vs_camber":
        fy_values_orig = []
        for gamma in gamma_range_deg:
            state = TyreState(kappa=0.0, alpha=math.radians(alpha_deg), gamma=math.radians(gamma), Fz=Fz, Vx=30.0)
            fy0, _ = lateral_force(state, params_orig.Fy, params_orig.Scale, params_orig.Fz0)
            fy_values_orig.append(fy0)
        fig.add_trace(go.Scatter(x=gamma_range_deg, y=fy_values_orig, mode='lines', name='Fy (Original)',
                                 line=dict(color='gray', width=2, dash='dash')))
    
    return fig

def plot_mz_vs_slip_angle(params: TyreParams, Fz: float, gamma_deg: float, alpha_range_deg: np.ndarray, params_orig: TyreParams = None) -> go.Figure:
    """Plot self-aligning moment vs slip angle at fixed camber angle."""
    mz_values = []
    
    for alpha_deg in alpha_range_deg:
        # Create TyreState with the slip angle sweep
        state = TyreState(
            kappa=0.0,
            alpha=math.radians(alpha_deg),
            gamma=math.radians(gamma_deg),
            Fz=Fz,
            Vx=30.0
        )
        
        # First, calculate Fy0 (needed for self_aligning_moment)
        fy0, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
        
        # Calculate self-aligning moment (returns Mz0, t)
        mz0, _ = self_alligning_moment(state, params.Mz, params.Fy, params.Scale, fy0, params.Fz0, params.R0)
        mz_values.append(mz0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=alpha_range_deg,
        y=mz_values,
        mode='lines',
        name='Mz',
        line=dict(color='red', width=2)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add original parameter overlay if provided
    if params_orig is not None:
        fig = add_original_trace(fig, params_orig, "mz_vs_slip_angle", Fz, gamma_deg, alpha_range_deg)
    
    fig.update_layout(
        title=f'Self-Aligning Moment vs Slip Angle (γ = {gamma_deg}°)',
        xaxis_title='Slip Angle α [deg]',
        yaxis_title='Self-Aligning Moment Mz [N⋅m]',
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_mz_vs_camber(params: TyreParams, Fz: float, alpha_deg: float, gamma_range_deg: np.ndarray, params_orig: TyreParams = None) -> go.Figure:
    """Plot self-aligning moment vs camber angle at fixed slip angle."""
    mz_values = []
    
    for gamma_deg in gamma_range_deg:
        # Create TyreState with the camber angle sweep
        state = TyreState(
            kappa=0.0,
            alpha=math.radians(alpha_deg),
            gamma=math.radians(gamma_deg),
            Fz=Fz,
            Vx=30.0
        )
        
        # First, calculate Fy0 (needed for self_aligning_moment)
        fy0, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
        
        # Calculate self-aligning moment (returns Mz0, t)
        mz0, _ = self_alligning_moment(state, params.Mz, params.Fy, params.Scale, fy0, params.Fz0, params.R0)
        mz_values.append(mz0)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=gamma_range_deg,
        y=mz_values,
        mode='lines',
        name='Mz',
        line=dict(color='darkred', width=2)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add original parameter overlay if provided
    if params_orig is not None:
        fig = add_original_trace(fig, params_orig, "mz_vs_camber", Fz, alpha_deg, gamma_range_deg=gamma_range_deg)
    
    fig.update_layout(
        title=f'Self-Aligning Moment vs Camber Angle (α = {alpha_deg}°)',
        xaxis_title='Camber Angle γ [deg]',
        yaxis_title='Self-Aligning Moment Mz [N⋅m]',
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_pneumatic_trail_vs_slip(params: TyreParams, Fz: float, gamma_deg: float, alpha_range_deg: np.ndarray, params_orig: TyreParams = None) -> go.Figure:
    """Plot pneumatic trail vs slip angle at fixed camber angle.
    
    Pneumatic trail is extracted directly from self_aligning_moment function.
    """
    trail_values = []
    
    for alpha_deg in alpha_range_deg:
        # Create TyreState with the slip angle sweep
        state = TyreState(
            kappa=0.0,
            alpha=math.radians(alpha_deg),
            gamma=math.radians(gamma_deg),
            Fz=Fz,
            Vx=30.0
        )
        
        # Calculate Fy0 (needed for self_aligning_moment)
        fy0, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
        
        # Get pneumatic trail from self_aligning_moment return value
        _, t = self_alligning_moment(state, params.Mz, params.Fy, params.Scale, fy0, params.Fz0, params.R0)
        trail_values.append(t)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=alpha_range_deg,
        y=trail_values,
        mode='lines',
        name='Pneumatic Trail',
        line=dict(color='green', width=2)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add original parameter overlay if provided
    if params_orig is not None:
        fig = add_original_trace(fig, params_orig, "pneumatic_trail", Fz, gamma_deg, alpha_range_deg)
    
    fig.update_layout(
        title=f'Pneumatic Trail vs Slip Angle (γ = {gamma_deg}°)',
        xaxis_title='Slip Angle α [deg]',
        yaxis_title='Pneumatic Trail t [m]',
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_fy_vs_slip_angle(params: TyreParams, Fz: float, gamma_deg: float, alpha_range_deg: np.ndarray, params_orig: TyreParams = None) -> go.Figure:
    """Plot lateral force vs slip angle at fixed camber angle."""
    fy_values = []
    
    for alpha_deg in alpha_range_deg:
        # Create TyreState with the slip angle sweep
        state = TyreState(
            kappa=0.0,
            alpha=math.radians(alpha_deg),
            gamma=math.radians(gamma_deg),
            Fz=Fz,
            Vx=30.0
        )
        
        # Calculate lateral force
        fy, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
        fy_values.append(fy)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=alpha_range_deg,
        y=fy_values,
        mode='lines',
        name='Fy',
        line=dict(color='purple', width=2)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add original parameter overlay if provided
    if params_orig is not None:
        fig = add_original_trace(fig, params_orig, "fy_vs_slip_angle", Fz, gamma_deg, alpha_range_deg)
    
    fig.update_layout(
        title=f'Lateral Force vs Slip Angle (γ = {gamma_deg}°)',
        xaxis_title='Slip Angle α [deg]',
        yaxis_title='Lateral Force Fy [N]',
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_fy_vs_camber(params: TyreParams, Fz: float, alpha_deg: float, gamma_range_deg: np.ndarray, params_orig: TyreParams = None) -> go.Figure:
    """Plot lateral force vs camber angle at fixed slip angle."""
    fy_values = []
    
    for gamma_deg in gamma_range_deg:
        # Create TyreState with the camber angle sweep
        state = TyreState(
            kappa=0.0,
            alpha=math.radians(alpha_deg),
            gamma=math.radians(gamma_deg),
            Fz=Fz,
            Vx=30.0
        )
        
        # Calculate lateral force
        fy, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
        fy_values.append(fy)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=gamma_range_deg,
        y=fy_values,
        mode='lines',
        name='Fy',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add original parameter overlay if provided
    if params_orig is not None:
        fig = add_original_trace(fig, params_orig, "fy_vs_camber", Fz, alpha_deg, gamma_range_deg=gamma_range_deg)
    
    fig.update_layout(
        title=f'Lateral Force vs Camber Angle (α = {alpha_deg}°)',
        xaxis_title='Camber Angle γ [deg]',
        yaxis_title='Lateral Force Fy [N]',
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_fx_vs_longitudinal_slip(params: TyreParams, Fz: float, kappa_range: np.ndarray, alpha_deg: float, gamma_deg: float, params_orig: TyreParams = None) -> go.Figure:
    """Plot longitudinal force vs longitudinal slip at zero slip angle."""
    fx_values = []
    
    for kappa in kappa_range:
        # Create TyreState with the longitudinal slip sweep
        state = TyreState(
            kappa=kappa,
            alpha=math.radians(alpha_deg),
            gamma=math.radians(gamma_deg),
            Fz=Fz,
            Vx=30.0
        )
        
        # Calculate longitudinal force
        fx, _ = longitudinal_force(state, params.Fx, params.Scale, params.Fz0)
        fx_values.append(fx)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=kappa_range,
        y=fx_values,
        mode='lines',
        name='Fx',
        line=dict(color='brown', width=2)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
    
    # Add original parameter overlay if provided
    if params_orig is not None:
        fig = add_original_trace(fig, params_orig, "fx_vs_longitudinal_slip", Fz, gamma_deg, 
                                 alpha_range_deg=None, kappa_range=kappa_range, alpha_deg=alpha_deg)
    
    fig.update_layout(
        title=f'Longitudinal Force vs Longitudinal Slip (α = {alpha_deg}°, γ = {gamma_deg}°)',
        xaxis_title='Longitudinal Slip κ',
        yaxis_title='Longitudinal Force Fx [N]',
        hovermode='x unified',
        height=400
    )
    
    return fig

def plot_mz_multi_camber(params: TyreParams, Fz: float, alpha_range_deg: np.ndarray, camber_values: list) -> go.Figure:
    """Plot self-aligning moment vs slip angle for multiple camber angles."""
    fig = go.Figure()
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    
    for gamma_deg, color in zip(camber_values, colors):
        mz_values = []
        for alpha_deg in alpha_range_deg:
            state = TyreState(
                kappa=0.0,
                alpha=math.radians(alpha_deg),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            fy0, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
            mz0, _ = self_alligning_moment(state, params.Mz, params.Fy, params.Scale, fy0, params.Fz0, params.R0)
            mz_values.append(mz0)
        
        fig.add_trace(go.Scatter(
            x=alpha_range_deg,
            y=mz_values,
            mode='lines',
            name=f'γ = {gamma_deg}°',
            line=dict(color=color, width=2)
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.update_layout(
        title='Mz vs Slip Angle (Multiple Cambers)',
        xaxis_title='Slip Angle α [deg]',
        yaxis_title='Self-Aligning Moment Mz [N⋅m]',
        hovermode='x unified',
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    
    return fig

def plot_fy_multi_camber(params: TyreParams, Fz: float, alpha_range_deg: np.ndarray, camber_values: list) -> go.Figure:
    """Plot lateral force vs slip angle for multiple camber angles."""
    fig = go.Figure()
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    
    for gamma_deg, color in zip(camber_values, colors):
        fy_values = []
        for alpha_deg in alpha_range_deg:
            state = TyreState(
                kappa=0.0,
                alpha=math.radians(alpha_deg),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            Fy, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
            fy_values.append(Fy)
        
        fig.add_trace(go.Scatter(
            x=alpha_range_deg,
            y=fy_values,
            mode='lines',
            name=f'γ = {gamma_deg}°',
            line=dict(color=color, width=2)
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.update_layout(
        title='Fy vs Slip Angle (Multiple Cambers)',
        xaxis_title='Slip Angle α [deg]',
        yaxis_title='Lateral Force Fy [N]',
        hovermode='x unified',
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    
    return fig

def plot_fy_multi_force_pure_slip(params: TyreParams, alpha_range_deg: np.ndarray, 
                                   gamma_deg: float, fz_values: list) -> go.Figure:
    """Plot lateral force vs slip angle (pure slip: κ=0) for multiple vertical loads.
    
    Shows how Fy varies with slip angle at different Fz values.
    """
    fig = go.Figure()
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown', 'pink']
    
    for Fz, color in zip(fz_values, colors):
        fy_values = []
        
        for alpha_deg in alpha_range_deg:
            state = TyreState(
                kappa=0.0,  # Pure slip condition
                alpha=math.radians(alpha_deg),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            
            # Calculate lateral force
            _, Fy0 = lateral_force(state, params.Fy, params.Scale, params.Fz0)
            fy_values.append(Fy0)
        
        fig.add_trace(go.Scatter(
            x=alpha_range_deg,
            y=fy_values,
            mode='lines',
            name=f'Fz = {Fz:.0f} N',
            line=dict(color=color, width=2)
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.update_layout(
        title=f'Lateral Force vs Slip Angle - Pure Slip (γ = {gamma_deg}°)',
        xaxis_title='Slip Angle α [deg]',
        yaxis_title='Lateral Force Fy [N]',
        hovermode='x unified',
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    
    return fig

def plot_fx_multi_force_pure_slip(params: TyreParams, kappa_range: np.ndarray,
                                   alpha_deg: float, fz_values: list) -> go.Figure:
    """Plot longitudinal force vs longitudinal slip (pure slip: α=0) for multiple vertical loads.
    
    Shows how Fx varies with longitudinal slip at different Fz values.
    Demonstrates load sensitivity of the longitudinal force curve.
    """
    fig = go.Figure()
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown', 'pink']
    
    for Fz, color in zip(fz_values, colors):
        fx_values = []
        
        for kappa in kappa_range:
            state = TyreState(
                kappa=kappa,
                alpha=math.radians(alpha_deg),
                gamma=0.0,
                Fz=Fz,
                Vx=30.0
            )
            
            # Calculate longitudinal force
            fx, _ = longitudinal_force(state, params.Fx, params.Scale, params.Fz0)
            fx_values.append(fx)
        
        fig.add_trace(go.Scatter(
            x=kappa_range,
            y=fx_values,
            mode='lines',
            name=f'Fz = {Fz:.0f} N',
            line=dict(color=color, width=2)
        ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)
    fig.update_layout(
        title=f'Longitudinal Force vs Longitudinal Slip - Load Sensitivity (α = {alpha_deg}°)',
        xaxis_title='Longitudinal Slip κ',
        yaxis_title='Longitudinal Force Fx [N]',
        hovermode='x unified',
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    
    return fig

def plot_combined_slip_ellipse(params: TyreParams, Fz: float, gamma_deg: float, 
                               alpha_range_deg: np.ndarray, kappa_range: np.ndarray) -> go.Figure:
    """Plot combined-slip ellipse envelope: Fy vs Fx for all combinations of κ and α.
    
    For each combination of longitudinal slip (κ) and slip angle (α),
    computes Fx and Fy, creating an envelope of tire grip capability.
    """
    fig = go.Figure()
    
    # Create a grid of κ and α values to generate the envelope
    fx_envelope = []
    fy_envelope = []
    
    # For each alpha value, sweep through kappa to create a slice of the ellipse
    for alpha_deg in alpha_range_deg:
        fx_slice = []
        fy_slice = []
        
        for kappa in kappa_range:
            state = TyreState(
                kappa=kappa,
                alpha=math.radians(alpha_deg),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            
            # Calculate both Fx and Fy
            fx, _ = longitudinal_force(state, params.Fx, params.Scale, params.Fz0)
            fy, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
            
            fx_slice.append(fx)
            fy_slice.append(fy)
        
        # Add trace for this slip angle
        fig.add_trace(go.Scatter(
            x=fx_slice,
            y=fy_slice,
            mode='lines+markers',
            name=f'α = {alpha_deg:.1f}°',
            line=dict(width=1.5),
            marker=dict(size=3),
            opacity=0.7
        ))
    
    # Add zero reference lines
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3)
    fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.3)
    
    fig.update_layout(
        title=f'Combined-Slip Ellipse Envelope (γ = {gamma_deg}°, Fz = {Fz:.0f} N)',
        xaxis_title='Longitudinal Force Fx [N]',
        yaxis_title='Lateral Force Fy [N]',
        hovermode='closest',
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        xaxis=dict(zeroline=True),
        yaxis=dict(zeroline=True)
    )
    
    return fig

def plot_fx_surface(params: TyreParams, Fz: float, gamma_deg: float,
                    alpha_range_deg: np.ndarray, kappa_range: np.ndarray) -> go.Figure:
    """Plot 3D surface of Fx as a function of slip angle (α) and longitudinal slip (κ).
    
    Creates a surface showing how longitudinal force varies across the combined
    slip parameter space.
    """
    # Create mesh grid for α and κ
    alpha_mesh = np.linspace(alpha_range_deg[0], alpha_range_deg[-1], 40)
    kappa_mesh = np.linspace(kappa_range[0], kappa_range[-1], 40)
    alpha_mesh, kappa_mesh = np.meshgrid(alpha_mesh, kappa_mesh)
    
    # Calculate Fx for each (κ, α) combination
    fx_surface = np.zeros_like(alpha_mesh)
    
    for i in range(alpha_mesh.shape[0]):
        for j in range(alpha_mesh.shape[1]):
            state = TyreState(
                kappa=kappa_mesh[i, j],
                alpha=math.radians(alpha_mesh[i, j]),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            
            fx, _ = longitudinal_force(state, params.Fx, params.Scale, params.Fz0)
            fx_surface[i, j] = fx
    
    fig = go.Figure(data=[go.Surface(
        x=alpha_mesh,
        y=kappa_mesh,
        z=fx_surface,
        colorscale='Viridis',
        colorbar=dict(title="Fx [N]"),
        name='Fx'
    )])
    
    fig.update_layout(
        title=f'Longitudinal Force Surface Fx(α, κ) (γ = {gamma_deg}°, Fz = {Fz:.0f} N)',
        scene=dict(
            xaxis_title='Slip Angle α [deg]',
            yaxis_title='Longitudinal Slip κ',
            zaxis_title='Longitudinal Force Fx [N]',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=750,
        width=1000
    )
    
    return fig


def plot_fy_surface(params: TyreParams, Fz: float, gamma_deg: float,
                    alpha_range_deg: np.ndarray, kappa_range: np.ndarray) -> go.Figure:
    """Plot 3D surface of Fy as a function of slip angle (α) and longitudinal slip (κ).
    
    Creates a surface showing how lateral force varies across the combined
    slip parameter space.
    """
    # Create mesh grid for α and κ
    alpha_mesh = np.linspace(alpha_range_deg[0], alpha_range_deg[-1], 40)
    kappa_mesh = np.linspace(kappa_range[0], kappa_range[-1], 40)
    alpha_mesh, kappa_mesh = np.meshgrid(alpha_mesh, kappa_mesh)
    
    # Calculate Fy for each (κ, α) combination
    fy_surface = np.zeros_like(alpha_mesh)
    
    for i in range(alpha_mesh.shape[0]):
        for j in range(alpha_mesh.shape[1]):
            state = TyreState(
                kappa=kappa_mesh[i, j],
                alpha=math.radians(alpha_mesh[i, j]),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            
            fy, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
            fy_surface[i, j] = fy
    
    fig = go.Figure(data=[go.Surface(
        x=alpha_mesh,
        y=kappa_mesh,
        z=fy_surface,
        colorscale='Plasma',
        colorbar=dict(title="Fy [N]"),
        name='Fy'
    )])
    
    fig.update_layout(
        title=f'Lateral Force Surface Fy(α, κ) (γ = {gamma_deg}°, Fz = {Fz:.0f} N)',
        scene=dict(
            xaxis_title='Slip Angle α [deg]',
            yaxis_title='Longitudinal Slip κ',
            zaxis_title='Lateral Force Fy [N]',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=750,
        width=1000
    )
    
    return fig

def plot_mz_surface(params: TyreParams, Fz: float, gamma_deg: float,
                    alpha_range_deg: np.ndarray, kappa_range: np.ndarray) -> go.Figure:
    """Plot 3D surface of Mz as a function of slip angle (α) and longitudinal slip (κ).
    
    Shows how self-aligning moment (aligning torque) collapses under large slip,
    demonstrating the loss of steering feedback at high longitudinal slip.
    """
    # Create mesh grid for α and κ
    alpha_mesh = np.linspace(alpha_range_deg[0], alpha_range_deg[-1], 40)
    kappa_mesh = np.linspace(kappa_range[0], kappa_range[-1], 40)
    alpha_mesh, kappa_mesh = np.meshgrid(alpha_mesh, kappa_mesh)
    
    # Calculate Mz for each (κ, α) combination
    mz_surface = np.zeros_like(alpha_mesh)
    
    for i in range(alpha_mesh.shape[0]):
        for j in range(alpha_mesh.shape[1]):
            state = TyreState(
                kappa=kappa_mesh[i, j],
                alpha=math.radians(alpha_mesh[i, j]),
                gamma=math.radians(gamma_deg),
                Fz=Fz,
                Vx=30.0
            )
            
            # Calculate Fy first (needed for self_aligning_moment)
            fy0, _ = lateral_force(state, params.Fy, params.Scale, params.Fz0)
            
            # Calculate self-aligning moment
            mz0, _ = self_alligning_moment(state, params.Mz, params.Fy, params.Scale, fy0, params.Fz0, params.R0)
            mz_surface[i, j] = mz0
    
    fig = go.Figure(data=[go.Surface(
        x=alpha_mesh,
        y=kappa_mesh,
        z=mz_surface,
        colorscale='RdBu',
        colorbar=dict(title="Mz [N⋅m]"),
        name='Mz'
    )])
    
    fig.update_layout(
        title=f'Self-Aligning Moment Surface Mz(α, κ) (γ = {gamma_deg}°, Fz = {Fz:.0f} N)',
        scene=dict(
            xaxis_title='Slip Angle α [deg]',
            yaxis_title='Longitudinal Slip κ',
            zaxis_title='Self-Aligning Moment Mz [N⋅m]',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=750,
        width=1000
    )
    
    return fig
