import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import xlwings as xw

# Set page configuration
st.set_page_config(page_title="Beam Analysis Tool", layout="wide")

# Define functions
def load_excel_data(filepath, database_sheet, lookup_sheet):
    try:
        wb = xw.Book(filepath)
        sheet_db = wb.sheets[database_sheet]
        sheet_lookup = wb.sheets[lookup_sheet]
        return wb, sheet_db, sheet_lookup
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None, None, None

def calculate_reaction_forces(length, supports, point_loads):
    if len(supports) < 2:
        st.error("At least two supports are needed for a static beam.")
        return None

    reactions = {support['name']: 0 for support in supports}

    A_loc, B_loc = supports[0]['location'], supports[1]['location']

    if A_loc == B_loc:
        st.error("Supports cannot be at the same location.")
        return None

    total_load = sum(load['magnitude'] for load in point_loads)
    moment_sum = sum(load['magnitude'] * (load['location'] - A_loc) for load in point_loads)
    reaction_B = moment_sum / (B_loc - A_loc)
    reaction_A = total_load - reaction_B

    reactions[supports[0]['name']] = reaction_A
    reactions[supports[1]['name']] = reaction_B
    
    return reactions

def calculate_deflection(x, point_loads, E, I, length):
    D = np.zeros_like(x)
    for i, xi in enumerate(x):
        deflection = 0
        # Sum contributions from each point load
        for load in point_loads:
            P = load['magnitude']
            a = load['location']
            
            # Deflection contribution based on load position relative to xi
            if xi < a:
                deflection += (P * (xi) * (3 * length - xi)) / (6 * E * I * length)
            else:
                deflection += (P * (length - xi) * (3 * xi - length)) / (6 * E * I * length)

        D[i] = deflection
    
    return D

def calculate_shear_force_moment_deflection(length, supports, point_loads, reactions, E, I):
    # Number of points for the x-axis (beam length)
    num_points = 1000
    x = np.linspace(0, length, num_points)  # positions along the beam
    
    # Initialize arrays for shear force (V), bending moment (M), and deflection (D)
    V = np.zeros_like(x)
    M = np.zeros_like(x)
    D = np.zeros_like(x)
    
    # Calculate shear force (V) at each point x
    for i, xi in enumerate(x):
        # Calculate shear force due to reactions (using leftward summation of forces)
        shear = 0
        for support in supports:
            if xi >= support['location']:  # Reaction force at this support
                shear += reactions[support['name']]
        
        # Subtract point loads to the left of xi
        for load in point_loads:
            if xi >= load['location']:  # Point load at this location
                shear -= load['magnitude']
        
        V[i] = shear  # Store shear force at xi
    
    # Calculate bending moment (M) at each point x
    for i, xi in enumerate(x):
        moment = 0
        # Moment due to reaction forces (calculate the moment about xi from the left)
        for support in supports:
            if xi >= support['location']:
                moment += reactions[support['name']] * (xi - support['location'])
        
        # Subtract moments from point loads to the left of xi
        for load in point_loads:
            if xi >= load['location']:
                moment -= load['magnitude'] * (xi - load['location'])
        
        M[i] = moment  # Store bending moment at xi
    
    # Calculate deflection (D) at each point x
    D = calculate_deflection(x, point_loads, E, I, length)

    return x, V, M, D

