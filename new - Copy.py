import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import xlwings as xw
import matplotlib.patches as patches

# Set page configuration
st.set_page_config(page_title="Beam Analysis Tool", layout="wide")

# Define functions for data extraction and calculations
def load_excel_data(filepath, database_sheet, lookup_sheet):
    try:
        wb = xw.Book(filepath)
        sheet_db = wb.sheets[database_sheet]
        sheet_lookup = wb.sheets[lookup_sheet]
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
    ax.text(fixed_width / 2 - fixed_web_thickness - 20, fixed_height / 2, f"{web_thickness} mm", ha='center', va='center', fontsize=5, color='black')

    # Flange thickness label (bottom flange only)
    ax.text(fixed_width + 35, fixed_flange_thickness / 2, f"{flange_thickness} mm", ha='center', va='center', fontsize=5, color='black')

    return fig

def draw_beam_with_supports_plotly(span, left_support_type, right_support_type, load_location, load_magnitude):
    # Ensure that load_location and load_magnitude are numeric (float type)
    load_location = float(load_location)
    load_magnitude = float(load_magnitude)
    # Define the x-coordinates for left and right supports (in meters)
    left_support_position = 0  # Left support is always at the start of the beam
    right_support_position = span  # Right support is at the end of the beam
    # Calculate reaction forces (assuming a simply supported beam with a point load)
    R_L = load_magnitude * (span - load_location) / span  # Reaction at left support
    R_R = load_magnitude * load_location / span  # Reaction at right support

    # Create the plot layout without axes
    layout = go.Layout(
        title="Beam Diagram with Supports and Load",
        shapes=[
            # Draw the beam (a simple line from left to right support)
            go.layout.Shape(
                type="line",  # The shape type
                x0=left_support_position,  # Starting x-coordinate (left support)
                y0=0,  # Starting y-coordinate (for simplicity, assume y=0)
                x1=right_support_position,  # Ending x-coordinate (right support)
                y1=0,  # Ending y-coordinate
                line=dict(color="blue", width=4),  # Line properties
            ),
            # Draw left support (triangle) based on support type
            # If left support is pinned, draw a triangle (upward)
            go.layout.Shape(
                type="path",  # Using a custom path to create a triangle for pinned support
                path=f"M {left_support_position-0.2} -0.5 L {left_support_position+0.2} -0.5 L {left_support_position} 0 Z",  # Triangle path
                fillcolor="yellow",
                line=dict(color="yellow", width=2),
            ) if left_support_type == "Pinned" else
            # Draw left fixed support (vertical wall)
            go.layout.Shape(
                type="line",  # Fixed support as a vertical wall
                x0=left_support_position,
                y0=-1,
                x1=left_support_position,
                y1=1,  # Height of the wall
                line=dict(color="yellow", width=6),
            ),
            # Draw right support (triangle) based on support type
            # If right support is pinned, draw a triangle (upward)
            go.layout.Shape(
                type="path",  # Using a custom path to create a triangle for pinned support
                path=f"M {right_support_position-0.2} -0.5 L {right_support_position+0.2} -0.5 L {right_support_position} 0 Z",  # Triangle path
                fillcolor="yellow",
                line=dict(color="yellow", width=2),
            ) if right_support_type == "Pinned" else
            # Draw right fixed support (vertical wall)
            go.layout.Shape(
                type="line",  # Fixed support as a vertical wall
                x0=right_support_position,
                y0=-1,
                x1=right_support_position,
                y1=1,  # Height of the wall
                line=dict(color="yellow", width=6),
            )
        ],
        annotations=[
            # Annotate the load magnitude at its location
            dict(
                x=load_location,
                y=0,  # Place text just below the arrow
                text=f"{load_magnitude} kN",
                font=dict(size=20, color="red"),
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-100,
            ),
            dict(
                x=left_support_position,
                y=0,  # Position above the left support
                text=f"R_L = {R_L:.2f} kN",
                font=dict(size=20, color="green"),
                showarrow=True,
                arrowhead=5,
                ax=0,
                ay=80,
            ),
            dict(
                x=right_support_position,
                y=0,  # Position above the right support
                text=f"R_R = {R_R:.2f} kN",
                font=dict(size=20, color="green"),
                showarrow=True,
                arrowhead=5,
                ax=0,
                ay=80,
            ),
        ],
        # Hide axes, grid, ticks, and background color
        xaxis=dict(
            visible=False,  # Hide x-axis
            range=[-2 , span + 2],
        ),
        yaxis=dict(
            visible=False,  # Hide y-axis
            range=[-1.5, 1.5],
        ),
        plot_bgcolor="white",  # Set background to white
        showlegend=False,  # Hide legend
        height=300,
    )
    # Create the figure with the layout
    fig = go.Figure(layout=layout)

    # Show the figure
    st.plotly_chart(fig)

