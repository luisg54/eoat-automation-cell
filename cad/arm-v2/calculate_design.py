"""Transparent first-principles sizing. Estimates, not physical test results.

No third-party packages, FEA, CAD launch, or large memory allocations.
All masses below are conservative allocation targets pending actual CAD volumes.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'design-parameters.json').read_text())
G = 9.80665

def calculate(payload_g=20):
    upper = P['upper_link_centres_mm'] / 1000
    lower = P['forearm_link_centres_mm'] / 1000
    # Named allocations make replacing estimates with CAD/weighed masses explicit.
    masses = dict(upper_link_g=18, elbow_servo_and_support_g=20,
                  forearm_g=12, gripper_including_servo_g=28,
                  payload_g=payload_g)
    shoulder_items = [
        ('upper link', masses['upper_link_g'], upper/2),
        ('elbow servo/support', masses['elbow_servo_and_support_g'], upper),
        ('forearm', masses['forearm_g'], upper+lower/2),
        ('gripper', masses['gripper_including_servo_g'], upper+lower),
        ('payload', payload_g, upper+lower),
    ]
    shoulder_static = sum(m/1000 * G * r for _, m, r in shoulder_items)
    elbow_static = G * (masses['forearm_g']/1000*lower/2
                       +(masses['gripper_including_servo_g']+payload_g)/1000*lower)
    torque_budget = P['servo_stall_reference_Nm'] * P['servo_design_fraction_of_reference_stall']
    shoulder_available = P['shoulder_servo_stall_reference_Nm'] * P['servo_design_fraction_of_reference_stall'] * P['shoulder_reduction_ratio'] * P['shoulder_transmission_efficiency_assumed']
    acceleration_factor = 1.25
    shoulder_design = shoulder_static * acceleration_factor
    elbow_design = elbow_static * acceleration_factor
    # Flat link preliminary bending check: bending in its print XY plane.
    # Rectangular equivalent excludes holes; detailed root stress remains unchecked.
    link_width, link_thickness = 12, 4
    section_modulus = link_thickness*link_width**2/6
    upper_bending = shoulder_design*1000/section_modulus
    bearing_dowel_radial_clearance = (P['bearing_ID_mm']-P['dowel_diameter_mm'])/2
    # For two jaws, 2*mu*N >= design payload weight.
    assumed_pad_mu = .3
    clamp_force_each = 2 * payload_g/1000*G / (2*assumed_pad_mu)
    report = {
        'status': 'PRELIMINARY ESTIMATE; masses and servo performance require verification',
        'mass_allocations_g': masses,
        'max_geometric_reach_mm': (upper+lower)*1000,
        'servo_design_budget_Nm': torque_budget,
        'dynamic_allowance_factor': acceleration_factor,
        'shoulder_static_Nm': shoulder_static,
        'shoulder_design_Nm': shoulder_design,
        'shoulder_available_after_reduction_Nm': shoulder_available,
        'shoulder_margin_ratio': shoulder_available/shoulder_design,
        'elbow_static_Nm': elbow_static,
        'elbow_design_Nm': elbow_design,
        'elbow_margin_ratio': torque_budget/elbow_design,
        'shoulder_travel_for_150deg_servo_deg': 150/P['shoulder_reduction_ratio'],
        'upper_link_nominal_bending_estimate_MPa': upper_bending,
        'dowel_in_608_radial_clearance_mm': bearing_dowel_radial_clearance,
        'two_jaw_normal_force_each_N_mu_0p3_SF2': clamp_force_each,
        'must_verify': [
            'Purchased SG90 dimensions, horn geometry and usable travel',
            'Actual CAD solid volumes, slicing mass and weighed assembly mass',
            'Horn connections, joint support, backlash and full travel collisions',
            'Native assembly degrees of freedom and part fit',
            'Quasi-static and dynamic servo capability at regulated supply voltage',
            'Thermal duty cycle, printed creep, fatigue and pin retention',
            'Grip friction, dropped-power behavior and 50-cycle retention test'
        ]
    }
    if shoulder_available < shoulder_design or torque_budget < elbow_design:
        raise ValueError('Allocated mass/payload exceeds preliminary torque budget')
    return report

if __name__ == '__main__':
    result = calculate(P['payload_target_g'])
    (ROOT/'calculation-results.json').write_text(json.dumps(result, indent=2)+'\n')
    for k,v in result.items():
        if isinstance(v, (int,float)):
            print(f'{k}: {v:.4f}')
