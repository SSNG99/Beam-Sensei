import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import openpyxl as op
import xlwings as xw
from openpyxl import load_workbook
from PIL import Image

#Initialize
excel_file = "000_Steel Section Library.xlsx"
wb = op.load_workbook(excel_file)
sheet_name_1 = "Database"
sheet_name_2 = "Beam_Check"
sheet_1 = wb[sheet_name_1]
sheet_2 = wb[sheet_name_2]
#cell id
# B12 = sheet['E12']

st.set_page_config(page_title="Beam Analysis Tool")
st.header("Beam Analysis Tool")
st.subheader("BEAM PROPERTIES")
st.markdown("Select Beam size:")


# Read the Excel file
# df_1 = pd.read_excel(excel_file, sheet_name=sheet_name_1)
# df_2 = pd.read_excel(excel_file, sheet_name=sheet_name_2)
# Extract the column as a list
# column_values = df_1['A'].tolist()

Beam_Type = [cell.value for cell in sheet_1['A']][3:]
Beam_Selection = st.selectbox("Beam Types:", Beam_Type)
st.write("Selected Beam:", Beam_Selection)
Yield_Strength = [cell.value for cell in sheet_1['AH']][20:25]
Yield_Strength_Selection = st.selectbox("Yield Strength:", Yield_Strength)
st.write(f"Selected Beam: {Yield_Strength_Selection} Mpa ")

def read_cell_with_formula(file_path, sheet_name, cell_address):
    try:
        # Use xlwings to connect to the Excel file
        app = xw.App(visible=False)  # Open Excel application not visible
        app.screen_updating = False
        wb = app.books.open(file_path)
        sheet = wb.sheets[sheet_name]

        # Read the cell with formula
        cell_formula = sheet.range(cell_address).formula
        cell_value = sheet.range(cell_address).value

        wb.close()
        app.quit()
        return cell_formula, cell_value
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None
    
def read_new(cell_address, type):
    _, updated_value = read_cell_with_formula(excel_file, sheet_name_2, cell_address)
    st.write(f"Updated {type}: {updated_value}")

if st.button("Update Lookup"):
    try:
        # Use xlwings to connect to the Excel file
        app = xw.App(visible=False)  # Open Excel application not visible
        app.screen_updating = False
        wb = xw.Book(excel_file)
        sheet = wb.sheets[sheet_name_2]

        # Update the cell that affects the VLOOKUP (assuming A1 affects VLOOKUP in B2)
        sheet.range('C12').value = Beam_Selection

        # Save and close the workbook
        wb.save()
        wb.close()
        app.quit()
        # Re-read the evaluated cell
        read_new("C13", "Standard")
        read_new("L12", "Alt. Std. 1")
        read_new("L13", "Alt. Std. 2")
        #Dataframe
        df = pd.read_excel(excel_file,sheet_name=sheet_name_2,
                           usecols='B:J',header=15)
        df.columns = ["Variable", "Symbol", "=", "Chosen","1","Alt. Std. 1","2","Alt. Std. 2","3"]
        st.dataframe(df)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# # second argument displays a default text inside the text input area
# w = st.text_input("Enter UDL")
# L = st.text_input("Enter Length")
# # display the name when the submit button is clicked
# # .title() is used to get the input text string

# def show_diagram():
#     m = bending_moment(distance)
#     fig = plt.figure(figsize=(7,8))
#     ax1 = fig.add_subplot(2,1,1)
#     ax1.fill_between(distance,v,color='green',alpha=0.5, hatch='||')
#     ax1.set_xlim(0,int(L))
#     ax1.set_ylim(-500,500)
#     ax1.set_title("Shear Force")
#     ax1.set_ylabel("Shear Force (N)")
#     ax1.plot(distance,v)

#     ax2=fig.add_subplot(2,1,2)
#     ax2.plot(distance,m)
#     ax2.fill_between (distance,m,color="red", alpha=0.5, hatch="||")
#     ax2.set_ylim(0,150)
#     ax2.set_title("Bending Moment")
#     ax2.set_ylabel("Bending Moment (Nm)")
#     ax2.set_xlim(0,int(L))
#     st.pyplot(plt.gcf())

# if(st.button('Submit')):
#     def shear_force(x):
#         return int(w)*((int(L)/2)-x)

#     distance = np.arange(0,1,0.01)
#     v = shear_force(distance)

#     def bending_moment(x):
#         return (int(w)*x/2)*(int(L)-x)
#     result_w = w.title()
#     result_L = L.title()
#     st.success(f"{result_w},{result_L}")
#     show_diagram()
# Function to calculate reaction forces based on supports and point loads
# Function to calculate reaction forces based on supports and point loads
# Function to calculate reaction forces based on supports and point loads
# Function to calculate reaction forces based on supports and point loads
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

