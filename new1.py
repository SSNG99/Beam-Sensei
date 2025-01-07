import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import xlwings as xw
import openpyxl
import matplotlib.patches as patches
import sfd_slp as sfd

# Set page configuration
st.set_page_config(page_title="MODEC Beam Sensei", layout="wide")

# Define functions for data extraction and calculations
# def load_excel_data(filepath, database_sheet, lookup_sheet):
#     try:
#         wb = xw.Book(filepath)
#         sheet_db = wb.sheets[database_sheet]
#         sheet_lookup = wb.sheets[lookup_sheet]
#         return wb, sheet_db, sheet_lookup
#     except FileNotFoundError:
#         st.error(f"File not found: {filepath}")
#     except Exception as e:
#         st.error(f"Error loading Excel file: {e}")
#         return None, None, None
def load_excel_data(filepath, database_sheet, lookup_sheet):
    try:
        wb = openpyxl.load_workbook(filepath)
        sheet_db = wb[database_sheet]
        sheet_lookup = wb[lookup_sheet]
        return wb, sheet_db, sheet_lookup
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None, None, None
    
# Function to draw I-beam based on user inputs and add labels
def draw_static_ibeam_with_labels(height, width, flange_thickness, web_thickness):
    # Fixed dimensions for the I-beam shape
    fixed_height = 200       # Fixed height of the I-beam
    fixed_width = 150         # Fixed width (width) of the I-beam
    fixed_flange_thickness = 20  # Fixed flange thickness
    fixed_web_thickness = 20  # Fixed flange thickness
    # Create a figure with a fixed size
    fig, ax = plt.subplots(figsize=(2, 2), dpi=400)  # Static figure size, higher DPI for clear resolution
    
    # Draw static I-beam shape (fixed height, width, and flange thickness)
    # Top flange
    top_flange = patches.Rectangle((0, fixed_height - fixed_flange_thickness), fixed_width, fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Bottom flange
    bottom_flange = patches.Rectangle((0, 0), fixed_width, fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Left web
    left_web = patches.Rectangle((fixed_width / 2 - fixed_web_thickness / 2, fixed_flange_thickness), fixed_web_thickness, fixed_height - 2 * fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    
    # Add the components to the plot (I-beam parts)
    ax.add_patch(top_flange)
    ax.add_patch(bottom_flange)
    ax.add_patch(left_web)

    # Set axis limits to make the diagram more compact
    ax.set_xlim([-50, fixed_width + 100])  # Fixed margin for a more compact diagram
    ax.set_ylim([-5, fixed_height + 10])   # Fixed margin for a more compact diagram
    # Set aspect ratio to equal so the I-beam is proportional
    ax.set_aspect('equal')
    # Remove axis lines for cleaner appearance
    ax.axis('off')
    # Add dimension lines (arrows) and labels based on user input
    # Flange width dimension line (fixed)
    ax.annotate('', xy=(-8, fixed_height + 10), xytext=(fixed_width+8, fixed_height + 10), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(fixed_width / 2, fixed_height + 20, f"{width} mm", ha='center', va='center', fontsize=5, color='black')
    # Beam height dimension line (fixed)
    ax.annotate('', xy=(-30, -5), xytext=(-30, fixed_height+5), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(-40, fixed_height / 2, f"{height} mm", ha='center', va='center', fontsize=5, color='black', rotation=90)
    # Flange thickness label (top flange only)
    ax.text(fixed_width + 35, fixed_height - fixed_flange_thickness / 2, f"{flange_thickness} mm", ha='center', va='center', fontsize=5, color='black')
    # Web thickness label (shifted to the left of the web without overlap)
    ax.text(fixed_width / 2 + fixed_web_thickness + 50, fixed_height / 2, f"{web_thickness} mm (Tw)", ha='center', va='center', fontsize=5, color='black')
    # Flange thickness label (bottom flange only)
    ax.text(fixed_width + 35, fixed_flange_thickness / 2, f"{flange_thickness} mm", ha='center', va='center', fontsize=5, color='black')

    return fig

def draw_static_assyym_ibeam_with_labels(height, tfb, bfb, tft, bft, wt):
    # Fixed dimensions for the I-beam shape
    fixed_height = 200       # Fixed height of the I-beam
    if tfb > bfb:
        top_fixed_width = 150
        bottom_fixed_width = 100
        most_long = top_fixed_width
    elif tfb < bfb:
        bottom_fixed_width = 150
        top_fixed_width = 100
        most_long = bottom_fixed_width
    else:
        bottom_fixed_width = 150
        top_fixed_width = 150
        most_long = 150
    fixed_flange_thickness = 20  # Fixed flange thickness
    fixed_web_thickness = 20  # Fixed flange thickness
    # Create a figure with a fixed size
    fig, ax = plt.subplots(figsize=(2, 2), dpi=400)  # Static figure size, higher DPI for clear resolution
    
    # Draw static I-beam shape (fixed height, width, and flange thickness)
    # Top flange
    top_flange = patches.Rectangle(((most_long - top_fixed_width)/2, fixed_height - fixed_flange_thickness), top_fixed_width, fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Bottom flange
    bottom_flange = patches.Rectangle(((most_long - bottom_fixed_width)/2, 0), bottom_fixed_width, fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Left web
    left_web = patches.Rectangle((most_long / 2 - fixed_web_thickness / 2, fixed_flange_thickness), fixed_web_thickness, fixed_height - 2 * fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    
    # Add the components to the plot (I-beam parts)
    ax.add_patch(top_flange)
    ax.add_patch(bottom_flange)
    ax.add_patch(left_web)


    # Set axis limits to make the diagram more compact
    ax.set_xlim([-50, most_long + 100])  # Fixed margin for a more compact diagram
    ax.set_ylim([-20, fixed_height + 10])   # Fixed margin for a more compact diagram
    # Set aspect ratio to equal so the I-beam is proportional
    ax.set_aspect('equal')
    # Remove axis lines for cleaner appearance
    ax.axis('off')
    # Add dimension lines (arrows) and labels based on user input
    # Top Flange width dimension line (fixed)
    ax.annotate('', xy=(most_long / 2 - (top_fixed_width*1.1) / 2, fixed_height + 10), xytext=(most_long / 2 + (top_fixed_width*1.1) / 2, fixed_height + 10), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(most_long / 2, fixed_height + 20, f"{tfb} mm", ha='center', va='center', fontsize=5, color='black')


    # Bottom Flange width dimension line (fixed)
    ax.annotate('', xy=(most_long / 2 - (bottom_fixed_width*1.1) / 2, -15), xytext=(most_long / 2 + (bottom_fixed_width*1.1) / 2, -15), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
                
    ax.text(most_long / 2, -30, f"{bfb} mm", ha='center', va='center', fontsize=5, color='black')
    
    # Beam height dimension line (fixed)
    ax.annotate('', xy=(-30, -5), xytext=(-30, fixed_height+5), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(-40, fixed_height / 2, f"{height} mm", ha='center', va='center', fontsize=5, color='black', rotation=90)


    # Flange thickness label (top flange only)
    ax.text(most_long + 50, fixed_height - fixed_flange_thickness / 2, f"{tft} mm (Tft)", ha='center', va='center', fontsize=5, color='black')
    # Web thickness label (shifted to the left of the web without overlap)
    ax.text(most_long/2 + 70, fixed_height / 2, f"{wt} mm (Tw)", ha='center', va='center', fontsize=5, color='black')
    # Flange thickness label (bottom flange only)
    ax.text(most_long + 50, fixed_flange_thickness / 2, f"{bft} mm (Tfb)", ha='center', va='center', fontsize=5, color='black')

    return fig

def draw_static_boxedup_ibeam_with_labels(height, width, flange_thickness, web_thickness, oft):
    # Fixed dimensions for the I-beam shape
    fixed_height = 200       # Fixed height of the I-beam
    fixed_width = 150         # Fixed width (width) of the I-beam
    fixed_flange_thickness = 20  # Fixed flange thickness
    fixed_web_thickness = 20  # Fixed flange thickness
    # Create a figure with a fixed size
    fig, ax = plt.subplots(figsize=(2, 2), dpi=400)  # Static figure size, higher DPI for clear resolution
    
    # Draw static I-beam shape (fixed height, width, and flange thickness)
    # Top flange
    top_flange = patches.Rectangle((0, fixed_height - fixed_flange_thickness), fixed_width, fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Bottom flange
    bottom_flange = patches.Rectangle((0, 0), fixed_width, fixed_flange_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Left web
    center_web = patches.Rectangle((fixed_width / 2 - fixed_web_thickness / 2, fixed_flange_thickness), 
        fixed_web_thickness, fixed_height - 2 * fixed_flange_thickness, linewidth=1, edgecolor='black', 
        facecolor='steelblue')
    left_web = patches.Rectangle((6, fixed_flange_thickness), 
        fixed_web_thickness, fixed_height - 2 * fixed_flange_thickness, linewidth=1, edgecolor='black', 
        facecolor='steelblue')
    right_web = patches.Rectangle((fixed_width - 25, fixed_flange_thickness), 
        fixed_web_thickness, fixed_height - 2 * fixed_flange_thickness, linewidth=1, edgecolor='black', 
        facecolor='steelblue')
    
    # Add the components to the plot (I-beam parts)
    ax.add_patch(top_flange)
    ax.add_patch(bottom_flange)
    ax.add_patch(center_web)
    ax.add_patch(left_web)
    ax.add_patch(right_web)

    # Set axis limits to make the diagram more compact
    ax.set_xlim([-50, fixed_width + 100])  # Fixed margin for a more compact diagram
    ax.set_ylim([-5, fixed_height + 10])   # Fixed margin for a more compact diagram
    # Set aspect ratio to equal so the I-beam is proportional
    ax.set_aspect('equal')
    # Remove axis lines for cleaner appearance
    ax.axis('off')
    # Add dimension lines (arrows) and labels based on user input
    # Flange width dimension line (fixed)
    ax.annotate('', xy=(-8, fixed_height + 10), xytext=(fixed_width+8, fixed_height + 10), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(fixed_width / 2, fixed_height + 20, f"{width} mm", ha='center', va='center', fontsize=5, color='black')
    # Beam height dimension line (fixed)
    ax.annotate('', xy=(-30, -5), xytext=(-30, fixed_height+5), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(-40, fixed_height / 2, f"{height} mm", ha='center', va='center', fontsize=5, color='black', rotation=90)
    # Flange thickness label (top flange only)
    ax.text(fixed_width + 35, fixed_height - fixed_flange_thickness / 2, f"{flange_thickness} mm", ha='center', va='center', fontsize=5, color='black')
    # Center Web thickness label
    ax.text(fixed_width / 2, -25, f"{web_thickness} mm (Tc)", ha='center', va='center', fontsize=5, color='black')
    # Outer Web thickness label
    ax.text(fixed_width + 40, fixed_height/2, f"{oft} mm (To)", ha='center', va='center', fontsize=5, color='black')
    # Flange thickness label (bottom flange only)
    ax.text(fixed_width + 35, fixed_flange_thickness / 2, f"{flange_thickness} mm", ha='center', va='center', fontsize=5, color='black')

    return fig

def draw_static_rect_tube_with_labels(height, width, thickness):
    # Fixed dimensions for the I-beam shape
    fixed_height = 200       # Fixed height of the I-beam
    fixed_width = 150         # Fixed width (width) of the I-beam
    fixed_thickness = 20  # Fixed flange thickness
    # Create a figure with a fixed size
    fig, ax = plt.subplots(figsize=(2, 2), dpi=400)  # Static figure size, higher DPI for clear resolution
    
    # Draw static I-beam shape (fixed height, width, and flange thickness)
    # Top flange
    top_flange = patches.Rectangle((0, fixed_height - fixed_thickness), fixed_width, fixed_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # Bottom flange
    bottom_flange = patches.Rectangle((0, 0), fixed_width, fixed_thickness, linewidth=1, edgecolor='black', facecolor='steelblue')
    # web
    left_web = patches.Rectangle((0, fixed_thickness), 
        fixed_thickness, fixed_height - 2 * fixed_thickness, linewidth=1, edgecolor='black', 
        facecolor='steelblue')
    right_web = patches.Rectangle((fixed_width-fixed_thickness, fixed_thickness), 
        fixed_thickness, fixed_height - 2 * fixed_thickness, linewidth=1, edgecolor='black', 
        facecolor='steelblue')
    
    # Add the components to the plot (I-beam parts)
    ax.add_patch(top_flange)
    ax.add_patch(bottom_flange)
    ax.add_patch(left_web)
    ax.add_patch(right_web)

    # Set axis limits to make the diagram more compact
    ax.set_xlim([-50, fixed_width + 100])  # Fixed margin for a more compact diagram
    ax.set_ylim([-5, fixed_height + 10])   # Fixed margin for a more compact diagram
    # Set aspect ratio to equal so the I-beam is proportional
    ax.set_aspect('equal')
    # Remove axis lines for cleaner appearance
    ax.axis('off')
    # Add dimension lines (arrows) and labels based on user input
    # Flange width dimension line (fixed)
    ax.annotate('', xy=(-8, fixed_height + 10), xytext=(fixed_width+8, fixed_height + 10), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(fixed_width / 2, fixed_height + 20, f"{width} mm", ha='center', va='center', fontsize=5, color='black')
    # Beam height dimension line (fixed)
    ax.annotate('', xy=(-30, -5), xytext=(-30, fixed_height+5), 
                arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(-40, fixed_height / 2, f"{height} mm", ha='center', va='center', fontsize=5, color='black', rotation=90)
    # Outer Web thickness label
    ax.text(fixed_width + 40, fixed_height/2, f"{thickness} mm (T)", ha='center', va='center', fontsize=5, color='black')

    return fig

def draw_beam_with_supports_plotly(span, left_support_type, right_support_type, load_location, load_magnitude, RA, RB, MA, MB):
    # Ensure that load_location and load_magnitude are numeric (float type)
    load_location = float(load_location)
    load_magnitude = float(load_magnitude)
    
    # Define the x-coordinates for left and right supports (in meters)
    left_support_position = 0  # Left support is always at the start of the beam
    right_support_position = span  # Right support is at the end of the beam

    # Create the plot layout without axes
    layout = go.Layout(
        shapes=[
            # Draw the beam (a simple line from left to right support)
            go.layout.Shape(
                type="line", 
                x0=left_support_position, 
                y0=0, 
                x1=right_support_position, 
                y1=0, 
                line=dict(color="blue", width=4),
            ),
            # Draw left support (triangle) based on support type
            go.layout.Shape(
                type="path", 
                path=f"M {left_support_position-0.2} -0.5 L {left_support_position+0.2} -0.5 L {left_support_position} 0 Z",  
                fillcolor="yellow",
                line=dict(color="yellow", width=2),
            ) if left_support_type == "Pinned" else
            go.layout.Shape(
                type="line", 
                x0=left_support_position,
                y0=-1,
                x1=left_support_position,
                y1=1,
                line=dict(color="yellow", width=6),
            ),
            # Draw right support (triangle) based on support type
            go.layout.Shape(
                type="path", 
                path=f"M {right_support_position-0.2} -0.5 L {right_support_position+0.2} -0.5 L {right_support_position} 0 Z", 
                fillcolor="yellow",
                line=dict(color="yellow", width=2),
            ) if right_support_type == "Pinned" else
            go.layout.Shape(
                type="line", 
                x0=right_support_position,
                y0=-1,
                x1=right_support_position,
                y1=1,
                line=dict(color="yellow", width=6),
            )
        ],
        annotations=[
            dict(
                x=load_location,
                y=0,
                text=f"{load_magnitude} kN",
                font=dict(size=20, color="red"),
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-100,
            ),
            dict(
                x=left_support_position,
                y=0,
                text=f"R_L = {RA:.2f} kN\nM_L = {MA:.2f} kNm",
                font=dict(size=20, color="green"),
                showarrow=True,
                arrowhead=5,
                ax=0,
                ay=80,
            ),
            dict(
                x=right_support_position,
                y=0,
                text=f"R_R = {RB:.2f} kN\nM_R = {MB:.2f} kNm",
                font=dict(size=20, color="green"),
                showarrow=True,
                arrowhead=5,
                ax=0,
                ay=80,
            ),
        ],
        xaxis=dict(
            visible=False,
            range=[-2, span + 2],
        ),
        yaxis=dict(
            visible=False,
            range=[-1.5, 1.5],
        ),
        plot_bgcolor="white",
        showlegend=False,
        height=300,
    )
    # Create the figure with the layout
    fig = go.Figure(layout=layout)

    # Show the figure
    st.plotly_chart(fig)

def draw_static_circ_tube_with_labels(diameter, thickness):
    # Calculate the inner and outer radii
    outer_radius = diameter / 2
    inner_radius = outer_radius - thickness
    fixed_diameter = 100
    fixed_thickness = 10
    outer_radius = fixed_diameter / 2
    inner_radius = outer_radius - fixed_thickness
    # Create a figure with a fixed size
    fig, ax = plt.subplots(figsize=(2, 2), dpi=400)  # Static figure size, appropriate DPI
    # Draw the outer circle
    outer_circle = patches.Circle((0, 0), radius=outer_radius, edgecolor='black', facecolor='steelblue')
    # Draw the inner circle
    inner_circle = patches.Circle((0, 0), radius=inner_radius, edgecolor='black', facecolor='white')
    # Add the circles to the plot
    ax.add_patch(outer_circle)
    ax.add_patch(inner_circle)
    # Set the axis limits to fit the tube within the plot area
    limit = outer_radius + fixed_thickness
    ax.set_xlim(-limit - 10, limit + 10)
    ax.set_ylim(-limit - 10, limit + 10)
    
    # Set equal scaling to maintain the aspect ratio
    ax.set_aspect('equal', adjustable='box')
    # Remove axis lines for cleaner appearance
    ax.axis('off')
    # Add labels for diameter and thickness using annotations
    # Diameter label
    # ax.annotate('', xy=(-outer_radius, 0), xytext=(outer_radius, 0),
    #             arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(0, - (fixed_diameter/2 + 10), f"Diameter = {diameter} mm", ha='center', va='center', fontsize=5, color='black')
    
    # Thickness label
    # ax.annotate('', xy=(outer_radius, 0), xytext=(inner_radius, 0),
    #             arrowprops=dict(arrowstyle='<->', lw=1, color='black'))
    ax.text(0, fixed_diameter/2 + 10, f"Thickness = {thickness} mm", ha='center', va='center', fontsize=5, color='black')
    
    return fig

# def shear_force_diagram(span, load_location, load_magnitude, left_support_type, right_support_type):
#     # Step 1: Calculate reactions using static equilibrium
    
#     # Left support reaction (pinned or fixed)
#     if left_support_type == "Pinned":
#         # For pinned: reaction R_L = (P * (span - load_location)) / span
#         R_L = (load_magnitude * (span - load_location)) / span
#     elif left_support_type == "Fixed":
#         # For fixed: calculate R_L using moment and force equilibrium
#         M_L = load_magnitude * (span - load_location)  # Moment at left fixed support
#         R_L = (load_magnitude * (span - load_location)) / span + M_L / span  # Vertical reaction

#     # Right support reaction (pinned or fixed)
#     if right_support_type == "Pinned":
#         # For pinned: reaction R_R = (P * load_location) / span
#         R_R = (load_magnitude * load_location) / span
#     elif right_support_type == "Fixed":
#         # For fixed: calculate R_R using moment equilibrium
#         M_R = -load_magnitude * load_location  # Moment at right fixed support
#         R_R = (load_magnitude * load_location) / span + M_R / span  # Vertical reaction

#     # Step 2: Define the x-coordinates along the beam
#     x_points = np.linspace(0, span, 1000)
#     shear_forces = []

#     # Step 3: Calculate shear force at each point along the beam
#     for x in x_points:
#         if x < load_location:
#             # Before the load, the shear force is influenced by the left support's reaction R_L
#             shear_force = R_L
#         elif x == load_location:
#             # At the load, the shear force has a discontinuity due to the applied load
#             shear_force = R_L - load_magnitude
#         else:
#             # After the load, the shear force is influenced by both reactions R_L and R_R
#             shear_force = R_L - load_magnitude

#         shear_forces.append(shear_force)


#     # Create the figure for the Shear Force Diagram
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=x_points, 
#         y=shear_forces, 
#         mode='lines', 
#         line=dict(color="blue", width=4),
#         name="Shear Force",
#     ))

#     # Customize layout for the shear force diagram
#     fig.update_layout(
#         title="Shear Force Diagram",
#         xaxis=dict(
#             title="Beam Length (m)", 
#             range=[0, span+0.2],
#             zeroline=True, 
#             zerolinecolor="black", 
#             showgrid=True,
#         ),
#         yaxis=dict(
#             title="Shear Force (kN)", 
#             rangemode="tozero", 
#             showgrid=True,
#             zeroline=True, 
#             zerolinecolor="black", 
#         ),
#         plot_bgcolor="white",
#         showlegend=False,
#         height=400,  
#         margin=dict(t=20, b=40, l=50, r=20),
#     )

#     return fig

# def bending_moment_diagram(span, load_location, load_magnitude, left_support_type, right_support_type):
    
#     # Initialize variables
#     M_L = 0  # Moment at left support (initially 0 or calculated for fixed support)
#     M_R = 0  # Moment at right support (initially 0 or calculated for fixed support)
#     R_L = 0  # Reaction at left support (initially 0)
#     R_R = 0  # Reaction at right support (initially 0)
    
#     # Calculate reactions at the supports (R_L and R_R)
#     if left_support_type == "Pinned":
#         R_L = (load_magnitude * (span - load_location)) / span
#     else:  # Left support is fixed
#         R_L = (load_magnitude * (span - load_location)) / span
#         M_L = load_magnitude * (span - load_location)  # Moment at left fixed support
        
#     if right_support_type == "Pinned":
#         R_R = (load_magnitude * load_location) / span
#     else:  # Right support is fixed
#         R_R = (load_magnitude * load_location) / span
#         M_R = -load_magnitude * load_location  # Moment at right fixed support

#     # Define the x-coordinates along the beam (splitting into smaller steps)
#     x_points = np.linspace(0, span, 1000)
#     bending_moments = []

#     # Calculate bending moments at each point
#     for x in x_points:
#         if x < load_location:
#             # Before the load, the bending moment increases linearly from the left support
#             M = M_L + R_L * x
#         elif x == load_location:
#             # At the load location, the moment has a discontinuity due to the applied load
#             M = M_L + R_L * load_location
#         else:
#             # After the load, the bending moment decreases linearly
#             M = M_R + R_L * load_location - R_R * (x - load_location)
#         bending_moments.append(M)

#     # Create the figure for the Bending Moment Diagram
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=x_points, 
#         y=bending_moments, 
#         mode='lines', 
#         line=dict(color="blue", width=4),
#         name="Bending Moment",
#     ))

#     # Customize layout for the bending moment diagram
#     fig.update_layout(
#         title="Bending Moment Diagram",
#         xaxis=dict(
#             title="Beam Length (m)", 
#             range=[0, span+0.2],
#             zeroline=True, 
#             zerolinecolor="black", 
#             showgrid=True,
#         ),
#         yaxis=dict(
#             title="Bending Moment (kNm)", 
#             rangemode="tozero", 
#             showgrid=True,
#             zeroline=True, 
#             zerolinecolor="black", 
#         ),
#         plot_bgcolor="white",
#         showlegend=False,
#         height=400, 
#         margin=dict(t=20, b=40, l=50, r=20),
#     )

#     return fig

# Function to draw beam with shear force diagram
def draw_beam_with_shear_force_and_bending_moment(span, left_support_type, right_support_type, load_location, load_magnitude):
    # Draw the beam with supports (from your previous function)
    RA, RB, MA, MB = sfd.calculate_supports(span, load_location, load_magnitude, left_support_type, right_support_type)
    draw_beam_with_supports_plotly(span, left_support_type, right_support_type, load_location, load_magnitude, RA, RB, MA, MB)
    st.write(f'Reaction force at left support (RA): {RA:.2f} N')
    st.write(f'Reaction force at right support (RB): {RB:.2f} N')

    if left_support_type == 'Fixed':
        st.write(f'Moment at left support (MA): {MA:.2f} Nm')
    else:
        st.write(f'Moment at left support (MA): 0 Nm')

    if right_support_type == 'Fixed':
        st.write(f'Moment at right support (MB): {MB:.2f} Nm')
    else:
        st.write(f'Moment at right support (MB): 0 Nm')
    # Calculate SFD
    x, V = sfd.shear_force_diagram(span, load_location, load_magnitude, RA, RB)
    # Plot SFD
    sfd.plot_sfd(x, V)

    x_bmd, M = sfd.bending_moment_fixed_fixed(span, load_location, load_magnitude, RA, MA, RB, MB)
    # Plot BMD
    sfd.plot_bmd(x_bmd, M)
    # # Generate and show the shear force diagram
    # sfd_fig = shear_force_diagram(span, load_location, load_magnitude, left_support_type, right_support_type)
    # sfd_fig.update_layout(margin=dict(t=20, b=20, l=40, r=40))  # Adjust margins for the shear force diagram
    # st.plotly_chart(sfd_fig, use_container_width=True)  # Show Shear Force Diagram
    # # Generate and show the bending moment diagram
    # bmd_fig = bending_moment_diagram(span, load_location, load_magnitude, left_support_type, right_support_type)
    # bmd_fig.update_layout(margin=dict(t=20, b=20, l=40, r=40))  # Adjust margins for the bending moment diagram
    # st.plotly_chart(bmd_fig, use_container_width=True)  # Show Bending Moment Diagram

# Main function to build the Streamlit app
def main():
    st.markdown("""
    <style>
        .title {
            margin-top: -65px;  /* Adjust space above title */
            font-size: 50px;     /* Adjust text size */
            font-weight: bold;   /* Optional: Make the text bold */
        }
    </style>
    <h1 class="title">MODEC Beam Sensei</h1>
""", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Section Library", "Custom Beam", "Beam Analyzer"])
    with st.container():
        # Use two columns for layout
        left_col, right_col = t1.columns([2, 5])  # 3 parts left, 1 part right for diagrams
        left2_col, right2_col = t2.columns([2, 7])
        left3_col, right3_col = t3.columns([1, 3])
        # Load Workbook
        excel_file = "000_Steel Section Library1.xlsx"
        wb, sheet_db, sheet_lookup = load_excel_data(excel_file, "Database", "Beam_Check")
        if not wb:
                st.error("Excel file could not be loaded.")
                return
        # Left Panel: Beam Input Section
        with left_col:
            # Beam_Type = sheet_db('A4:A1021').value
            Beam_Type = [sheet_db[f"{'A'}{row}"].value for row in range(4, 1021 + 1)]
            Beam_Selection = st.selectbox("Select Beam Type:", Beam_Type, index=0)
            # Similarity_Type = sheet_db('AW28:AW29').value
            Similarity_Type = [sheet_db[f'{'AW'}{row}'].value for row in range(28, 29 + 1)]
            Similarity_Selection = st.selectbox("Select Similarity Type:", Similarity_Type, index=0)
            # Yield_Strength = sheet_db('AR21:AR25').value
            Yield_Strength = [sheet_db[f'{'AR'}{row}'].value for row in range(21, 25 + 1)]
            Yield_Strength_Selection = st.selectbox("Select Yield Strength (MPa):", Yield_Strength, index=0)

            if st.button("Generate properties from Database"):
                try:
                    sheet_lookup['C12'].value = Beam_Selection
                    sheet_lookup['C14'].value = Similarity_Selection
                    # wb.save()
                    wb.save(excel_file)
                    # Generate the I-beam diagram when button is pressed
                    fig = draw_static_ibeam_with_labels(sheet_lookup['E19'].value, sheet_lookup['E20'].value, sheet_lookup['E21'].value, sheet_lookup['E22'].value)
                    st.pyplot(fig)
                    with right_col:
                        a, b = st.columns([1,1])
                        with a:
                            st.write(f"Alt. Std. 1: {sheet_lookup['L12'].value}")
                        with b:
                            st.write(f"Alt. Std. 2: {sheet_lookup['L13'].value}")
                        df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:J', header=16, nrows=21)
                        df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3"]
                        # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                        df = df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                        # Display the DataFrame with `st.table()`
                        st.table(df)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        with left2_col:
            # Streamlit UI
            # st.markdown('<h1 style="font-size: 20px;">Static I-Beam Diagram with Dynamic Labels</h1>', unsafe_allow_html=True)
            beam_type_selection = st.selectbox("Select Beam Type:", ["Symmetric I-Beam", "Assymmetric I-Beam", "Boxed Up I-Beam", "Rectangular Tube", "Circular Tube"])
            # Display input fields based on the selected beam type
            if beam_type_selection == "Symmetric I-Beam":
                a, b = st.columns([1, 1])
                with a:
                    height = st.number_input("Height (mm)", min_value=100, max_value=2000, value=200)
                    width = st.number_input("Width (mm)", min_value=50, max_value=1000, value=150)
                with b:
                    flange_thickness = st.number_input("Tf (mm)", min_value=1, max_value=200, value=20)
                    web_thickness = st.number_input("Tw (mm)", min_value=1, max_value=100, value=20)
                # Yield_Strength = sheet_db.range('AR21:AR25').value
                Yield_Strength = [sheet_db[f'{'AR'}{row}'].value for row in range(21, 25 + 1)]
                Yield_Strength_Selection = st.selectbox("Select Yield Strength (MPa): ", Yield_Strength, index=0)
    
            elif beam_type_selection == "Assymmetric I-Beam":
                a, b = st.columns([1, 1])
                with a:
                    depth = st.number_input("Depth (mm)", min_value=50, max_value=5000, value=200)
                    top_flange_breadth = st.number_input("Top flange breadth (mm)", min_value=50, max_value=5000, value=150)
                    bottom_flange_breadth = st.number_input("Bottom flange breadth (mm)", min_value=50, max_value=5000, value=100)
                with b:
                    top_flange_thickness = st.number_input("Top flange thickness (mm)", min_value=5, max_value=100, value=20)
                    bottom_flange_thickness = st.number_input("Bottom flange thickness (mm)", min_value=5, max_value=100, value=10)
                    web_thickness = st.number_input("Web thickness (mm)", min_value=5, max_value=100, value=20)
                # Yield_Strength = sheet_db.range('AR21:AR25').value
                Yield_Strength = [sheet_db[f'{'AR'}{row}'].value for row in range(21, 25 + 1)]
                Yield_Strength_Selection = st.selectbox("Select Yield Strength (MPa): ", Yield_Strength, index=0)

            elif beam_type_selection == "Boxed Up I-Beam":
                a, b = st.columns([1, 1])
                with a:
                    depth = st.number_input("Depth (mm)", min_value=50, max_value=5000, value=200)
                    flange_breadth = st.number_input("Flange breadth (mm)", min_value=50, max_value=5000, value=150)
                    flange_thickness = st.number_input("Flange thickness (mm)", min_value=5, max_value=100, value=20)
                with b:
                    center_web_thickness = st.number_input("Center web thickness (mm)", min_value=5, max_value=100, value=10)
                    outer_web_thickness = st.number_input("Outer web thickness (mm)", min_value=5, max_value=100, value=20)

            elif beam_type_selection == "Rectangular Tube":
                depth = st.number_input("Depth (mm)", min_value=50, max_value=5000, value=200)
                breadth = st.number_input("Breadth (mm)", min_value=50, max_value=5000, value=150)
                thickness = st.number_input("Thickness (mm)", min_value=5, max_value=100, value=20)

            elif beam_type_selection == "Circular Tube":
                diameter = st.number_input("Diameter (mm)", min_value=50, max_value=1000, value=200)
                thickness = st.number_input("Thickness (mm)", min_value=5, max_value=1000, value=10)

            # Similarity_Type = sheet_db.range('AW28:AW29').value
            Similarity_Type = [sheet_db[f'{'AW'}{row}'].value for row in range(28, 29 + 1)]
            Similarity_Selection = st.selectbox("Select Similarity Type: ", Similarity_Type, index=0)
            
            # Button to generate the diagram
            generate_button = st.button("Generate Properties")
            if generate_button:
                # Depending on the selected beam type, call the appropriate function to generate the diagram
                if beam_type_selection == "Symmetric I-Beam":
                    try:
                        sheet_lookup['E42'].value = height
                        sheet_lookup['E43'].value = width
                        sheet_lookup['E44'].value = flange_thickness
                        sheet_lookup['E45'].value = web_thickness
                        sheet_lookup['C47'].value = Similarity_Selection
                        sheet_lookup['C48'].value = Yield_Strength_Selection
                        # Save other properties to the Excel sheet
                        wb.save(excel_file)
                        fig = draw_static_ibeam_with_labels(height, width, flange_thickness, web_thickness)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Failed to save data to Excel: {e}")
                    
                    with right2_col:
                        a, b, c = st.columns([1, 1, 1])
                        with a:
                            st.write(f"Alt. Std. 1: {sheet_lookup['L42'].value}")
                        with b:
                            st.write(f"Alt. Std. 2: {sheet_lookup['L43'].value}")
                        with c:
                            st.write(f"Alt. Std. 3: {sheet_lookup['L44'].value}")
                        
                        df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:L', header=48, nrows=21)
                        df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3","Alt. Std. 3", "4"]
                        # st.dataframe(df, height = 740, use_container_width=True)
                        # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                        df = df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                        # Display the DataFrame with `st.table()`
                        st.table(df)

                elif beam_type_selection == "Assymmetric I-Beam":
                    try:
                        sheet_lookup['E74'].value = depth
                        sheet_lookup['E75'].value = top_flange_breadth
                        sheet_lookup['E76'].value = bottom_flange_breadth
                        sheet_lookup['E77'].value = top_flange_thickness
                        sheet_lookup['E78'].value = bottom_flange_thickness
                        sheet_lookup['E79'].value = web_thickness
                        sheet_lookup['C81'].value = Similarity_Selection
                        sheet_lookup['C82'].value = Yield_Strength_Selection
                        # Save other properties to the Excel sheet
                        wb.save(excel_file)
                        fig = draw_static_assyym_ibeam_with_labels(depth, top_flange_breadth, bottom_flange_breadth, top_flange_thickness, bottom_flange_thickness, web_thickness)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Failed to save data to Excel: {e}")
                    
                    with right2_col:
                        a, b, c = st.columns([1, 1, 1])
                        with a:
                            st.write(f"Alt. Std. 1: {sheet_lookup['L74'].value}")
                        with b:
                            st.write(f"Alt. Std. 2: {sheet_lookup['L75'].value}")
                        with c:
                            st.write(f"Alt. Std. 3: {sheet_lookup['L76'].value}")
                        
                        df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:L', header=82, nrows=23)
                        df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3","Alt. Std. 3", "4"]
                        # st.dataframe(df, height = 740, use_container_width=True)
                        # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                        df = df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                        # Display the DataFrame with `st.table()`
                        st.table(df)

                elif beam_type_selection == "Boxed Up I-Beam":
                    try:
                        sheet_lookup['E110'].value = depth
                        sheet_lookup['E111'].value = flange_breadth
                        sheet_lookup['E112'].value = flange_thickness
                        sheet_lookup['E113'].value = center_web_thickness
                        sheet_lookup['E114'].value = outer_web_thickness
                        sheet_lookup['C116'].value = Similarity_Selection
                        # Save other properties to the Excel sheet
                        wb.save(excel_file)
                        fig = draw_static_boxedup_ibeam_with_labels(depth, flange_breadth, flange_thickness, center_web_thickness, outer_web_thickness)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Failed to save data to Excel: {e}")
                    
                    with right2_col:
                        a, b, c = st.columns([1, 1, 1])
                        with a:
                            st.write(f"Alt. Std. 1: {sheet_lookup['L110'].value}")
                        with b:
                            st.write(f"Alt. Std. 2: {sheet_lookup['L111'].value}")
                        with c:
                            st.write(f"Alt. Std. 3: {sheet_lookup['L112'].value}")
                        
                        df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:L', header=117, nrows=22)
                        df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3","Alt. Std. 3", "4"]
                        # st.dataframe(df, height = 740, use_container_width=True)
                        # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                        df = df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                        # Display the DataFrame with `st.table()`
                        st.table(df)

                elif beam_type_selection == "Rectangular Tube":
                    try:
                        sheet_lookup['E144'].value = depth
                        sheet_lookup['E145'].value = breadth
                        sheet_lookup['E146'].value = thickness
                        sheet_lookup['C148'].value = Similarity_Selection
                        # Save other properties to the Excel sheet
                        wb.save(excel_file)
                        fig = draw_static_rect_tube_with_labels(depth, breadth, thickness)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Failed to save data to Excel: {e}")
                    
                    with right2_col:
                        a, b, c = st.columns([1, 1, 1])
                        with a:
                            st.write(f"Alt. Std. 1: {sheet_lookup['L144'].value}")
                        with b:
                            st.write(f"Alt. Std. 2: {sheet_lookup['L145'].value}")
                        with c:
                            st.write(f"Alt. Std. 3: {sheet_lookup['L146'].value}")
                        
                        df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:L', header=149, nrows=22)
                        df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3","Alt. Std. 3", "4"]
                        # st.dataframe(df, height = 740, use_container_width=True)
                        # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                        df = df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                        # Display the DataFrame with `st.table()`
                        st.table(df)

                elif beam_type_selection == "Circular Tube":
                    try:
                        sheet_lookup['E175'].value = diameter
                        sheet_lookup['E176'].value = thickness
                        sheet_lookup['C178'].value = Similarity_Selection
                        # Save other properties to the Excel sheet
                        wb.save(excel_file)
                        fig = draw_static_circ_tube_with_labels(diameter, thickness)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Failed to save data to Excel: {e}")
                    
                    with right2_col:
                        a, b, c = st.columns([1, 1, 1])
                        with a:
                            st.write(f"Alt. Std. 1: {sheet_lookup['L175'].value}")
                        with b:
                            st.write(f"Alt. Std. 2: {sheet_lookup['L176'].value}")
                        with c:
                            st.write(f"Alt. Std. 3: {sheet_lookup['L177'].value}")
                        
                        df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:L', header=179, nrows=23)
                        df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3","Alt. Std. 3", "4"]
                        # st.dataframe(df, height = 740, use_container_width=True)
                        # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                        df = df.map(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                        # Display the DataFrame with `st.table()`
                        st.table(df)

                    
    
        with left3_col:
            # st.subheader("BEAM CONDITION INITIALIZATION")
            st.markdown('<h1 style="font-size: 24px;">Beam Initialisation</h1>', unsafe_allow_html=True)
            span = st.number_input("Beam Span (in meters):", min_value=1.0, value=5.0)  # Default value 5 meters
            load_magnitude = st.number_input("Load Magnitude (in kN):", min_value=1.0, value=5.0)  # Default value 5 kN
            load_location = st.number_input("Load distance from left support (in meters):", min_value=1.0, value=2.5)  # Default value 2.5m
            # Left beam support
            left_support_type = st.radio(
            "Left End Support",
            options=["Pinned", "Fixed"],
            index=0,  # Default selection, you can change if you prefer
            horizontal=True)
            # Right beam support
            right_support_type = st.radio(
            "Right End Support",
            options=["Pinned", "Fixed"],
            index=0,  # Default selection, you can change if you prefer
            horizontal=True)
            
            generate_button = st.button("Generate Diagrams", key="generate_button_tab3")

    # Add some space between the top and bottom section
    st.markdown("<hr>", unsafe_allow_html=True)
 
    if generate_button:
        with right3_col:
            # Draw the beam with supports (from your previous function)
            st.markdown('<h1 style="font-size: 24px;">Beam Diagram with Supports and Load</h1>', unsafe_allow_html=True)
            RA, RB, MA, MB = sfd.calculate_supports(span, load_location, load_magnitude, left_support_type, right_support_type)
            draw_beam_with_supports_plotly(span, left_support_type, right_support_type, load_location, load_magnitude, RA, RB, -MA, MB)
            a, b = st.columns([2, 1])
            with a:
                st.markdown('<h1 style="font-size: 24px;">Reactions and Moments Summary:</h1>', unsafe_allow_html=True)
                sfd.display_summary_table(RA, RB, MA, MB)
        with t3.container():  
            left_sfd, right_bmd = st.columns([1,1])
            with left_sfd:
                # Calculate SFD
                x, V = sfd.shear_force_diagram(span, load_location, load_magnitude, RA, RB)
                # Plot SFD
                sfd.plot_sfd(x, V)
            with right_bmd:
                # # # Choose the correct BMD function based on support configuration
                if left_support_type == 'Fixed' or right_support_type == 'Fixed':
                    x_bmd, M = sfd.bending_moment_fixed_fixed(span, load_location, load_magnitude, RA, MA, RB, MB)
                else:
                    x_bmd, M = sfd.bending_moment_diagram(span, load_location, load_magnitude, RA)
                # Plot BMD
                sfd.plot_bmd(x_bmd, M)
                
if __name__ == "__main__":
    main()
