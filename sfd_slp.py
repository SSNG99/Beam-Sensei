import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Define default values for Elastic Modulus (E) and Moment of Inertia (I)
E = 210e9  # Pa (N/m^2)
I = 5e-6  # m^4

# Function to calculate moments and shear forces
def calculate_supports(span, load_location, load_magnitude, left_support_type, right_support_type):
    L = span
    a = load_location
    b = L - a
    P = load_magnitude *1000
    
    # Initialize reactions at supports.
    RA = RB = 0
    MA = MB = 0
    
    if left_support_type == 'Pinned' and right_support_type == 'Pinned':
        # Both ends are pinned
        RA = P * b / L
        RB = P * a / L
        MA = MB = 0

    elif left_support_type == 'Pinned' and right_support_type == 'Fixed':
        # Calculate moment at right fixed support (MA)
        # MB = calculate_moment_at_fixed(load_magnitude, span)
        MB = (P / L**2) * (a**2 * b + ((b**2 * a) / 2))
        # Calculate reaction at left fixed support (RA) and right pinned support (RB)
        RA = (P * (L - a) - MB) / L
        RB = P - RA
        MB = MB * -1
        MA = 0  # Moment at the pinned support is zero.

    elif left_support_type == 'Fixed' and right_support_type == 'Pinned':
        # Calculate moment at right fixed support (MA)
        MA = (P / L**2) * (b**2 * a + ((a**2 * b) / 2))
        # Calculate reaction at left fixed support (RA) and right pinned support (RB)
        RB = (P * (L - b) - MA) / L
        RA = P - RB
        MB = 0  # Moment at the pinned support is zero.

    elif left_support_type == 'Fixed' and right_support_type == 'Fixed':
        # Both ends are fixed
        RA = (P * b**2 * (3*L - 2*b)) / L**3
        RB = (P * a**2 * (3*L - 2*a)) / L**3
        MA = P * a * b**2 / L**2
        MB = -P * b * a**2 / L**2

    return RA, RB, MA, MB

# Function to calculate SFD and BMD
def shear_force_diagram(L, a, P, RA, RB):
    x = np.linspace(0, L, 500)
    V = np.piecewise(x, [x < a, x >= a], [RA, -RB])

    return x, V

def bending_moment_diagram(L, a, P, RA):
    P *= 1000
    x = np.linspace(0, L, 500)
    M = np.piecewise(x, 
                     [x < a, x >= a], 
                     [lambda x: RA * x, 
                      lambda x: RA * x - (P * (x - a))])
    return x, M

# Function to calculate Bending Moment Diagram for Fixed-Fixed
def bending_moment_fixed_fixed(L, a, P, RA, MA, RB, MB):
    x = np.linspace(0, L, 500)
    M = np.piecewise(x, [x < a, x >= a], 
                     [lambda x: -MA + RA * x, lambda x: MB - RB * (x - L)])
    return x, M

# Function to plot SFD
def plot_sfd(x, V, figsize=(10, 5)):
    # Create a figure using plotly
    fig = go.Figure()

    # Add line trace for the Shear Force Diagram
    fig.add_trace(go.Scatter(
        x=x,
        y=V,
        mode='markers+lines',
        name='Shear Force Diagram',
        line=dict(color='blue'),
        marker=dict(symbol='circle'),
        hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>',
        # Adjust hover label positioning slightly away from the point
        hoverlabel=dict(
        bgcolor='white',  # background color of the hover label
        bordercolor='black',  # border color of the hover label
        font=dict(family='Arial', size=12, color='black'),  # font properties
        align='left',  # text alignment
        namelength=0,),  # Do not display trace name in the hover
        # Move the hover text slightly away from the point by using `textposition`
        textposition="top right",)  # Move the hover text above the point
    )

    # Add fill between for positive values (yellow)
    fig.add_trace(go.Scatter(
        x=x,
        y=[value if value >= 0 else 0 for value in V],  # Keep positive values, set negative values to 0
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(255, 255, 0, 0.5)',  # Semi-transparent yellow
        line=dict(width=0),
        name='Positive Area'
    ))

    # Add fill between for negative values (red)
    fig.add_trace(go.Scatter(
        x=x,
        y=[value if value < 0 else 0 for value in V],  # Keep negative values, set positive values to 0
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(255, 0, 0, 0.5)',  # Semi-transparent red
        line=dict(width=0),
        name='Negative Area'
    ))

    # Add zero line
    fig.add_trace(go.Scatter(
        x=[min(x), max(x)],
        y=[0, 0],
        mode='lines',
        line=dict(color='black', width=3),
        name='Zero Line'
    ))

    # Update layout for titles and labels
    fig.update_layout(
        title='Shear Force Diagram',
        title_font=dict(size=24), 
        xaxis_title='Distance along the beam (m)',
        yaxis_title='Shear Force (N)',
        showlegend=False,
        template='plotly_white',  # Optional, for a white background
        width=figsize[0] * 100,  # Width in pixels (e.g., 10 * 100 = 1000px)
        height=figsize[1] * 100,  # Height in pixels (e.g., 5 * 100 = 500px)
        xaxis=dict(showgrid=True,
            gridcolor='black',
            gridwidth=0.5,         
            griddash='solid',
            showline=True,       # Show the x-axis line
            linewidth=3,         # Increase the line width (bold)
            linecolor='black',   # Color of the axis line  
            ),
        yaxis=dict(showgrid=True,
            gridcolor='black',
            gridwidth=0.5,         
            griddash='solid',
            showline=True,       # Show the x-axis line
            linewidth=3,         # Increase the line width (bold)
            linecolor='black', ),
        # hovermode='closest'
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)

