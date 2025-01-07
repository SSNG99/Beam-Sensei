import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import xlwings as xw

# Set page configuration
st.set_page_config(page_title="Beam Analysis Tool", layout="wide")

# Define functions for data extraction and calculations

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
    reactions = {support['name']: {'vertical': 0, 'moment': 0} for support in supports}  # Updated to store both reactions

    A_loc, B_loc = supports[0]['location'], supports[1]['location']

    total_load = sum(load['magnitude'] for load in point_loads)
    moment_sum = sum(load['magnitude'] * (load['location'] - A_loc) for load in point_loads)
    
    if supports[0]['type'] == 'Fixed':  # Fixed support at A
        reaction_A_vertical = total_load - moment_sum / (B_loc - A_loc)
        reaction_A_moment = moment_sum
        reactions[supports[0]['name']] = {'vertical': reaction_A_vertical, 'moment': reaction_A_moment}
    else:  # Pinned or Roller
        reaction_A_vertical = total_load / 2
        reactions[supports[0]['name']] = {'vertical': reaction_A_vertical}

    if supports[1]['type'] == 'Fixed':  # Fixed support at B
        reaction_B_vertical = total_load - reaction_A_vertical
        reaction_B_moment = moment_sum / (B_loc - A_loc)
        reactions[supports[1]['name']] = {'vertical': reaction_B_vertical, 'moment': reaction_B_moment}
    else:
        reaction_B_vertical = total_load / 2
        reactions[supports[1]['name']] = {'vertical': reaction_B_vertical}

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
    # Use a higher resolution for more accurate calculations
    num_points = 5000  # Increase the number of points for better precision
    x = np.linspace(0, length, num_points)  # positions along the beam
    
    V = np.zeros_like(x)  # Shear force array
    M = np.zeros_like(x)  # Bending moment array
    D = np.zeros_like(x)  # Deflection array
    
    # Calculate shear force (V) at each point x
    for i, xi in enumerate(x):
        shear = 0
        moment = 0
        
        # Loop through all supports and add reactions at appropriate locations
        for support in supports:
            if xi >= support['location']:  # Add reaction forces at locations <= xi
                reaction = reactions[support['name']]
                
                if isinstance(reaction, dict):  # Fixed support (has moment and vertical force)
                    shear += reaction.get('vertical', 0)  # Add vertical force from the reaction
                    moment += reaction.get('moment', 0) * (xi - support['location'])  # Moment due to fixed support
                else:  # Roller or pinned support (only vertical force)
                    shear += reaction  # Add vertical reaction force

        # Subtract point loads to the left of xi
        for load in point_loads:
            if xi > load['location']:  # Point load is to the left of xi
                shear -= load['magnitude']  # Subtract point load value
                moment -= load['magnitude'] * (xi - load['location'])  # Subtract moment due to point load
        
        V[i] = shear  # Store shear force at xi
        M[i] = moment  # Store moment at xi
    
    # Calculate deflection (D) at each point x using the given deflection function
    D = calculate_deflection(x, point_loads, E, I, length)

    return x, V, M, D

