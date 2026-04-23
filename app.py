# app.py
# streamlit run app.py 
import sys
import os
import json
import numpy as np
from dataclasses import asdict

import streamlit as st
import plotly.graph_objects as go
from plotting_functions import plot_fx_vs_longitudinal_slip, plot_fy_vs_slip_angle, plot_mz_vs_slip_angle
import math

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alias_min import *
from formulas import *
from formula_dependencies import get_parameter_info, ALL_FORMULAS

# Parameter name mapping - convert dataclass names to parameter codes
def get_parameter_code(field_name: str) -> str:
    """Convert dataclass field name to parameter code (e.g., pCx1 -> PCX1)."""
    # Try each alias mapping
    if field_name in LONGITUDINAL_ALIASES:
        return LONGITUDINAL_ALIASES[field_name]
    elif field_name in LATERAL_ALIASES:
        return LATERAL_ALIASES[field_name]
    elif field_name in ALIGNING_ALIASES:
        return ALIGNING_ALIASES[field_name]
    elif field_name in SCALING_ALIASES:
        return SCALING_ALIASES[field_name]
    elif field_name in OVERTURNING_COEFFICIENTS:
        return OVERTURNING_COEFFICIENTS[field_name]
    else:
        # Fallback: return as-is if not found
        return field_name

# Parameter descriptions and units - using JSON parameter names
PARAMETER_INFO = {
    # Longitudinal Parameters (Fx)
    "PCX1": "Shape factor for longitudinal friction curve",
    "PDX1": "Peak longitudinal friction coefficient - load dependency",
    "PDX2": "Peak longitudinal friction coefficient - camber dependency", 
    "PDX3": "Peak longitudinal friction coefficient - speed dependency",
    "PEX1": "Longitudinal friction curve shape curvature - load dependency",
    "PEX2": "Longitudinal friction curve shape curvature - speed dependency",
    "PEX3": "Additional longitudinal friction curve shape curvature",
    "PEX4": "Additional longitudinal friction curve shape curvature parameter",
    "PKX1": "Longitudinal slip stiffness at reference load",
    "PKX2": "Longitudinal slip stiffness - load dependency",
    "PKX3": "Longitudinal slip stiffness - friction coefficient dependency",
    "PHX1": "Horizontal shift for longitudinal friction curve",
    "PHX2": "Horizontal shift for longitudinal friction curve - speed dependency",
    "PVX1": "Vertical shift for longitudinal friction curve",
    "PVX2": "Vertical shift for longitudinal friction curve - speed dependency",
    "RBX1": "Longitudinal friction curve break point - load dependency",
    "RBX2": "Longitudinal friction curve break point - speed dependency",
    "RCX1": "Longitudinal friction curve break point - shape factor",
    "REX1": "Longitudinal friction curve break point - load dependency",
    "REX2": "Longitudinal friction curve break point - speed dependency",
    "RHX1": "Horizontal shift for longitudinal friction curve break point",
    
    # Lateral Parameters (Fy)
    "PCY1": "Shape factor for lateral friction curve",
    "PDY1": "Peak lateral friction coefficient - load dependency",
    "PDY2": "Peak lateral friction coefficient - camber dependency",
    "PDY3": "Peak lateral friction coefficient - speed dependency",
    "PEY1": "Lateral friction curve shape curvature - load dependency",
    "PEY2": "Lateral friction curve shape curvature - speed dependency",
    "PEY3": "Additional lateral friction curve shape curvature",
    "PEY4": "Additional lateral friction curve shape curvature parameter",
    "PKY1": "Cornering stiffness at reference load",
    "PKY2": "Cornering stiffness - load dependency",
    "PKY3": "Cornering stiffness - friction coefficient dependency",
    "PHY1": "Horizontal shift for lateral friction curve",
    "PHY2": "Horizontal shift for lateral friction curve - speed dependency",
    "PHY3": "Additional horizontal shift for lateral friction curve",
    "PVY1": "Vertical shift for lateral friction curve",
    "PVY2": "Vertical shift for lateral friction curve - speed dependency",
    "PVY3": "Additional vertical shift for lateral friction curve",
    "PVY4": "Additional vertical shift for lateral friction curve parameter",
    "RBY1": "Lateral friction curve break point - load dependency",
    "RBY2": "Lateral friction curve break point - speed dependency",
    "RBY3": "Lateral friction curve break point - load and speed dependency",
    "RCY1": "Lateral friction curve break point - shape factor",
    "REY1": "Lateral friction curve break point - load dependency",
    "REY2": "Lateral friction curve break point - speed dependency",
    "RHY1": "Horizontal shift for lateral friction curve break point",
    "RHY2": "Horizontal shift for lateral friction curve break point - speed",
    "RVY1": "Vertical shift for lateral friction curve break point",
    "RVY2": "Vertical shift for lateral friction curve break point - speed",
    "RVY3": "Vertical shift for lateral friction curve break point - load",
    "RVY4": "Vertical shift for lateral friction curve break point - load/speed",
    "RVY5": "Vertical shift for lateral friction curve break point parameter",
    "RVY6": "Vertical shift for lateral friction curve break point parameter",
    
    # Aligning Moment Parameters (Mz)
    "QBZ1": "Trail curvature - load dependency",
    "QBZ2": "Trail curvature - camber and speed dependency",
    "QBZ3": "Trail curvature - camber dependency",
    "QBZ4": "Trail curvature - load and speed dependency",
    "QBZ5": "Trail curvature - friction coefficient dependency",
    "QBZ9": "Trail curvature - speed dependency",
    "QBZ10": "Trail curvature - load and friction dependency",
    "QCZ1": "Peak aligning torque - shape factor",
    "QDZ1": "Peak aligning torque - load dependency",
    "QDZ2": "Peak aligning torque - camber dependency",
    "QDZ3": "Peak aligning torque - load and camber dependency",
    "QDZ4": "Peak aligning torque - speed dependency",
    "QDZ6": "Peak aligning torque - friction coefficient dependency",
    "QDZ7": "Peak aligning torque - load and friction dependency",
    "QDZ8": "Peak aligning torque - load and friction dependency parameter",
    "QDZ9": "Peak aligning torque - speed and friction dependency",
    "QEZ1": "Aligning torque curve shape curvature - load dependency",
    "QEZ2": "Aligning torque curve shape curvature - camber dependency",
    "QEZ3": "Aligning torque curve shape curvature - load and camber",
    "QEZ4": "Aligning torque curve shape curvature - speed dependency",
    "QEZ5": "Aligning torque curve shape curvature - friction dependency",
    "QHZ1": "Shift of peak aligning torque",
    "QHZ2": "Shift of peak aligning torque - load dependency",
    "QHZ3": "Shift of peak aligning torque - speed dependency",
    "QHZ4": "Shift of peak aligning torque - friction dependency",
    "SSZ1": "Nominal value of shift in aligning torque stiffness",
    "SSZ2": "Shift in aligning torque stiffness - load dependency",
    "SSZ3": "Shift in aligning torque stiffness - camber dependency",
    "SSZ4": "Shift in aligning torque stiffness - speed dependency",
    
    # Scaling Parameters
    "LFZ0": "Scaling factor for reference load",
    "LCX": "Scaling factor for longitudinal friction curve shape",
    "LMUX": "Scaling factor for maximum longitudinal friction",
    "LEX": "Scaling factor for longitudinal friction curve shape curvature",
    "LKX": "Scaling factor for longitudinal slip stiffness",
    "LHX": "Scaling factor for horizontal shift of longitudinal curve",
    "LVX": "Scaling factor for vertical shift of longitudinal curve",
    "LGAX": "Scaling factor for longitudinal load sensitivity",
    "LCY": "Scaling factor for lateral friction curve shape",
    "LMUY": "Scaling factor for maximum lateral friction",
    "LEY": "Scaling factor for lateral friction curve shape curvature",
    "LKY": "Scaling factor for cornering stiffness",
    "LHY": "Scaling factor for horizontal shift of lateral curve",
    "LVY": "Scaling factor for vertical shift of lateral curve",
    "LGAY": "Scaling factor for lateral load sensitivity",
    "LTR": "Scaling factor for pneumatic trail",
    "LGAZ": "Scaling factor for aligning torque load sensitivity",
    "LXAL": "Scaling factor for aligning moment sensitivity to lateral force",
    "LYKA": "Scaling factor for lateral acceleration sensitivity",
    "LVYKA": "Scaling factor for vertical load sensitivity of lateral stiffness",
    "LS": "Scaling factor for slip ratio",
    
    # Overturning Coefficients
    "QSX1": "Overturning torque - load dependency",
    "QSX2": "Overturning torque - speed dependency",
    "QSX3": "Overturning torque - friction coefficient dependency",
}