# Function to plot Bending Moment Diagram (BMD)
def plot_bmd(x, M, figsize=(10, 5)):
    fig = go.Figure()
    # Plotting the bending moment diagram
    fig.add_trace(go.Scatter(x=x, y=M, mode='lines+markers', 
    name='Bending Moment Diagram', 
    line=dict(color='green'),
    hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>',
    # Adjust hover label positioning slightly away from the point
    hoverlabel=dict(
        bgcolor='white',  # background color of the hover label
        bordercolor='black',  # border color of the hover label
        font=dict(family='Arial', size=12, color='black'),  # font properties
        align='left',  # text alignment
        namelength=0,),  # Do not display trace name in the hover
    # Move the hover text slightly away from the point by using `textposition`
    textposition="top right",)  # Move the hover text above the point
    )
    # Adding fill between for positive and negative values
    fig.add_trace(go.Scatter(x=x, y=[value if value > 0 else 0 for value in M], 
        mode='lines', fill='tozeroy', 
        fillcolor='rgba(255,255,0,0.5)', 
        line=dict(color='rgba(255,255,0,0.5)')))
    fig.add_trace(go.Scatter(x=x, y=[value if value < 0 else 0 for value in M], 
        mode='lines', fill='tozeroy', 
        fillcolor='rgba(255,0,0,0.5)', 
        line=dict(color='rgba(255,0,0,0.5)')))
    # Add zero line
    fig.add_trace(go.Scatter(
        x=[min(x), max(x)],
        y=[0, 0],
        mode='lines',
        line=dict(color='black', width=3),
        name='Zero Line'
    ))
        # Identify maximum and minimum bending moment values and their corresponding x-values
    max_m = max(M)
    max_x = x[np.argmax(M)]  # x value corresponding to maximum bending moment

    # Add annotations for maximum and minimum points
    fig.add_annotation(
        x=max_x,
        y=max_m,
        text=f'Max: {max_m:.0f} Nm, {max_x:.1f} m ',
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50,
        font=dict(size=12, color="black"),
        bgcolor="yellow",
        borderpad=4
    )
    # Adding labels and title
    fig.update_layout(
        title='Bending Moment Diagram',
        title_font=dict(size=24), 
        xaxis_title='Distance along the beam (m)',
        yaxis_title='Bending Moment (Nm)',
        showlegend=False,
        width=figsize[0] * 100,  # Width in pixels (e.g., 10 * 100 = 1000px)
        height=figsize[1] * 100,  # Height in pixels (e.g., 5 * 100 = 500px)
        xaxis=dict(showgrid=True,
            gridcolor='black',
            gridwidth=0.5,       
            griddash='solid',
            showline=True,       # Show the x-axis line
            linewidth=3,         # Increase the line width (bold)
            linecolor='black',   # Color of the axis line  
            ),
        yaxis=dict(showgrid=True,
            gridcolor='black',
            gridwidth=0.5,         
            griddash='solid',
            showline=True,       # Show the x-axis line
            linewidth=3,         # Increase the line width (bold)
            linecolor='black', ),
    )
    st.plotly_chart(fig)

def display_summary_table(RA, RB, MA, MB):
    # st.write("### Reactions and Moments Summary:")
    table_data = {
        "Location (m)": ["Left Support", "Right Support"],
        "Reaction Force (N)": [f"{RA:.2f}",f"{-RB:.2f}"],
        "Moment (Nm)": [f"{-MA:.2f}",f"{MB:.2f}"],
    }
    st.table(table_data)
# # Streamlit UI setup
# st.title('Shear Force Diagram (SFD) using Moment Distribution Method')

# span = st.number_input('Enter the span length of the beam (m):', value=10.0, step=0.1)
# load_location = st.number_input('Enter the location of the load from the left support (m):', value=5.0, step=0.1)
# load_magnitude = st.number_input('Enter the magnitude of the point load (N):', value=1000.0, step=10.0)
# left_support_type = st.selectbox('Select the type of the left support:', ('Pinned', 'Fixed'))
# right_support_type = st.selectbox('Select the type of the right support:', ('Pinned', 'Fixed'))

# # Compute support reactions and moments
# RA, RB, MA, MB = calculate_supports(span, load_location, load_magnitude, left_support_type, right_support_type)

# st.write(f'Reaction force at left support (RA): {RA:.2f} N')
# st.write(f'Reaction force at right support (RB): {RB:.2f} N')

# if left_support_type == 'Fixed':
#     st.write(f'Moment at left support (MA): {MA:.2f} Nm')
# else:
#     st.write(f'Moment at left support (MA): 0 Nm')

# if right_support_type == 'Fixed':
#     st.write(f'Moment at right support (MB): {MB:.2f} Nm')
# else:
#     st.write(f'Moment at right support (MB): 0 Nm')

# # Calculate SFD
# x, V = shear_force_diagram(span, load_location, load_magnitude, RA, RB)
# # Plot SFD
# plot_sfd(x, V)

# # # Choose the correct BMD function based on support configuration
# # if left_support_type == 'Fixed' and right_support_type == 'Fixed':
# #     x_bmd, M = bending_moment_fixed_fixed(span, load_location, load_magnitude, RA, MA, RB, MB)
# # else:
# #     x_bmd, M = bending_moment_diagram(span, load_location, load_magnitude, RA)
# x_bmd, M = bending_moment_fixed_fixed(span, load_location, load_magnitude, RA, MA, RB, MB)
# # Plot BMD
# plot_bmd(x_bmd, M)

# D4: Depth of the I-beam
# E4: Breadth of the top flange
# F4: Breadth of the bottom flange
# G4: Thickness of the top flange
# H4: Thickness of the bottom flange
# I4: Thickness of the web

# deduce a single line excel formula using the formula above, using cell references only