def shear_force_diagram(span, load_location, load_magnitude):
    # Calculate reactions at the supports (R_L and R_R)
    R_L = (load_magnitude * (span - load_location)) / span  # Reaction at left support
    R_R = (load_magnitude * load_location) / span  # Reaction at right support
    # Define the x-coordinates along the beam (splitting into smaller steps to see the discontinuity)
    x_points = np.linspace(0, span, 1000)
    # Define the shear force at each x-coordinate
    shear_forces = []

    # Calculate shear force at each point
    for x in x_points:
        if x < load_location:
            # Before the load, the shear force is equal to R_L
            shear_forces.append(R_L)
        elif x == load_location:
            # At the load, there is a jump in shear force, so we'll add a marker
            shear_forces.append(R_L)  # Keep shear force right before the load
        else:
            # After the load, the shear force is R_L - P
            shear_forces.append(R_L - load_magnitude)

    # Create the figure for the Shear Force Diagram
    fig = go.Figure()
    # Plot the shear force diagram as a piecewise constant function
    fig.add_trace(go.Scatter(
        x=x_points, 
        y=shear_forces, 
        mode='lines', 
        line=dict(color="blue", width=4),
        name="Shear Force",
    ))
    # Add a vertical line at the load location to represent the discontinuity (jump)
    fig.add_vline(
        x=load_location,
        line=dict(color="red", dash="dash"),
        annotation_text=f"Load = {load_magnitude} kN",
        annotation_position="top right",
        annotation=dict(font=dict(size=14, color="red")),
    )
    # Customize layout for the shear force diagram
    fig.update_layout(
        title="Shear Force Diagram",
        xaxis=dict(
            title="Beam Length (m)", 
            range=[0, span+0.2],  # Set the range for the x-axis from 0 to the span of the beam
            zeroline=True,  # Ensure a line at x = 0
            zerolinecolor="black",  # Color for the x-axis at y = 0
        ),
        yaxis=dict(
            title="Shear Force (kN)", 
            rangemode="tozero",  # Start the y-axis at zero for better clarity
            showgrid=True,  # Show grid for better clarity of values
            zeroline=True,  # Ensure a line at y = 0
            zerolinecolor="black",  # Color for the y-axis at x = 0
            range=[-max(R_L, load_magnitude), max(R_L, load_magnitude)],  # Make sure the range includes the reactions and load
        ),
        plot_bgcolor="white",
        showlegend=False,
        # Adjust figure size by setting a specific height and width
        height=300,  # Set the height of the plot (reduce the size)
        margin=dict(t=20, b=40, l=40, r=40),  # Adjust the margins for better spacing
    )
    return fig

def bending_moment_diagram(span, load_location, load_magnitude):
    # Calculate reactions at the supports (R_L and R_R)
    R_L = (load_magnitude * (span - load_location)) / span  # Reaction at left support
    R_R = (load_magnitude * load_location) / span  # Reaction at right support
    # Define the x-coordinates along the beam (splitting into smaller steps to see the behavior)
    x_points = np.linspace(0, span, 1000)
    # Define the bending moment at each x-coordinate
    bending_moments = []

    # Calculate the bending moment at each point along the beam
    for x in x_points:
        if x < load_location:
            # Before the load, the bending moment increases linearly
            bending_moments.append(R_L * x)
        else:
            # After the load, the bending moment decreases due to the applied point load
            bending_moments.append(R_L * x - load_magnitude * (x - load_location))

    # Create the figure for the Bending Moment Diagram
    fig = go.Figure()

    # Plot the bending moment diagram as a continuous curve
    fig.add_trace(go.Scatter(
        x=x_points, 
        y=bending_moments, 
        mode='lines', 
        line=dict(color="green", width=4),
        name="Bending Moment",
    ))

    # Add a vertical line at the load location to represent the discontinuity (jump)
    fig.add_vline(
        x=load_location,
        line=dict(color="red", dash="dash"),
        annotation_text=f"Load = {load_magnitude} kN",
        annotation_position="top right",
        annotation=dict(font=dict(size=14, color="red")),
    )

    # Customize layout for the bending moment diagram
    fig.update_layout(
        title="Bending Moment Diagram",
        xaxis=dict(
            title="Beam Length (m)", 
            range=[0, span+0.5],  # Set the range for the x-axis from 0 to the span of the beam
            zeroline=True,  # Ensure a line at x = 0
            zerolinecolor="black",  # Color for the x-axis at y = 0
        ),
        yaxis=dict(
            title="Bending Moment (kNm)", 
            rangemode="tozero",  # Start the y-axis at zero for better clarity
            showgrid=True,  # Show grid for better clarity of values
            zeroline=True,  # Ensure a line at y = 0
            zerolinecolor="black",  # Color for the y-axis at x = 0
            range=[-max(R_L * span-2, load_magnitude * span-30), max(R_L * span-2, load_magnitude * span-30)],  # Make sure the range includes the reactions and load
        ),
        plot_bgcolor="white",
        showlegend=False,
        height=300,  # Set the height of the plot (reduce the size)
        margin=dict(t=20, b=40, l=40, r=40),  # Adjust the margins for better spacing
    )
    return fig