# Slider helper
# -------------------------

def slider_group_adjust(simple_dict: dict) -> dict:
    """
    Convert simple dict into modified dict using Streamlit sliders.
    All groups are displayed and can be adjusted.
    Includes undo/reset functionality via session state.
    """
    # Initialize session state for parameter history
    if "param_history" not in st.session_state:
        st.session_state.param_history = [json.loads(json.dumps(simple_dict))]
    if "history_index" not in st.session_state:
        st.session_state.history_index = 0
    
    st.sidebar.markdown("### Adjust parameters")
    
    # Undo/Reset controls
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button("↶ Undo", help="Undo last parameter change"):
            if st.session_state.history_index > 0:
                st.session_state.history_index -= 1
                st.rerun()
    with col2:
        if st.button("↷ Redo", help="Redo parameter change"):
            if st.session_state.history_index < len(st.session_state.param_history) - 1:
                st.session_state.history_index += 1
                st.rerun()
    with col3:
        if st.button("⟲ Reset", help="Reset to original parameters"):
            st.session_state.param_history = [json.loads(json.dumps(simple_dict))]
            st.session_state.history_index = 0
            st.rerun()
    
    st.sidebar.markdown(f"*History: {st.session_state.history_index + 1}/{len(st.session_state.param_history)}*")
    st.sidebar.markdown("---")

    # Only show groups that have parameters, including 'Scale' for lambdas
    available_groups = [g for g in ["Fx", "Fy", "Mz", "Scale"] if g in simple_dict and simple_dict[g]]
    
    if not available_groups:
        st.sidebar.warning("No parameters found to adjust")
        return simple_dict
    
    # Get current state from history
    current_state = st.session_state.param_history[st.session_state.history_index]
    out = json.loads(json.dumps(current_state))
    
    # Process each available group
    for group in available_groups:
        st.sidebar.markdown(f"**{group} Parameters:**")
        
        param_names = list(simple_dict[group].keys())
        
        # Allow selecting specific parameters to adjust
        chosen = st.sidebar.multiselect(
            f"Parameters to adjust in {group}",
            param_names,
            default=param_names[:3],
            key=f"params_{group}"
        )
        
        for p in chosen:
            v = float(simple_dict[group][p])
            span = abs(v) if v != 0 else 1
            current_val = float(current_state[group][p])
            
            new_val = st.sidebar.slider(
                f"{group}.{p}",
                v - 0.5 * span,
                v + 0.5 * span,
                current_val,
                step=span / 200,
                key=f"slider_{group}_{p}"
            )
            
            # Track changes in history
            if abs(new_val - float(current_state[group][p])) > 1e-9:
                # Truncate future history if we're not at the latest state
                if st.session_state.history_index < len(st.session_state.param_history) - 1:
                    st.session_state.param_history = st.session_state.param_history[:st.session_state.history_index + 1]
                
                # Create new history entry
                new_state = json.loads(json.dumps(st.session_state.param_history[-1]))
                new_state[group][p] = new_val
                st.session_state.param_history.append(new_state)
                st.session_state.history_index = len(st.session_state.param_history) - 1
            
            out[group][p] = new_val
        
        st.sidebar.markdown("---")
    
    return out



