import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Function to compute the fixed-end moments for a point load
def fixed_end_moments(span, load_location, load_magnitude):
    M_A = -load_magnitude * load_location * (span - load_location) / span  # Moment at left support
    M_B = load_magnitude * load_location * (span - load_location) / span  # Moment at right support
    return M_A, M_B

# Function to calculate the shear force at each point along the beam
def calculate_shear_force(span, load_location, load_magnitude, reactions, left_support_type, right_support_type):
    # Generate points along the span for SFD
    num_points = 100
    x_vals = np.linspace(0, span, num_points)
    shear_forces = np.zeros_like(x_vals)

    # Unpack reactions
    R_A, R_B, M_A, M_B = reactions

    for i, x in enumerate(x_vals):
        if left_support_type == 'Pinned' and right_support_type == 'Pinned':
            # For Pinned + Pinned: Linear shear force distribution
            if x < load_location:
                shear_forces[i] = R_A
            else:
                shear_forces[i] = R_A - load_magnitude
        elif left_support_type == 'Pinned' and right_support_type == 'Fixed':
            # For Pinned + Fixed: Moment effect at the right support
            if x < load_location:
                shear_forces[i] = R_A
            else:
                shear_forces[i] = R_A - load_magnitude + M_A / span  # Moment influence at fixed support

        elif left_support_type == 'Fixed' and right_support_type == 'Pinned':
            # For Fixed + Pinned: Moment effect at the left support
            if x < load_location:
                shear_forces[i] = R_A + M_A / span  # Moment influence at fixed support
            else:
                shear_forces[i] = R_A - load_magnitude

        elif left_support_type == 'Fixed' and right_support_type == 'Fixed':
            # For Fixed + Fixed: Both supports have moment influences
            if x < load_location:
                shear_forces[i] = R_A + M_A / span  # Moment influence at left fixed support
            else:
                shear_forces[i] = R_A - load_magnitude + M_B / span  # Moment influence at right fixed support

    return x_vals, shear_forces

# Function to calculate the reactions at supports (including moments for fixed supports)
def calculate_reactions(span, load_location, load_magnitude, left_support_type, right_support_type):
    if left_support_type == 'Pinned' and right_support_type == 'Pinned':
        R_A = (load_magnitude * (span - load_location)) / span  # Reaction at left support
        R_B = load_magnitude - R_A  # Reaction at right support
        M_A = 0  # No moment at pinned support
        M_B = 0  # No moment at pinned support

    elif left_support_type == 'Pinned' and right_support_type == 'Fixed':
        # Reaction at left support (pinned)
        R_A = (load_magnitude * (span - load_location)) / span
        R_B = load_magnitude - R_A  # Reaction at right support

        # Fixed-end moments at right support (M_B)
        M_A = 0  # No moment at pinned support
        M_B = load_magnitude * load_location * (span - load_location) / (2 * span)  # Moment at fixed support

    elif left_support_type == 'Fixed' and right_support_type == 'Pinned':
        # Reaction at right support (pinned)
        R_B = (load_magnitude * load_location) / span
        R_A = load_magnitude - R_B  # Reaction at left support

        # Fixed-end moments at left support (M_A)
        M_A = -(load_magnitude * load_location * (span - load_location)) / (2 * span)
        M_B = 0  # No moment at pinned support

    elif left_support_type == 'Fixed' and right_support_type == 'Fixed':
        # Reactions for both fixed supports
        R_A = (load_magnitude * (span - load_location)) / span
        R_B = load_magnitude - R_A

        # Fixed-end moments for both supports
        M_A = -(load_magnitude * load_location * (span - load_location)) / (2 * span)
        M_B = (load_magnitude * load_location * (span - load_location)) / (2 * span)

    return R_A, R_B, M_A, M_B

# Function to display the shear force values in a table format
def display_shear_force_values(span, load_location, load_magnitude, reactions, left_support_type, right_support_type):
    # Calculate shear force at key points
    R_A, R_B, M_A, M_B = reactions

    shear_at_left_support = R_A + M_A / span
    shear_at_right_support = R_B + M_B / span
    shear_at_load_location = R_A - load_magnitude + M_A / span

    # Prepare the results table
    shear_force_data = {
        'Location (m)': ['Left Support', 'Load Location', 'Right Support'],
        'Shear Force (kN)': [shear_at_left_support, shear_at_load_location, shear_at_right_support]
    }

    # Display the table using Streamlit
    st.write("### Shear Force Values at Key Locations:")
    st.table(shear_force_data)

# Plotting the Shear Force Diagram (SFD)
def plot_sfd(x_vals, shear_forces):
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, shear_forces, label="Shear Force", color='blue', lw=2)
    plt.axhline(0, color='black', lw=1)
    plt.title('Shear Force Diagram (SFD)')
    plt.xlabel('Span (m)')
    plt.ylabel('Shear Force (kN)')
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

# Main function to run the Moment Distribution Method
def main():
    st.title('Moment Distribution Method for Beam Analysis')

    # User Inputs
    span = st.number_input("Enter span of beam (in meters):", min_value=0.1, value=5.0)
    load_location = st.number_input("Enter location of point load (in meters from left support):", 
                                    min_value=0.0, max_value=span, value=2.0)
    load_magnitude = st.number_input("Enter load magnitude (in kN):", min_value=0.0, value=10.0)
    
    left_support_type = st.selectbox("Select left support type:", ["Pinned", "Fixed"])
    right_support_type = st.selectbox("Select right support type:", ["Pinned", "Fixed"])
    
    # Calculate reactions and moments at the supports
    reactions = calculate_reactions(span, load_location, load_magnitude, left_support_type, right_support_type)
    
    # Display the results (reactions, moments, shear forces)
    R_A, R_B, M_A, M_B = reactions
    st.subheader("Results:")
    st.write(f"Reaction at Left Support (R_A): {R_A:.2f} kN")
    st.write(f"Reaction at Right Support (R_B): {R_B:.2f} kN")
    st.write(f"Moment at Left Support (M_A): {M_A:.2f} kNm")
    st.write(f"Moment at Right Support (M_B): {M_B:.2f} kNm")
    
    # Display shear force values at key locations in a table
    display_shear_force_values(span, load_location, load_magnitude, reactions, left_support_type, right_support_type)

    # Calculate and plot Shear Force Diagram (SFD)
    x_vals, shear_forces = calculate_shear_force(span, load_location, load_magnitude, reactions, left_support_type, right_support_type)
    plot_sfd(x_vals, shear_forces)

# Run the Streamlit app
if __name__ == "__main__":
    main()