# Function to calculate shear force and bending moment along the beam
def calculate_shear_force_moment(length, supports, point_loads, reactions):
    x = np.linspace(0, length, 1000)
    V = np.zeros_like(x)
    M = np.zeros_like(x)

    # Calculate the shear force and bending moment at each point along the beam
    for i, xi in enumerate(x):
        V[i] = sum(reactions[support['name']] if xi >= support['location'] else 0 for support in supports)
        V[i] -= sum(load['magnitude'] if xi >= load['location'] else 0 for load in point_loads)
        M[i] = sum(reactions[support['name']] * (xi - support['location']) if xi >= support['location'] else 0 for support in supports)
        M[i] -= sum(load['magnitude'] * (xi - load['location']) if xi >= load['location'] else 0 for load in point_loads)

    return x, V, M

# Function to draw the beam diagram with supports, loads, and reaction forces
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

# Function to draw the shear force diagram
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

# Function to draw the bending moment diagram
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

# Main function to build the Streamlit app
def main():
    st.title("Interactive Beam Analysis: Reaction Forces, Shear Force, and Bending Moment Diagrams")
    st.write("Update the inputs to see live changes in the beam diagrams.")

    # Initialize session state for number of supports and point loads
    if 'num_supports' not in st.session_state:
        st.session_state.num_supports = 2  # Minimum two supports required for a static beam
    if 'num_point_loads' not in st.session_state:
        st.session_state.num_point_loads = 1

    # User input for beam length
    length = st.number_input("Length of Beam (in meters):", min_value=1.0)

    # User input for number of supports
    st.session_state.num_supports = st.number_input("Number of Supports:", min_value=2, step=1)

    # User input for supports details
    supports = []
    for i in range(st.session_state.num_supports):
        with st.expander(f"Support {i+1}", expanded=True):
            name = st.text_input(f"Name of Support {i+1}", f"Support {i+1}", key=f"support_name_{i+1}")
            location = st.number_input(f"Location of Support {i+1} (in meters)", min_value=0.0, max_value=length, key=f"location_{i+1}")
            support_type = st.selectbox(f"Type of Support {i+1}", options=["Pinned", "Roller", "Fixed", "Spring"], key=f"support_type_{i+1}")
            supports.append({"name": name, "type": support_type, "location": location})

    # User input for number of point loads
    st.session_state.num_point_loads = st.number_input("Number of Point Loads", min_value=1, step=1)

    # User input for point loads details
    point_loads_section = {"loads": []}
    for i in range(st.session_state.num_point_loads):
        with st.expander(f"Point Load {i+1}", expanded=True):
            magnitude = st.number_input(f"Magnitude of Point Load {i+1} (in kN)", min_value=0.0, key=f"magnitude_{i+1}")
            location = st.number_input(f"Location of Point Load {i+1} (in meters)", min_value=0.0, max_value=length, key=f"plocation_{i+1}")
            point_loads_section["loads"].append({"magnitude": magnitude, "location": location})

    # Create a container to dynamically update the diagrams
    reaction_container = st.empty()
    beam_container = st.empty()
    shear_force_container = st.empty()
    bending_moment_container = st.empty()

    # Function to update the diagrams based on the inputs
    def update_diagrams():
        point_loads = point_loads_section['loads']
        reactions = calculate_reaction_forces(length, supports, point_loads)
        if reactions:
            with reaction_container:
                st.subheader("Reaction Forces:")
                for support in supports:
                    st.write(f"{support['name']} ({support['type']}) at {support['location']} m: {reactions[support['name']]:.2f} kN")
            with beam_container:
                fig_beam = draw_beam_diagram(length, point_loads, reactions, supports)
                st.plotly_chart(fig_beam, use_container_width=True)
            x, V, M = calculate_shear_force_moment(length, supports, point_loads, reactions)
            with shear_force_container:
                fig_shear_force = draw_shear_force_diagram(x, V)
                st.plotly_chart(fig_shear_force, use_container_width=True)
            with bending_moment_container:
                fig_bending_moment = draw_bending_moment_diagram(x, M)
                st.plotly_chart(fig_bending_moment, use_container_width=True)

    # Update diagrams initially and whenever the inputs change
    update_diagrams()

    # Add callbacks to update diagrams when inputs change
    st.session_state.update_diagrams = update_diagrams

if __name__ == "__main__":
    # st.set_page_config(layout="wide")
    main()