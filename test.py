import numpy as np
import plotly.graph_objects as go

# Define constants (example)
E = 200e9  # Modulus of Elasticity (N/m^2)
I = 5000e-8  # Moment of Inertia (m^4)
L = 5.0  # Length of the beam (m)
point_loads = [{'magnitude': 10.0, 'location': 2.0}]  # Single point load of 10 kN at 2 m

# Define reaction forces (simplified for this example)
reaction_A = 6.0  # Reaction at support A (N)
reaction_B = 4.0  # Reaction at support B (N)

# Calculate deflection (corrected)
def calculate_deflection(x, point_loads, E, I, L):
    D = np.zeros_like(x)
    
    for i, xi in enumerate(x):  # Iterate over each point along the beam
        deflection = 0
        
        for load in point_loads:  # Sum contributions of each point load
            P = load['magnitude']  # Point load magnitude
            a = load['location']   # Location of the point load
            
            if xi < a:
                # Deflection contribution for points before the load
                deflection += (P * xi * (L - xi) * (3 * a - xi)) / (6 * E * I * L)
            else:
                # Deflection contribution for points after the load
                deflection += (P * (L - xi) * (3 * xi - L - a)) / (6 * E * I * L)

        D[i] = deflection  # Store the deflection at point xi
    
    return D

# Generate x values along the length of the beam
x = np.linspace(0, L, 1000)

# Calculate deflection at each point along the beam
deflection = calculate_deflection(x, point_loads, E, I, L)

# Plot the deflection diagram
fig = go.Figure()

fig.add_trace(go.Scatter(x=x, y=deflection, mode='lines', line=dict(color='purple', width=2), name='Deflection'))

fig.update_layout(
    title="Deflection Diagram",
    xaxis_title="Length (m)",
    yaxis_title="Deflection (m)",
    height=400,
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=True
)

fig.show()

# This is my latest code, just analyse without output code.
# for the my subsequent prompts, only provide before and after for the segment of code to be changed
# TASKS
# 1) determinate
# 2) indeterminate (2 fixed ends, > 2 supports)
# 3) Deflection diagram
# 4) UDL
# 5) intranet deployment

1) SEPARATE IN 2 TABS
2) Custom Beam Section
# 3) Database PM use book
4) Ratios to change, using small small b
5) user just input beam span, fixed and pin only
6) yield strength add in units
7) to display extracted DB properly
8) provide next similar by area and elastic modulus
# 9) how to deploy using a link
10) redo section classification
# 11) PM for GB n HY follow mine?