# Function to draw beam with shear force diagram
def draw_beam_with_shear_force_and_bending_moment(span, left_support_type, right_support_type, load_location, load_magnitude):
    # Draw the beam with supports (from your previous function)
    draw_beam_with_supports_plotly(span, left_support_type, right_support_type, load_location, load_magnitude)
    # Generate and show the shear force diagram
    sfd_fig = shear_force_diagram(span, load_location, load_magnitude)
    sfd_fig.update_layout(margin=dict(t=20, b=20, l=40, r=40))  # Adjust margins for the shear force diagram
    st.plotly_chart(sfd_fig, use_container_width=True)  # Show Shear Force Diagram
    # Generate and show the bending moment diagram
    bmd_fig = bending_moment_diagram(span, load_location, load_magnitude)
    bmd_fig.update_layout(margin=dict(t=20, b=20, l=40, r=40))  # Adjust margins for the bending moment diagram
    st.plotly_chart(bmd_fig, use_container_width=True)  # Show Bending Moment Diagram

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
    t1, t2, t3 = st.tabs(["Section Library", "Custom Beam", "Beam Analyser"])

    # Use two columns for layout
    left_col, right_col = t1.columns([2, 5])  # 3 parts left, 1 part right for diagrams
    left2_col, right2_col = t2.columns([2, 7])
    left3_col, right3_col = t3.columns([1,3])
    # Load Workbook
    excel_file = "000_Steel Section Library.xlsx"
    wb, sheet_db, sheet_lookup = load_excel_data(excel_file, "Database", "Beam_Check")
    if not wb:
            st.error("Excel file could not be loaded.")
            return
    # Left Panel: Beam Input Section
    with left_col:
        Beam_Type = sheet_db.range('A4:A1021').value
        Beam_Selection = st.selectbox("Select Beam Type:", Beam_Type, index=0)
        Similarity_Type = sheet_db.range('AW28:AW29').value
        Similarity_Selection = st.selectbox("Select Similarity Type:", Similarity_Type, index=0)
        Yield_Strength = sheet_db.range('AR21:AR25').value
        Yield_Strength_Selection = st.selectbox("Yield Strength (MPa):", Yield_Strength, index=0)

        if st.button("Generate properties from Database"):
            try:
                sheet_lookup.range('C12').value = Beam_Selection
                sheet_lookup.range('C14').value = Similarity_Selection
                wb.save()
                # Generate the I-beam diagram when button is pressed
                fig = draw_static_ibeam_with_labels(sheet_lookup.range('E19').value, sheet_lookup.range('E20').value, sheet_lookup.range('E21').value, sheet_lookup.range('E22').value)
                st.pyplot(fig)
                with right_col:
                    a, b = st.columns([1,1])
                    with a:
                        st.write(f"Alt. Std. 1: {sheet_lookup.range('L12').value}")
                    with b:
                        st.write(f"Alt. Std. 2: {sheet_lookup.range('L13').value}")
                    df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:J', header=16, nrows=21)
                    df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3"]
                    # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                    df = df.applymap(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                    # Display the DataFrame with `st.table()`
                    st.table(df)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    with left2_col:
        # Streamlit UI
        # st.markdown('<h1 style="font-size: 20px;">Static I-Beam Diagram with Dynamic Labels</h1>', unsafe_allow_html=True)
        beam_type_selection = st.selectbox("Select Beam Type:", ["I-Beam", "Rectangular Beam", "Circular Beam"])
        # Display input fields based on the selected beam type
        if beam_type_selection == "I-Beam":
            # st.subheader("I-Beam Dimensions")
            a, b = st.columns([1, 1])
            with a:
                height = st.number_input("Height (mm)", min_value=100, max_value=2000, value=200)
                width = st.number_input("Width (mm)", min_value=50, max_value=1000, value=150)
            with b:
                flange_thickness = st.number_input("Tf (mm)", min_value=1, max_value=200, value=20)
                web_thickness = st.number_input("Tw (mm)", min_value=1, max_value=100, value=20)
        elif beam_type_selection == "Rectangular Beam":
            # st.subheader("Rectangular Beam Dimensions")
            a, b = st.columns([1, 1])
            with a:
                length = st.number_input("Length (mm)", min_value=100, max_value=5000, value=2000)
            with b:
                width = st.number_input("Width (mm)", min_value=1, max_value=1000, value=200)
                depth = st.number_input("Depth (mm)", min_value=1, max_value=1000, value=300)

        elif beam_type_selection == "Circular Beam":
            # st.subheader("Circular Beam Dimensions")
            diameter = st.number_input("Diameter (mm)", min_value=50, max_value=1000, value=200)

        Similarity_Type = sheet_db.range('AW28:AW29').value
        Similarity_Selection = st.selectbox("Select Similarity Type: ", Similarity_Type, index=0)
        Yield_Strength = sheet_db.range('AR21:AR25').value
        Yield_Strength_Selection = st.selectbox("Yield Strength (MPa): ", Yield_Strength, index=0)
        
        # Button to generate the diagram
        generate_button = st.button("Generate Properties")
        if generate_button:
               # Depending on the selected beam type, call the appropriate function to generate the diagram
            if beam_type_selection == "I-Beam":
                fig = draw_static_ibeam_with_labels(height, width, flange_thickness, web_thickness)
                st.pyplot(fig)
                try:
                    sheet_lookup.range('E42').value = height
                    sheet_lookup.range('E43').value = width
                    sheet_lookup.range('E44').value = flange_thickness
                    sheet_lookup.range('E45').value = web_thickness
                except Exception as e:
                    st.error(f"Failed to save data to Excel: {e}")
                
                with right2_col:
                    a, b, c = st.columns([1, 1, 1])
                    with a:
                        st.write(f"Alt. Std. 1: {sheet_lookup.range('L42').value}")
                    with b:
                        st.write(f"Alt. Std. 2: {sheet_lookup.range('L43').value}")
                    with c:
                        st.write(f"Alt. Std. 3: {sheet_lookup.range('L44').value}")

                    # Save other properties to the Excel sheet
                    try:
                        sheet_lookup.range('C47').value = Similarity_Selection
                        sheet_lookup.range('C48').value = Yield_Strength_Selection
                        wb.save()
                    except Exception as e:
                        st.error(f"Failed to save data to Excel: {e}")
                    df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:L', header=49, nrows=20)
                    df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3","Alt. Std. 3", "4"]
                    # st.dataframe(df, height = 740, use_container_width=True)
                    # Apply formatting to keep original decimal points but limit to 2 decimal places if necessary
                    df = df.applymap(lambda x: f"{x:.2f}" if isinstance(x, (float, int)) and ('.' in str(x) and len(str(x).split('.')[1]) > 2) else x)
                    # Display the DataFrame with `st.table()`
                    st.table(df)

            elif beam_type_selection == "Rectangular Beam":
                # Placeholder for generating a rectangular beam diagram
                # You will need to write a function for this if needed
                st.write("Rectangular Beam selected. (Function not yet implemented)")

            elif beam_type_selection == "Circular Beam":
                # Placeholder for generating a circular beam diagram
                # You will need to write a function for this if needed
                st.write("Circular Beam selected. (Function not yet implemented)")
 
    with left3_col:
        # st.subheader("BEAM CONDITION INITIALIZATION")
        st.markdown('<h1 style="font-size: 20px;">Beam Initialisation</h1>', unsafe_allow_html=True)
        span = st.number_input("Beam Span (in meters):", min_value=1.0, value=5.0)  # Default value 5 meters
        load = st.number_input("Load Magnitude (in kN):", min_value=1.0, value=5.0)  # Default value 5 kN
        load_loc = st.number_input("Load distance from left support (in meters):", min_value=1.0, value=2.5)  # Default value 2.5m
        # Left beam support
        left_support = st.radio(
        "Left End Support",
        options=["Pinned", "Fixed"],
        index=0,  # Default selection, you can change if you prefer
        horizontal=True)
        # Right beam support
        right_support = st.radio(
        "Right End Support",
        options=["Pinned", "Fixed"],
        index=0,  # Default selection, you can change if you prefer
        horizontal=True)
        
        generate_button = st.button("Generate Diagrams", key="generate_button_tab3")
        with right3_col:
            if generate_button:
                # draw_beam_with_supports_plotly(span,left_support,right_support, load_loc, load)
                draw_beam_with_shear_force_and_bending_moment(span,left_support,right_support, load_loc, load)
                
if __name__ == "__main__":
    main()
