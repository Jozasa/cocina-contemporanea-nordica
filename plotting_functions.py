# plotting_functions.py
# This file will contain plotting-related functions moved from app.py


# Import all plot functions from plots.py
from plots import (
	plot_mz_vs_slip_angle,
	plot_mz_vs_camber,
	plot_pneumatic_trail_vs_slip,
	plot_fy_vs_slip_angle,
	plot_fy_vs_camber,
	plot_fx_vs_longitudinal_slip,
	plot_mz_multi_camber,
	plot_fy_multi_camber,
	plot_fy_multi_force_pure_slip,
	plot_fx_multi_force_pure_slip,
	plot_combined_slip_ellipse,
	plot_fx_surface,
	plot_fy_surface,
	plot_mz_surface
)


# Helper function to generate plots (moved from app.py)
def generate_plot(plot_name, params, Fz, gamma_deg, alpha_range_deg, alpha_deg, gamma_range_deg, kappa_range, original_params):
	if plot_name == "Mz vs Slip Angle":
		return plot_mz_vs_slip_angle(params, Fz, gamma_deg, alpha_range_deg, original_params)
	elif plot_name == "Mz vs Camber":
		return plot_mz_vs_camber(params, Fz, alpha_deg, gamma_range_deg, original_params)
	elif plot_name == "Mz Multi-Camber":
		camber_values = [0, 2, 4, 6]
		return plot_mz_multi_camber(params, Fz, alpha_range_deg, camber_values)
	elif plot_name == "Pneumatic Trail vs Slip Angle":
		return plot_pneumatic_trail_vs_slip(params, Fz, gamma_deg, alpha_range_deg, original_params)
	elif plot_name == "Fy vs Slip Angle":
		return plot_fy_vs_slip_angle(params, Fz, gamma_deg, alpha_range_deg, original_params)
	elif plot_name == "Fy vs Camber":
		return plot_fy_vs_camber(params, Fz, alpha_deg, gamma_range_deg, original_params)
	elif plot_name == "Fy Multi-Camber":
		camber_values = [0, 2, 4, 6]
		return plot_fy_multi_camber(params, Fz, alpha_range_deg, camber_values)
	elif plot_name == "Fy Multi-Force (Pure Slip)":
		fz_values = [2000, 3500, 5000, 6500, 8000]
		return plot_fy_multi_force_pure_slip(params, alpha_range_deg, gamma_deg, fz_values)
	elif plot_name == "Fx vs Longitudinal Slip":
		return plot_fx_vs_longitudinal_slip(params, Fz, kappa_range, alpha_deg, gamma_deg, original_params)
	elif plot_name == "Fx Multi-Force (Load Sensitivity)":
		fz_values = [2000, 3500, 5000, 6500, 8000]
		return plot_fx_multi_force_pure_slip(params, kappa_range, alpha_deg, fz_values)
	elif plot_name == "Fx Surface (α, κ)":
		return plot_fx_surface(params, Fz, gamma_deg, alpha_range_deg, kappa_range)
	elif plot_name == "Fy Surface (α, κ)":
		return plot_fy_surface(params, Fz, gamma_deg, alpha_range_deg, kappa_range)
	elif plot_name == "Mz Surface (α, κ)":
		return plot_mz_surface(params, Fz, gamma_deg, alpha_range_deg, kappa_range)
	elif plot_name == "Combined-Slip Ellipse Envelope":
		return plot_combined_slip_ellipse(params, Fz, gamma_deg, alpha_range_deg, kappa_range)