def draw_beam_diagram(length, point_loads, reactions, supports):
    fig = go.Figure()

    # Draw the beam base line
    fig.add_trace(go.Scatter(x=[0, length], y=[0, 0], mode="lines", line=dict(color="black", width=6), showlegend=False))

    # Draw supports
    support_markers = {'Pinned': 'circle', 'Roller': 'triangle-up', 'Fixed': 'square', 'Spring': 'x'}
    support_colors = {'Pinned': 'blue', 'Roller': 'orange', 'Fixed': 'red', 'Spring': 'green'}

    for support in supports:
        fig.add_trace(go.Scatter(
            x=[support['location']],
            y=[0],
            mode='markers+text',
            marker=dict(size=12, symbol=support_markers[support['type']], color=support_colors[support['type']]),
            text=f"{support['name']}<br>({reactions[support['name']]:.2f} kN)",
            textposition="top center",
            hoverinfo='text',
            showlegend=False
        ))

    # Draw point loads
    for load in point_loads:
        fig.add_trace(go.Scatter(
            x=[load['location']],
            y=[0],
            mode='markers+text',
            marker=dict(size=12, symbol='arrow-bar-down', color='red'),
            text=f"{load['magnitude']} kN",
            textposition="bottom center",
            hoverinfo='text',
            showlegend=False
        ))

    fig.update_layout(
        title="Beam Diagram",
        showlegend=False,
        yaxis=dict(range=[-1, 1], showgrid=False, zeroline=False, showticklabels=False),
        xaxis=dict(range=[-0.5, length + 0.5], showgrid=False, zeroline=False, showticklabels=True),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def draw_shear_force_diagram(x, V):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=V, mode='lines', line=dict(color='blue', width=2), name='Shear Force'))
    fig.update_layout(
        title="Shear Force Diagram",
        xaxis_title="Length (m)",
        yaxis_title="Shear Force (kN)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

    return fig

def draw_bending_moment_diagram(x, M):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=M, mode='lines', line=dict(color='green', width=2), name='Bending Moment'))
    fig.update_layout(
        title="Bending Moment Diagram",
        xaxis_title="Length (m)",
        yaxis_title="Bending Moment (kN·m)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

    return fig

def draw_deflection_diagram(x, D):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=D, mode='lines', line=dict(color='purple', width=2), name='Deflection'))
    fig.update_layout(
        title="Deflection Diagram",
        xaxis_title="Length (m)",
        yaxis_title="Deflection (m)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

    return fig

# Main function to build the Streamlit app
def main():
    st.title("Interactive Beam Analysis: Reaction Forces, Shear Force, Bending Moment, and Deflection Diagrams")
    st.write("Update the inputs to see live changes in the beam diagrams.")

    # Load Workbook
    excel_file = "000_Steel Section Library.xlsx"
    wb, sheet_db, sheet_lookup = load_excel_data(excel_file, "Database", "Beam_Check")

    if not wb:
        st.stop()
    
    # Beam Selection
    st.subheader("BEAM PROPERTIES")
    col1, col2 = st.columns(2)
    with col1:
        Beam_Type = sheet_db.range('A3:A1021').value
        Beam_Selection = st.selectbox("Select Beam Type:", Beam_Type, index=1)  # Default to first option
        st.write("Selected Beam:", Beam_Selection)

    with col2:
        Yield_Strength = sheet_db.range('AH20:AH25').value
        Yield_Strength_Selection = st.selectbox("Yield Strength:", Yield_Strength, index=1)  # Default to first option
        st.write(f"Selected Yield Strength: {Yield_Strength_Selection} Mpa")

    # Update button
    E = I = None  # Initialize E and I
    if st.button("Generate properties from Database"):
        try:
            sheet_lookup.range('C12').value = Beam_Selection
            wb.save()

            df = pd.read_excel(excel_file, sheet_name="Beam_Check", usecols='B:J', header=15)
            df.columns = ["Variable", "Symbol", "=", "Chosen", "1", "Alt. Std. 1", "2", "Alt. Std. 2", "3"]
            st.dataframe(df)

            E_row = df.loc[df['Variable'] == 'Elastic Modulus (X)']
            I_row = df.loc[df['Variable'] == 'Second Moment Of Area (X)']

            if not E_row.empty:
                E = E_row['Chosen'].values[0]
                st.session_state["E"] = E
            else:
                st.error("Could not find Modulus of Elasticity (E) in the generated table.")

            if not I_row.empty:
                I = I_row['Chosen'].values[0]
                st.session_state["I"] = I
            else:
                st.error("Could not find Moment of Inertia (I) in the generated table.")

            if "E" in st.session_state:
                st.write(f"Extracted Modulus of Elasticity (E): {st.session_state['E']} N/m^2")
            if "I" in st.session_state:
                st.write(f"Extracted Moment of Inertia (I): {st.session_state['I']} m^4")

        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Check if user wants to input or extract material properties
    E_input_method = st.radio("How would you like to provide the material properties?", ("Extract from Table", "Manual Input"))

    if E_input_method == "Manual Input":
        col1, col2 = st.columns(2)
        with col1:
            E = st.number_input("Modulus of Elasticity (E) in GPa:", min_value=0.0) * 1e9
            st.session_state["E"] = E
        with col2:
            I = st.number_input("Moment of Inertia (I) in cm^4:", min_value=0.0) * 1e-8
            st.session_state["I"] = I

    if st.session_state.get("E") is not None and st.session_state.get("I") is not None:
        E = st.session_state["E"]
        I = st.session_state["I"]
        st.write(f"Using Modulus of Elasticity (E): {E} N/m^2")
        st.write(f"Using Moment of Inertia (I): {I} m^4")
    else:
        st.warning("Please provide the material properties either manually or by extraction.")
    
    # Beam Condition Initialization
    st.subheader("BEAM CONDITION INITIALIZATION")

    # User input for beam length with validation
    length = st.number_input("Length of Beam (in meters):", min_value=0.01, value=5.0)  # Default value 5 meters
    if length <= 0:
        st.error("Beam length must be greater than 0 meters.")
        return  # Stop further execution if length is invalid

    # User input for number of supports with validation
    num_supports = st.number_input("Number of Supports:", min_value=2, step=1, value=2)
    if num_supports < 2:
        st.error("At least 2 supports are required.")
        return  # Stop further execution if number of supports is invalid

    # User input for supports details with validation
    supports = []
    support_columns = st.columns(num_supports)  # Create columns dynamically based on number of supports
    support_locations = []

    for i in range(num_supports):
        with support_columns[i]:
            name = st.text_input(f"Name {i+1}", f"Support {i+1}", key=f"support_name_{i+1}")
            location = st.number_input(f"Location {i+1} (m)", min_value=0.0, max_value=length, key=f"location_{i+1}")
            support_type = st.selectbox(f"Type {i+1}", options=["Pinned", "Roller", "Fixed", "Spring"], key=f"support_type_{i+1}")
            
            # Check for duplicate support locations
            if location in support_locations:
                st.error(f"Duplicate support location detected: {location}m. Please ensure all support locations are unique.")
                return  # Stop execution if there are duplicates
            
            support_locations.append(location)
            supports.append({"name": name, "type": support_type, "location": location})

    # Check if support locations are within the beam's length
    if any(loc < 0 or loc > length for loc in support_locations):
        st.error("Support locations must be within the length of the beam (0m to {}m).".format(length))
        return  # Stop execution if any support location is out of range

    # User input for point loads with validation
    num_point_loads = st.number_input("Number of Point Loads", min_value=1, step=1)
    point_loads = []

    # User input for point loads details with validation
    for i in range(num_point_loads):
        with st.columns(1)[0]:
            magnitude = st.number_input(f"Magnitude {i+1} (kN)", min_value=0.0, key=f"magnitude_{i+1}")
            location = st.number_input(f"Location {i+1} (m)", min_value=0.0, max_value=length, key=f"plocation_{i+1}")
            
            # Check if the load magnitude is greater than zero
            if magnitude <= 0:
                st.error(f"Point load {i+1} must have a positive magnitude greater than 0 kN.")
                return  # Stop execution if the load magnitude is invalid
            
            # Ensure point load location is within the beam length
            if location < 0 or location > length:
                st.error(f"Point load {i+1} location must be within the beam's length (0m to {length}m).")
                return  # Stop execution if any load is out of range

            point_loads.append({"magnitude": magnitude, "location": location})

    # Create containers to dynamically update the diagrams
    reaction_container = st.empty()
    beam_container = st.empty()
    shear_force_container = st.empty()
    bending_moment_container = st.empty()
    deflection_container = st.empty()
    results_container = st.container()

    # Function to update the diagrams based on the inputs
    def update_diagrams():
        # Ensure that both E and I are provided before proceeding
        if 'E' not in st.session_state or 'I' not in st.session_state:
            st.error("Error: Both Modulus of Elasticity (E) and Moment of Inertia (I) must be provided to perform the calculations.")
            return  # Stop further execution if material properties are missing

        E = st.session_state.get("E")
        I = st.session_state.get("I")
        
        # Proceed with reaction force calculations
        reactions = calculate_reaction_forces(length, supports, point_loads)
        
        if reactions:
            # Display Reaction Forces
            with reaction_container:
                st.subheader("Reaction Forces:")
                reactions_df = pd.DataFrame(list(reactions.items()), columns=["Support", "Reaction Force (kN)"])
                st.table(reactions_df)
            
            # Draw Beam Diagram
            with beam_container:
                fig_beam = draw_beam_diagram(length, point_loads, reactions, supports)
                st.plotly_chart(fig_beam, use_container_width=True)
            
            # If E and I are provided, calculate and display the shear, moment, and deflection diagrams
            if E is not None and I is not None:
                x, V, M, D = calculate_shear_force_moment_deflection(length, supports, point_loads, reactions, E, I)
                
                # Shear Force Diagram
                with shear_force_container:
                    fig_shear_force = draw_shear_force_diagram(x, V)
                    st.plotly_chart(fig_shear_force, use_container_width=True)
                
                # Bending Moment Diagram
                with bending_moment_container:
                    fig_bending_moment = draw_bending_moment_diagram(x, M)
                    st.plotly_chart(fig_bending_moment, use_container_width=True)
                
                # Displaying extreme values (max shear, max moment, and max deflection)
                with results_container:
                    st.subheader("Force Extremes:")
                    extremes_df = pd.DataFrame({
                        "Position (m)": x,
                        "Shear Force (kN)": V,
                        "Bending Moment (kN·m)": M,
                        "Deflection (m)": D
                    })
                    
                    max_shear = extremes_df.iloc[np.argmax(np.abs(extremes_df["Shear Force (kN)"]))] 
                    max_moment = extremes_df.iloc[np.argmax(np.abs(extremes_df["Bending Moment (kN·m)"]))] 
                    max_deflection = extremes_df.iloc[np.argmax(np.abs(extremes_df["Deflection (m)"]))] 

                    st.table(pd.DataFrame([max_shear, max_moment, max_deflection], index=["Max Shear Force", "Max Bending Moment", "Max Deflection"]))
            else:
                st.error("Modulus of Elasticity (E) and Moment of Inertia (I) must be provided to calculate shear force, bending moment, and deflection.")
        else:
            st.error("Failed to calculate reaction forces. Please check the beam and support configuration.")

    # Update diagrams initially and whenever the inputs change
    update_diagrams()

    # Add callbacks to update diagrams when inputs change
    st.session_state.update_diagrams = update_diagrams

if __name__ == "__main__":
    main()