# -------------------------
# Main - Dashboard
# -------------------------
def main():
    st.set_page_config(layout="wide", page_title="Tire Model Dashboard")
    st.title("Pacejka / MF-Tyre")

    uploaded = st.file_uploader("Upload tyre JSON", type=["json"])
    if not uploaded:
        return

    full_json = json.load(uploaded)
    side = st.sidebar.radio("Tyre set", ["front", "rear"])
    base_internal = convert_json_to_internal(full_json, side)
    adjusted_internal = slider_group_adjust(base_internal)
    params = params_from_internal_dict(adjusted_internal)
    
    # Get original parameters for overlay comparison
    original_params = params_from_internal_dict(base_internal)

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Operating Conditions")
    
    Fz = st.sidebar.slider("Vertical Load Fz [N]", 1000.0, 10000.0, base_internal.get("Fz0", 5000.0), step=100.0)
    gamma_deg = st.sidebar.slider("Camber Angle γ [deg]", -10.0, 10.0, 0.0, step=0.5)
    alpha_deg = st.sidebar.slider("Slip Angle α [deg]", -15.0, 15.0, 5.0, step=0.5)
    
    # Data ranges for plots
    alpha_range_deg = np.linspace(-15, 15, 60)
    gamma_range_deg = np.linspace(-10, 10, 50)
    kappa_range = np.linspace(-0.3, 0.3, 50)
    
    # All available plots
    all_plots = {
        "Mz vs Slip Angle": ("plot_mz_vs_slip_angle", 2),
        "Mz vs Camber": ("plot_mz_vs_camber", 2),
        "Mz Multi-Camber": ("plot_mz_multi_camber", 2),
        "Pneumatic Trail vs Slip Angle": ("plot_pneumatic_trail_vs_slip", 2),
        "Fy vs Slip Angle": ("plot_fy_vs_slip_angle", 2),
        "Fy vs Camber": ("plot_fy_vs_camber", 2),
        "Fy Multi-Camber": ("plot_fy_multi_camber", 2),
        "Fy Multi-Force (Pure Slip)": ("plot_fy_multi_force_pure_slip", 2),
        "Fx vs Longitudinal Slip": ("plot_fx_vs_longitudinal_slip", 2),
        "Fx Multi-Force (Load Sensitivity)": ("plot_fx_multi_force_pure_slip", 2),
        "Fx Surface (α, κ)": ("plot_fx_surface", 3),
        "Fy Surface (α, κ)": ("plot_fy_surface", 3),
        "Mz Surface (α, κ)": ("plot_mz_surface", 3),
        "Combined-Slip Ellipse Envelope": ("plot_combined_slip_ellipse", 2),
    }


    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Parameter Viewer", "MF 5.2 Documentation"])
    
    with tab1:
        st.markdown("## Dashboard")
        
        # Dashboard configuration
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Dashboard Configuration")
        
        selected_plots = st.sidebar.multiselect(
            "Select plots to display",
            list(all_plots.keys()),
            default=["Mz vs Slip Angle", "Fy vs Slip Angle", "Fx vs Longitudinal Slip"]
        )
        
        if not selected_plots:
            st.info("Please select at least one plot to display")
        else:
            grid_columns = st.sidebar.slider("Columns in grid", 1, 4, 2)
            plot_height = st.sidebar.slider("Plot height (px)", 300, 800, 400)
            
            from plotting_functions import generate_plot
            
            # Create grid layout
            cols = st.columns(grid_columns)
            col_idx = 0
            
            for plot_name in selected_plots:
                with cols[col_idx % grid_columns]:
                    fig = generate_plot(
                        plot_name,
                        params,
                        Fz,
                        gamma_deg,
                        alpha_range_deg,
                        alpha_deg,
                        gamma_range_deg,
                        kappa_range,
                        original_params
                    )
                    # Update figure height
                    fig.update_layout(height=plot_height)
                    st.plotly_chart(fig, use_container_width=True, key=f"plot_{plot_name}_{col_idx}")
                col_idx += 1
    
    
    with tab2:
        st.markdown("## Parameter Viewer")
        
        # Get original parameters from base_internal
        original_params = params_from_internal_dict(base_internal)
        
        st.info("Click on any parameter to view its description and detailed information. Changed values are highlighted in orange.")
        
        # Helper function to display parameters with change indicators
        def display_params_single_column(original_param, current_param, container):
            if original_param and current_param:
                orig_dict = asdict(original_param)
                curr_dict = asdict(current_param)
                
                for key in orig_dict.keys():
                    orig_val = orig_dict[key]
                    curr_val = curr_dict.get(key, orig_val)
                    param_code = get_parameter_code(key)  # Convert to uppercase code
                    description = PARAMETER_INFO.get(param_code, "No description available")
                    
                    # Get affected formulas
                    param_info = get_parameter_info(param_code)
                    affected = param_info["affected_formulas"]
                    direct_count = len(affected["direct"])
                    indirect_count = len(affected["indirect"])
                    total_count = direct_count + indirect_count
                    
                    # Check if value changed (with small tolerance for float comparison)
                    if abs(curr_val - orig_val) > 1e-9:
                        # Changed parameter - use warning styling with custom HTML
                        container.markdown(f"""
                        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 8px 0; border-radius: 4px;">
                        <details>
                        <summary><b>{param_code}</b>: <code>{curr_val:.6f}</code> (was <code>{orig_val:.6f}</code>) <span style="color: #d32f2f; font-weight: bold;">• Affects {total_count} formula(s)</span></summary>
                        <div style="margin-top: 12px;">
                        <p><b>Parameter Code:</b> <code>{param_code}</code></p>
                        <p><b>Field Name:</b> <code>{key}</code></p>
                        <p><b>Description:</b> {description}</p>
                        <p><b>Current Value:</b> <code>{curr_val:.6f}</code></p>
                        <p><b>Original Value:</b> <code>{orig_val:.6f}</code></p>
                        <p><b>Change:</b> <code>{curr_val - orig_val:+.6f}</code></p>
                        <hr style="margin: 10px 0;">
                        <p><b>Affected Formulas:</b></p>
                        <ul>""", unsafe_allow_html=True)
                        
                        # Direct formulas
                        if affected["direct"]:
                            container.markdown(f"<li style='color: #d32f2f; font-weight: bold;'>Direct ({direct_count}):</li>", unsafe_allow_html=True)
                            for formula_name in affected["direct"]:
                                if formula_name in ALL_FORMULAS:
                                    formula = ALL_FORMULAS[formula_name]
                                    container.markdown(f"  - <code>{formula.name}</code>: {formula.description}", unsafe_allow_html=True)
                        
                        # Indirect formulas
                        if affected["indirect"]:
                            container.markdown(f"<li style='color: #f57c00; font-weight: bold;'>Indirect ({indirect_count}):</li>", unsafe_allow_html=True)
                            for formula_name in affected["indirect"]:
                                if formula_name in ALL_FORMULAS:
                                    formula = ALL_FORMULAS[formula_name]
                                    container.markdown(f"  - <code>{formula.name}</code>: {formula.description}", unsafe_allow_html=True)
                        
                        container.markdown("</ul></div></details></div>", unsafe_allow_html=True)
                    else:
                        # Unchanged parameter - normal styling
                        with container.expander(f"**{param_code}** ({key}): `{curr_val:.6f}` {' [' + str(total_count) + ' formulas]' if total_count > 0 else ''}"):
                            st.markdown(f"**Parameter Code:** `{param_code}`")
                            st.markdown(f"**Field Name:** `{key}`")
                            st.markdown(f"**Description:** {description}")
                            st.markdown(f"**Value:** `{curr_val:.6f}`")
                            
                            if total_count > 0:
                                st.markdown("---")
                                st.markdown(f"**Affects {total_count} formula(s):**")
                                
                                if affected["direct"]:
                                    st.markdown(f"**Direct ({direct_count}):**")
                                    for formula_name in affected["direct"]:
                                        if formula_name in ALL_FORMULAS:
                                            formula = ALL_FORMULAS[formula_name]
                                            st.markdown(f"- `{formula.name}`: {formula.description}")
                                
                                if affected["indirect"]:
                                    st.markdown(f"**Indirect ({indirect_count}):**")
                                    for formula_name in affected["indirect"]:
                                        if formula_name in ALL_FORMULAS:
                                            formula = ALL_FORMULAS[formula_name]
                                            st.markdown(f"- `{formula.name}`: {formula.description}")
            elif current_param:
                curr_dict = asdict(current_param)
                for key, value in curr_dict.items():
                    param_code = get_parameter_code(key)  # Convert to uppercase code
                    description = PARAMETER_INFO.get(param_code, "No description available")
                    
                    # Get affected formulas
                    param_info = get_parameter_info(param_code)
                    affected = param_info["affected_formulas"]
                    direct_count = len(affected["direct"])
                    indirect_count = len(affected["indirect"])
                    total_count = direct_count + indirect_count
                    
                    with container.expander(f"**{param_code}** ({key}): `{value:.6f}` {' [' + str(total_count) + ' formulas]' if total_count > 0 else ''}"):
                        st.markdown(f"**Parameter Code:** `{param_code}`")
                        st.markdown(f"**Field Name:** `{key}`")
                        st.markdown(f"**Description:** {description}")
                        st.markdown(f"**Value:** `{value:.6f}`")
                        
                        if total_count > 0:
                            st.markdown("---")
                            st.markdown(f"**Affects {total_count} formula(s):**")
                            
                            if affected["direct"]:
                                st.markdown(f"**Direct ({direct_count}):**")
                                for formula_name in affected["direct"]:
                                    if formula_name in ALL_FORMULAS:
                                        formula = ALL_FORMULAS[formula_name]
                                        st.markdown(f"- `{formula.name}`: {formula.description}")
                            
                            if affected["indirect"]:
                                st.markdown(f"**Indirect ({indirect_count}):**")
                                for formula_name in affected["indirect"]:
                                    if formula_name in ALL_FORMULAS:
                                        formula = ALL_FORMULAS[formula_name]
                                        st.markdown(f"- `{formula.name}`: {formula.description}")
        
        # Create 2-column layout
        col1, col2 = st.columns(2)
        
        # Left column: Longitudinal and Reference
        with col1:
            st.markdown("### Longitudinal Parameters (Fx)")
            display_params_single_column(original_params.Fx, params.Fx, st)

            st.markdown("### Lateral Parameters (Fy)")
            display_params_single_column(original_params.Fy, params.Fy, st)
            
            st.markdown("### Reference Parameters")
            r0_changed = abs(params.R0 - original_params.R0) > 1e-9
            fz0_changed = abs(params.Fz0 - original_params.Fz0) > 1e-9
            
            if r0_changed:
                st.markdown(f"""
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 8px 0; border-radius: 4px;">
                <details>
                <summary><b>R0</b> (Tire Radius): <code>{params.R0:.6f}</code> m (was <code>{original_params.R0:.6f}</code> m)</summary>
                <div style="margin-top: 12px;">
                <p><b>Current Value:</b> <code>{params.R0:.6f}</code> m</p>
                <p><b>Original Value:</b> <code>{original_params.R0:.6f}</code> m</p>
                <p><b>Change:</b> <code>{params.R0 - original_params.R0:+.6f}</code> m</p>
                </div>
                </details>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.expander(f"**R0** (Tire Radius): `{params.R0:.6f}` m"):
                    st.markdown(f"**Value:** `{params.R0:.6f}` m")
            
            if fz0_changed:
                st.markdown(f"""
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 8px 0; border-radius: 4px;">
                <details>
                <summary><b>Fz0</b> (Reference Normal Force): <code>{params.Fz0:.6f}</code> N (was <code>{original_params.Fz0:.6f}</code> N)</summary>
                <div style="margin-top: 12px;">
                <p><b>Current Value:</b> <code>{params.Fz0:.6f}</code> N</p>
                <p><b>Original Value:</b> <code>{original_params.Fz0:.6f}</code> N</p>
                <p><b>Change:</b> <code>{params.Fz0 - original_params.Fz0:+.6f}</code> N</p>
                </div>
                </details>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.expander(f"**Fz0** (Reference Normal Force): `{params.Fz0:.6f}` N"):
                    st.markdown(f"**Value:** `{params.Fz0:.6f}` N")
        
        # Right column: Lateral, Aligning, and Scaling
        with col2:

            st.markdown("### Aligning Moment Parameters (Mz)")
            display_params_single_column(original_params.Mz, params.Mz, st)

            st.markdown("### Scaling Parameters")
            display_params_single_column(original_params.Scale, params.Scale, st)
            

        
        # Operating conditions spanning full width
        st.markdown("---")
        st.markdown("### Operating Conditions")
        col_op1, col_op2, col_op3 = st.columns(3)
        with col_op1:
            st.metric("Vertical Load (Fz)", f"{Fz:.2f} N")
        with col_op2:
            st.metric("Camber Angle (γ)", f"{gamma_deg:.2f}°")
        with col_op3:
            st.metric("Slip Angle (α)", f"{alpha_deg:.2f}°")
        
        # Display changed parameters plots section
        st.markdown("---")
        if st.button("Display Changed Parameters Plots"):
            st.markdown("### Impact of Parameter Changes")
            
            # Check if any parameters have changed
            orig_dict_fx = asdict(original_params.Fx)
            curr_dict_fx = asdict(params.Fx)
            orig_dict_fy = asdict(original_params.Fy)
            curr_dict_fy = asdict(params.Fy)
            orig_dict_mz = asdict(original_params.Mz)
            curr_dict_mz = asdict(params.Mz)
            
            any_changed = (
                any(abs(curr_dict_fx.get(k, 0) - orig_dict_fx.get(k, 0)) > 1e-9 for k in orig_dict_fx) or
                any(abs(curr_dict_fy.get(k, 0) - orig_dict_fy.get(k, 0)) > 1e-9 for k in orig_dict_fy) or
                any(abs(curr_dict_mz.get(k, 0) - orig_dict_mz.get(k, 0)) > 1e-9 for k in orig_dict_mz)
            )
            
            if any_changed:
                # Create 3-column layout for main plots
                col_plot1, col_plot2, col_plot3 = st.columns(3)
                
                with col_plot1:
                    fig_fx = plot_fx_vs_longitudinal_slip(params, Fz, kappa_range, alpha_deg, gamma_deg, original_params)
                    fig_fx.update_layout(height=400)
                    st.plotly_chart(fig_fx, use_container_width=True, key="param_viewer_fx")
                
                with col_plot2:
                    fig_fy = plot_fy_vs_slip_angle(params, Fz, gamma_deg, alpha_range_deg, original_params)
                    fig_fy.update_layout(height=400)
                    st.plotly_chart(fig_fy, use_container_width=True, key="param_viewer_fy")
                
                with col_plot3:
                    fig_mz = plot_mz_vs_slip_angle(params, Fz, gamma_deg, alpha_range_deg, original_params)
                    fig_mz.update_layout(height=400)
                    st.plotly_chart(fig_mz, use_container_width=True, key="param_viewer_mz")
            else:
                st.info("No parameters have been changed yet. Adjust parameters above to see their impact.")
    
    with tab3:
        st.markdown("## Magic Formula Documentation")
        
        # Create sub-tabs for Documentation and Formula Browser
        doc_tab1, doc_tab2 = st.tabs(["MF5.2 Reference", "Formula Browser & Impact Analysis"])
        
        with doc_tab1:
            st.markdown("""
                        
The model implemented in this dashboard is based on the Magic Formula Tire Model version 5.2 (MF 5.2) For purpose of clarity the numbering follows the original MF 5.2 documentation
                        
Below you can find the orignal documenation of 5.2 used to develop this model as well as info on later versions.""")
            
            # PDF Display Section
            st.markdown("#### Reference PDFs")
            
            # Check if PDF files exist in the directory
            import os
            pdf_dir = os.path.dirname(os.path.abspath(__file__))
            pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
            
            if pdf_files:
                # Create columns for PDF display
                cols = st.columns(len(pdf_files))
                
                for idx, pdf_file in enumerate(pdf_files):
                    with cols[idx]:
                        pdf_path = os.path.join(pdf_dir, pdf_file)
                        with open(pdf_path, "rb") as f:
                            pdf_data = f.read()
                        
                        st.download_button(
                            label=f"Download {pdf_file}",
                            data=pdf_data,
                            file_name=pdf_file,
                            mime="application/pdf",
                            key=f"download_{pdf_file}"
                        )
            else:
                st.info("No PDF files found in the application directory")
            
            st.markdown("""#### Reference Statement


All parameter definitions, mathematical formulations, tyre-model equations, and explanatory material used in this work have been taken directly from the following documents:

• Using the MF-Tyre Model, TNO Automotive 

• Besselink, I.J.M., Schmeitz, A.J.C., & Pacejka, H.B. (2010). An improved Magic Formula/SWIFT tyre model that can handle inflation pressure changes. Proceedings of IAVSD 2009 

• MF-Tyre/MF-Swift 6.2 Help Manual, TNO (2013) """)
        
        with doc_tab2:
            st.markdown("## Formula Browser & Impact Analysis")
            
            st.markdown("""
This tool helps you understand the tire model formulas and how parameter changes propagate through the model.
- **Search** for specific formulas by name or parameter
- **View** detailed formula information including equations and dependencies
- **Understand** the impact chain: which formulas affect which outputs
- **Trace** parameter effects through direct and indirect dependencies
            """)
            
            # Formula search and filtering
            col_search1, col_search2 = st.columns([2, 1])
            
            with col_search1:
                search_query = st.text_input(
                    "Search formulas",
                    placeholder="e.g., 'Fx0', 'friction', 'PCX1', 'slip angle'",
                    help="Search by formula name, description, or parameter"
                )
            
            with col_search2:
                category_filter = st.selectbox(
                    "Category",
                    ["All", "Fx", "Fy", "Mz", "intermediate"],
                    help="Filter by formula category"
                )
            
            # Filter formulas
            filtered_formulas = {}
            search_lower = search_query.lower()
            
            for formula_name, formula_info in ALL_FORMULAS.items():
                # Check category filter
                if category_filter != "All" and formula_info.category != category_filter:
                    continue
                
                # Check search query
                if search_query:
                    matches = (
                        search_lower in formula_name.lower() or
                        search_lower in formula_info.description.lower() or
                        any(search_lower in param.lower() for param in formula_info.parameters)
                    )
                    if not matches:
                        continue
                
                filtered_formulas[formula_name] = formula_info
            
            # Display results
            if filtered_formulas:
                st.markdown(f"### Found {len(filtered_formulas)} formula(s)")
                
                # Sort by category then name
                sorted_formulas = sorted(
                    filtered_formulas.items(),
                    key=lambda x: (x[1].category, x[0])
                )
                
                for formula_name, formula_info in sorted_formulas:
                    # Category label
                    category_label = f"[{formula_info.category}]" if formula_info.category != "intermediate" else "[Helper]"
                    
                    with st.expander(f"{category_label} **{formula_info.name}** - {formula_info.description}"):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown("**Formula Details:**")
                            st.markdown(f"**Name:** `{formula_info.name}`")
                            st.markdown(f"**Category:** `{formula_info.category}`")
                            st.markdown(f"**Description:** {formula_info.description}")
                        
                        with col2:
                            st.markdown("**Equation:**")
                            st.latex(formula_info.equation)
                        
                        st.markdown("---")
                        
                        # Parameters used
                        if formula_info.parameters:
                            st.markdown("**Parameters Used:**")
                            param_cols = st.columns(min(3, len(formula_info.parameters)))
                            for idx, param in enumerate(formula_info.parameters):
                                with param_cols[idx % 3]:
                                    st.code(param, language="")
                        
                        # Dependencies
                        if formula_info.depends_on:
                            st.markdown("**Depends On (Direct Dependencies):**")
                            dep_cols = st.columns(min(3, len(formula_info.depends_on)))
                            for idx, dep in enumerate(formula_info.depends_on):
                                with dep_cols[idx % 3]:
                                    if dep in ALL_FORMULAS:
                                        dep_info = ALL_FORMULAS[dep]
                                        st.markdown(f"• `{dep_info.name}` - {dep_info.description}")
                        
                        # Impact analysis - what formulas depend on this one
                        dependent_formulas = [
                            (name, info) for name, info in ALL_FORMULAS.items()
                            if formula_name in info.depends_on
                        ]
                        
                        if dependent_formulas:
                            st.markdown("**Downstream Impact (Formulas That Depend On This):**")
                            for dep_name, dep_info in dependent_formulas:
                                st.markdown(f"• `{dep_info.name}` - {dep_info.description}")
                        
                        # Parameter impact analysis
                        st.markdown("---")
                        st.markdown("**Parameter Impact Analysis:**")
                        
                        if formula_info.parameters:
                            st.markdown(f"If you change any of these {len(formula_info.parameters)} parameter(s):")
                            for param in formula_info.parameters:
                                param_info = get_parameter_info(param)
                                affected = param_info["affected_formulas"]
                                st.markdown(f"- **{param}**: Affects {len(affected['direct']) + len(affected['indirect'])} formula(s)")
                        else:
                            st.markdown("*This formula uses no direct parameters (only calculated values)*")
            else:
                if search_query or category_filter != "All":
                    st.info("No formulas found matching your search. Try adjusting your filters.")
                else:
                    st.info("Use the search box to find and explore formulas.")
            
            # Quick reference section
            st.markdown("---")
            st.markdown("### Quick Reference - Formula Categories")
            
            col_ref1, col_ref2, col_ref3, col_ref4 = st.columns(4)
            
            with col_ref1:
                fx_count = len([f for f in ALL_FORMULAS.values() if f.category == "Fx"])
                st.metric("Fx Formulas", fx_count)
            
            with col_ref2:
                fy_count = len([f for f in ALL_FORMULAS.values() if f.category == "Fy"])
                st.metric("Fy Formulas", fy_count)
            
            with col_ref3:
                mz_count = len([f for f in ALL_FORMULAS.values() if f.category == "Mz"])
                st.metric("Mz Formulas", mz_count)
            
            with col_ref4:
                total_count = len(ALL_FORMULAS)
                st.metric("Total Formulas", total_count)
        
        st.markdown("""
---

## General Magic Formula

The core Magic Formula is a smooth nonlinear function used throughout MF 5.2:

$$Y = D \\sin\\left(C \\arctan\\left(Bx - E(Bx - \\arctan(Bx))\\right)\\right) + V$$

Where:
- **B**: Stiffness factor
- **C**: Shape factor  
- **D**: Peak value
- **E**: Curvature factor (typically near 1.0)
- **x**: Input (slip, slip angle, etc.)
- **Y**: Output force or moment
- **V**: Vertical shift

---

## 1. Longitudinal Force (Fx)

### Pure Slip Condition

**Load normalization:**
$$\\Delta F_z = \\frac{F_z - F_{z0}}{F_{z0}}$$

**Horizontal shift:**
$$S_{Hx} = (p_{Hx1} + p_{Hx2} \\Delta F_z) \\lambda_{HX} \\quad \\text{(26)}$$

**Vertical shift:**
$$S_{Vx} = F_z (p_{Vx1} + p_{Vx2} \\Delta F_z) \\lambda_{MUX} \\lambda_{VX} \\quad \\text{(27)}$$

**Longitudinal slip state:**
$$\\kappa_x = \\kappa + S_{Hx} \\quad \\text{(18)}$$

**Camber effect:**
$$\\gamma_x = \\gamma \\lambda_{GAX} \\quad \\text{(19)}$$

**Friction coefficient:**
$$\\mu_x = (p_{Dx1} + p_{Dx2} \\Delta F_z)(1 - p_{Dx3} \\gamma_x^2) \\lambda_{MUX} \\quad \\text{(22)}$$

**Pacejka coefficients:**

$$C_x = p_{Cx1} \\lambda_{CX} \\quad \\text{(20)}$$

$$D_x = \\mu_x F_z \\quad \\text{(20)}$$

$$E_x = (p_{Ex1} + p_{Ex2} \\Delta F_z + p_{Ex3} \\Delta F_z^2)(1 - p_{Ex4} \\text{sgn}(\\kappa_x)) \\lambda_{EX} \\quad \\text{(23)}$$

$$K_x = F_z(p_{Kx1} + p_{Kx2} \\Delta F_z) e^{p_{Kx3} \\Delta F_z} \\lambda_{KX} \\quad \\text{(24)}$$

$$B_x = \\frac{K_x}{C_x D_x} \\quad \\text{(25)}$$

**Pure slip longitudinal force:**
$$F_{x0} = D_x \\sin\\left(C_x \\arctan\\left(B_x \\kappa_x - E_x(B_x \\kappa_x - \\arctan(B_x \\kappa_x))\\right)\\right) + S_{Vx}$$

### Combined Slip Condition

**Horizontal shift:**
$$S_{Hxa} = p_{Hx1} \\quad \\text{(63)}$$

**Slip angle with shift:**
$$\\alpha_s = \\alpha + S_{Hxa} \\quad \\text{(58)}$$

**Weighting coefficients:**

$$B_{xa} = p_{Bx1} \\cos\\left(\\arctan(p_{Bx2} \\kappa)\\right) \\lambda_{XAL} \\quad \\text{(59)}$$

$$C_{xa} = p_{Cx1} \\quad \\text{(60)}$$

$$E_{xa} = p_{Ex1} + p_{Ex2} \\Delta F_z \\quad \\text{(62)}$$

$$D_x = \\frac{F_{x0}}{\\cos\\left(C_{xa} \\arctan\\left(B_{xa} S_{Hxa} - E_{xa}(B_{xa} S_{Hxa} - \\arctan(B_{xa} S_{Hxa}))\\right)\\right)} \\quad \\text{(61)}$$

**Combined slip weighting function:**
$$G_{xa} = \\frac{\\cos\\left(C_{xa} \\arctan\\left(B_{xa} \\alpha_s - E_{xa}(B_{xa} \\alpha_s - \\arctan(B_{xa} \\alpha_s))\\right)\\right)}{\\cos\\left(C_{xa} \\arctan\\left(B_{xa} S_{Hxa} - E_{xa}(B_{xa} S_{Hxa} - \\arctan(B_{xa} S_{Hxa}))\\right)\\right)} \\quad \\text{(64)}$$

**Final combined longitudinal force:**
$$F_x = F_{x0} \\cdot G_{xa}$$

---

## 2. Lateral Force (Fy)

### Pure Slip Condition

**Camber effect:**
$$\\gamma_y = \\gamma \\lambda_{GAY} \\quad \\text{(31)}$$

**Horizontal shift:**
$$S_{Hy} = (p_{Hy1} + p_{Hy2} \\Delta F_z) \\lambda_{HY} + p_{Hy3} \\gamma_y \\quad \\text{(38)}$$

**Vertical shift:**
$$S_{Vy} = F_z \\left[(p_{Vy1} + p_{Vy2} \\Delta F_z) \\lambda_{VY} + (p_{Vy3} + p_{Vy4} \\Delta F_z) \\gamma_y\\right] \\lambda_{MUY} \\quad \\text{(39)}$$

**Lateral slip state:**
$$\\alpha_y = \\alpha + S_{Hy} \\quad \\text{(30)}$$

**Friction coefficient:**
$$\\mu_y = (p_{Dy1} + p_{Dy2} \\Delta F_z)(1 - p_{Dy3} \\gamma_y^2) \\lambda_{MUY} \\quad \\text{(34)}$$

**Pacejka coefficients:**

$$C_y = p_{Cy1} \\lambda_{CY} \\quad \\text{(32)}$$

$$D_y = \\mu_y F_z \\quad \\text{(33)}$$

$$E_y = (p_{Ey1} + p_{Ey2} \\Delta F_z) (1 - (p_{Ey3} + p_{Ey4} \\gamma_y) \\text{sgn}(\\alpha_y)) \\lambda_{EY} \\quad \\text{(35)}$$

$$K_y = p_{Ky1} F_{z0} \\sin\\left(2 \\arctan\\left(\\frac{F_z}{p_{Ky2} F_{z0} \\lambda_{FZ0}}\\right)\\right) (1 - p_{Ky3} |\\gamma_y|) \\lambda_{FZ0} \\lambda_{KY} \\quad \\text{(36)}$$

$$B_y = \\frac{K_y}{C_y D_y} \\quad \\text{(37)}$$

**Pure slip lateral force:**
$$F_{y0} = D_y \\sin\\left(C_y \\arctan\\left(B_y \\alpha_y - E_y(B_y \\alpha_y - \\arctan(B_y \\alpha_y))\\right)\\right) + S_{Vy}$$

### Combined Slip Condition

**Horizontal shift for combined slip:**
$$S_{Hyk} = p_{Hy1} + p_{Hy2} \\Delta F_z \\quad \\text{(72)}$$

**Longitudinal slip with shift:**
$$\\kappa_s = \\kappa + S_{Hyk} \\quad \\text{(67)}$$

**Weighting coefficients:**

$$B_{yk} = p_{By1} \\cos\\left(\\arctan(p_{By2}(\\alpha - p_{By3}))\\right) \\lambda_{YKA} \\quad \\text{(68)}$$

$$C_{yk} = p_{Cy1} \\quad \\text{(69)}$$

$$E_{yk} = p_{Ey1} + p_{Ey2} \\Delta F_z \\quad \\text{(71)}$$

$$D_{yk} = \\frac{F_{y0}}{\\cos\\left(C_{yk} \\arctan\\left(B_{yk} S_{Hyk} - E_{yk}(B_{yk} S_{Hyk} - \\arctan(B_{yk} S_{Hyk}))\\right)\\right)} \\quad \\text{(70)}$$

**Vertical shift for combined slip:**
$$S_{Vyk} = D_{Vyk} \\sin\\left(p_{Vy5} \\arctan(p_{Vy6} \\kappa)\\right) \\lambda_{VYKA} \\quad \\text{(73)}$$

Where:
$$D_{Vyk} = \\mu_y F_z (p_{Vy1} + p_{Vy2} \\Delta F_z + p_{Vy3} \\gamma) \\cos\\left(\\arctan(p_{Vy4} \\alpha)\\right) \\quad \\text{(74)}$$

**Combined slip weighting function:**
$$G_{yk} = \\frac{\\cos\\left(C_{yk} \\arctan\\left(B_{yk} \\kappa_s - E_{yk}(B_{yk} \\kappa_s - \\arctan(B_{yk} \\kappa_s))\\right)\\right)}{\\cos\\left(C_{yk} \\arctan\\left(B_{yk} S_{Hyk} - E_{yk}(B_{yk} S_{Hyk} - \\arctan(B_{yk} S_{Hyk}))\\right)\\right)} \\quad \\text{(75)}$$

**Final combined lateral force:**
$$F_y = F_{y0} \\cdot G_{yk} + S_{Vyk} \\quad \\text{(65)}$$

---

## 3. Self-Aligning Moment (Mz)

The self-aligning moment is composed of two parts: the pneumatic trail contribution and the residual torque.

### Pneumatic Trail (Pure Slip)

**Vertical shift:**

$$S_{Ht} = p_{Hz1} + p_{Hz2} \\Delta F_z + (p_{Hz3} + p_{Hz4} \\Delta F_z) \\gamma_z \\quad \\text{(52)}$$


Where:

$$\\gamma_z = \\gamma \\lambda_{GAZ}$$


**Trail coefficients:**

$$C_t = p_{Cz1} \\quad \\text{(49)}$$


$$D_t = F_z (p_{Dz1} + p_{Dz2} \\Delta F_z) (1 + p_{Dz3} \\gamma_z + p_{Dz4} \\gamma_z^2) \\frac{R_0}{F_{z0}} \\lambda_{T} \\quad \\text{(50)}$$


$$B_t = (p_{Bz1} + p_{Bz2} \\Delta F_z + p_{Bz3} \\Delta F_z^2) (1 + p_{Bz4} \\gamma_z + p_{Bz5} |\\gamma_z|) \\frac{\\lambda_{KY}}{\\lambda_{MUY}} \\quad \\text{(48)}$$


**Trail slip state:**

$$\\alpha_t = \\alpha + S_{Ht} \\quad \\text{(43)}$$


**Curvature factor:**

$$E_t = (p_{Ez1} + p_{Ez2} \\Delta F_z + p_{Ez3} \\Delta F_z^2) \\left(1 + (p_{Ez4} + p_{Ez5} \\gamma_z) \\frac{2}{\\pi} \\arctan(B_t C_t \\alpha_t)\\right) \\quad \\text{(51)}$$


**Pneumatic trail:**

$$t = D_t \\cos\\left(C_t \\arctan\\left(B_t \\alpha_t - E_t(B_t \\alpha_t - \\arctan(\\alpha_t))\\right)\\right) \\cos(\\alpha)$$

### Residual Torque

**Residual torque coefficient:**

$$D_r = F_z \\left[(p_{Dz6} + p_{Dz7} \\Delta F_z) \\lambda_{Mr} + (p_{Dz8} + p_{Dz9} \\Delta F_z) \\gamma_z\\right] R_0 \\lambda_{MUY} \\quad \\text{(54)}$$


**Reference slip angle:**

$$\\alpha_r = \\alpha + S_{Hf} \\quad \\text{(45)}$$


Where:

$$S_{Hf} = S_{Hy} + \\frac{S_{Vy}}{K_y}$$


**Residual torque:**

$$B_r = p_{Bz9} \\frac{\\lambda_{KY}}{\\lambda_{MUY}} + p_{Bz10} B_y C_y$$


$$M_{zr} = D_r \\cos(\\arctan(B_r \\alpha_r)) \\cos(\\alpha) \\quad \\text{(44)}$$


### Total Self-Aligning Moment

$$M_{z0} = -t \\cdot F_{y0} + M_{zr} \\quad \\text{(41)}$$

---

## Helper Functions

**Sign function:**
$$\\text{sgn}(x) = \\begin{cases} 1.0 & \\text{if } x > 0 \\\\ -1.0 & \\text{if } x < 0 \\\\ 0.0 & \\text{if } x = 0 \\end{cases}$$

---

## Scaling Factors (L-coefficients)

These factors scale the base model coefficients for different tire specifications:

| Factor | Application |
|--------|-------------|
| $\\lambda_{FZ0}$ | Reference load scaling |
| $\\lambda_{MUX}$, $\\lambda_{MUY}$ | Friction coefficient |
| $\\lambda_{CX}$, $\\lambda_{CY}$ | Shape factor |
| $\\lambda_{EX}$, $\\lambda_{EY}$ | Curvature factor |
| $\\lambda_{KX}$, $\\lambda_{KY}$ | Slip/cornering stiffness |
| $\\lambda_{HX}$, $\\lambda_{HY}$ | Horizontal shift |
| $\\lambda_{VX}$, $\\lambda_{VY}$ | Vertical shift |
| $\\lambda_{GAX}$, $\\lambda_{GAY}$, $\\lambda_{GAZ}$ | Camber sensitivity |
| $\\lambda_{T}$ | Trail scaling |
| $\\lambda_{Mr}$ | Residual torque scaling |
| $\\lambda_{XAL}$ | Aligning moment - lateral load |
| $\\lambda_{YKA}$ | Lateral - longitudinal coupling |
| $\\lambda_{VYKA}$ | Vertical load sensitivity |

        """)

if __name__ == "__main__":
    main()