def draw_beam_diagram(length, point_loads, reactions, supports):
    fig = go.Figure()

    # Draw the beam base line
    fig.add_trace(go.Scatter(x=[0, length], y=[0, 0], mode="lines", line=dict(color="black", width=6), name="Beam", showlegend=True))

    # Define markers and colors for supports
    support_markers = {'Pinned': 'circle', 'Roller': 'triangle-up', 'Fixed': 'square', 'Spring': 'x'}
    support_colors = {'Pinned': 'blue', 'Roller': 'orange', 'Fixed': 'red', 'Spring': 'green'}

    # A dictionary to store the adjusted y-positions for text labels to avoid overlap
    adjusted_positions = {'vertical': {}, 'moment': {}}

    # Step 1: Create a dictionary to store calculated positions for text
    # Store reactions and moments dynamically
    for support in supports:
        support_location = support['location']
        support_type = support['type']
        reaction_data = reactions.get(support['name'], {})

        # Check if the reaction data is a dict with vertical force and moment (for fixed support)
        vertical_reaction = reaction_data.get('vertical', 0)
        moment_reaction = reaction_data.get('moment', 0)

        # Initialize dynamic vertical and moment offsets
        y_offset_vertical = 0
        y_offset_moment = 0

        # Step 2: Avoid overlap by dynamically adjusting positions based on previous reactions/moments
        # Adjust vertical position
        if support['name'] not in adjusted_positions['vertical']:
            adjusted_positions['vertical'][support['name']] = vertical_reaction  # Set the initial position
        else:
            adjusted_positions['vertical'][support['name']] += 0.4  # Increase space if overlapping

        # Adjust moment position, if there is a moment
        if moment_reaction != 0:
            if support['name'] not in adjusted_positions['moment']:
                adjusted_positions['moment'][support['name']] = moment_reaction + 0.5  # Place it above or below reaction
            else:
                adjusted_positions['moment'][support['name']] += 0.5  # Increase space for the moment label if needed

        # Step 3: Place the support marker and labels dynamically
        fig.add_trace(go.Scatter(
            x=[support_location],
            y=[0],
            mode='markers+text',
            marker=dict(size=12, symbol=support_markers[support_type], color=support_colors[support_type]),
            text=f"{support['name']}<br>({vertical_reaction:.2f} kN)",
            textposition="top center",
            hoverinfo='text',
            name=f"Support {support['name']}",
            showlegend=True
        ))

        # Vertical reaction force line and text
        fig.add_trace(go.Scatter(
            x=[support_location, support_location],
            y=[0, vertical_reaction],
            mode="lines+text",
            line=dict(color=support_colors[support_type], width=2, dash="dot"),
            text=[f"{vertical_reaction:.2f} kN"],
            textposition="top right" if vertical_reaction > 0 else "bottom right",
            name=f"Reaction at {support['name']} (Vertical)",
            showlegend=True
        ))

        # Add moment reaction force with dynamic positioning
        if moment_reaction != 0:
            fig.add_trace(go.Scatter(
                x=[support_location],
                y=[adjusted_positions['moment'][support['name']]],  # Dynamic position
                mode="markers+text",
                marker=dict(size=12, symbol="star", color="black"),
                text=f"Moment: {moment_reaction:.2f} kN·m",
                textposition="bottom center" if moment_reaction > 0 else "top center",
                hoverinfo='text',
                name=f"Moment at {support['name']}",
                showlegend=True
            ))
        else:
            # If no moment, make sure the placeholder text is showing correctly for non-zero reactions
            if support['name'] not in adjusted_positions['moment']:
                adjusted_positions['moment'][support['name']] = 0.5  # Placeholder to keep space

    # Draw point loads
    for load in point_loads:
        fig.add_trace(go.Scatter(
            x=[load['location']],
            y=[0],
            mode='markers+text',
            marker=dict(size=12, symbol='arrow-bar-down', color='red'),
            text=f"{load['magnitude']} kN",
            textposition="bottom center" if load['magnitude'] > 0 else "top center",
            hoverinfo='text',
            name=f"Load at {load['location']}",
            showlegend=True
        ))

    # Update layout and make adjustments for visibility
    fig.update_layout(
        title="Beam Diagram with Supports and Reaction Forces",
        showlegend=True,  # Enable legend
        yaxis=dict(
            range=[-1, max([reaction_data.get('vertical', 0) for reaction_data in reactions.values()]) + 2],  # Adjust y range for clearer labels
            showgrid=False, zeroline=False, showticklabels=False),
        xaxis=dict(range=[-0.5, length + 0.5], showgrid=False, zeroline=False, showticklabels=True),
        height=500,  # Adjust height for better visibility
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
    st.write("Update the inputs and click the 'Generate Diagrams' button to see live changes in the beam diagrams.")

    # Use two columns for layout
    left_col, right_col = st.columns([1, 1])  # 3 parts left, 1 part right for diagrams

    # Left Panel: Beam Input Section
    with left_col:
        # Load Workbook
        excel_file = "000_Steel Section Library.xlsx"
        wb, sheet_db, sheet_lookup = load_excel_data(excel_file, "Database", "Beam_Check")

        if not wb:
            st.error("Excel file could not be loaded.")
            return
        
        Beam_Type = sheet_db.range('A3:A1021').value
        Beam_Selection = st.selectbox("Select Beam Type:", Beam_Type, index=1)

        Yield_Strength = sheet_db.range('AH20:AH25').value
        Yield_Strength_Selection = st.selectbox("Yield Strength:", Yield_Strength, index=1)

        E = I = None

        if st.button("Generate properties from Database"):
            try:
                sheet_lookup.range('C12').value = Beam_Selection
                wb.save()
                a, b = st.columns([1,1])
                with a:
                    st.write(f"Alt. Std. 1: {sheet_lookup.range('L12').value}")
                with b:
                    st.write(f"Alt. Std. 2: {sheet_lookup.range('L13').value}")
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

        # Manual Input for Material Properties (E, I)
        E_input_method = st.radio("Provide Material Properties:", ("Extract from Database", "Manual Input"))

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
        length = st.number_input("Length of Beam (in meters):", min_value=1.0, value=5.0)  # Default value 5 meters

        num_supports = st.number_input("Number of Supports:", min_value=2, step=1)

        st.subheader("SUPPORT DETAILS")
        supports = []
        support_columns = st.columns(num_supports)  # Create columns dynamically based on number of supports

        for i in range(num_supports):
            with support_columns[i]:
                name = st.text_input(f"Name {i+1}", f"Support {i+1}", key=f"support_name_{i+1}")
                location = st.number_input(f"Location {i+1} (m)", min_value=0.0, max_value=length, key=f"location_{i+1}")
                support_type = st.selectbox(f"Type {i+1}", options=["Pinned", "Roller", "Fixed"], key=f"support_type_{i+1}")
                supports.append({"name": name, "type": support_type, "location": location})

        num_point_loads = st.number_input("Number of Point Loads", min_value=1, step=1)
        st.subheader("POINT LOADS")
        point_loads = []
        point_load_columns = st.columns(num_point_loads)  # Create columns dynamically based on number of point loads

        for i in range(num_point_loads):
            with point_load_columns[i]:
                magnitude = st.number_input(f"Magnitude {i+1} (kN)", min_value=0.0, key=f"magnitude_{i+1}")
                location = st.number_input(f"Location {i+1} (m)", min_value=0.0, max_value=length, key=f"plocation_{i+1}")
                point_loads.append({"magnitude": magnitude, "location": location})

        # Generate Diagrams Button
        if st.button("Generate Diagrams"):
            if E is not None and I is not None and supports and point_loads:
                reactions = calculate_reaction_forces(length, supports, point_loads)
                if reactions:
                    with right_col:
                        st.subheader("Reaction Forces and Moments:")

                        # Prepare data for the table
                        reaction_data = []
                        for support in supports:
                            support_name = support['name']
                            reaction = reactions.get(support_name, {})

                            vertical_reaction = reaction.get('vertical', 0)
                            moment_reaction = reaction.get('moment', 0)
                            
                            # Append the data for each support
                            reaction_data.append([support_name, vertical_reaction, moment_reaction])

                        # Create a DataFrame for the reactions table
                        reactions_df = pd.DataFrame(reaction_data, columns=["Support", "Reaction Force (kN)", "Moment (kN·m)"])

                        # Display the table
                        st.table(reactions_df)

                    # Draw and display the diagrams
                    fig_beam = draw_beam_diagram(length, point_loads, reactions, supports)
                    right_col.plotly_chart(fig_beam, use_container_width=True)

                    x, V, M, D = calculate_shear_force_moment_deflection(length, supports, point_loads, reactions, E, I)

                    fig_shear_force = draw_shear_force_diagram(x, V)
                    right_col.plotly_chart(fig_shear_force, use_container_width=True)

                    fig_bending_moment = draw_bending_moment_diagram(x, M)
                    right_col.plotly_chart(fig_bending_moment, use_container_width=True)

                    fig_deflection = draw_deflection_diagram(x, D)
                    right_col.plotly_chart(fig_deflection, use_container_width=True)
            else:
                st.error("Please fill in all required fields before generating the diagrams.")

if __name__ == "__main__":
    main()