from circuitq.core import CircuitQ
from circuitq.functions_file import visualize_circuit_general

# Wrap the CircuitQ class
def cirCircuitQ(circuit_graph, ground_nodes=None, offset_nodes=None, force_flux_nodes=None,
                print_feedback=False, natural_units=False):
    """
    Initialize the circuit class corresponding to a superconducting circuit.

    Parameters
    ----------
    circuit_graph : NetworkX Graph
        The circuit graph, edges need to specify the 'element' attribute, with values 'C', 'L', or 'J'.
    ground_nodes : list, optional
        List of ground nodes, default is None.
    offset_nodes : list, optional
        List of offset nodes, default is None.
    force_flux_nodes : list, optional
        List of forced flux nodes, default is None.
    print_feedback : bool, optional
        Whether to print feedback information, default is False.
    natural_units : bool, optional
        Whether to use natural units, default is False.

    Returns
    -------
    CircuitQ
        The initialized circuit object.
    """
    return CircuitQ(circuit_graph, ground_nodes, offset_nodes, force_flux_nodes,
                    print_feedback, natural_units)

# Get classical Hamiltonian
def cirGet_classical_hamiltonian(CircuitQ):
    """
    Return the classical Hamiltonian of the circuit (Sympy expression).

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.

    Returns
    -------
    tuple
        A tuple containing the classical Hamiltonian, Hamiltonian parameters, and the implementation of the Hamiltonian.
    """
    return CircuitQ.get_classical_hamiltonian()

# Get numerical Hamiltonian
def cirGet_numerical_hamiltonian(CircuitQ, n_dim, grid_length=None, unit_cell=False,
                                parameter_values=None, default_zero=True):
    """
    Create a numerical Hamiltonian.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    n_dim : int
        The matrix dimension for each subsystem.
    grid_length : float, optional
        The length of the flux grid, default is None.
    unit_cell : bool, optional
        Whether to use a unit cell, default is False.
    parameter_values : list, optional
        A list of numerical values for system parameters, default is None.
    default_zero : bool, optional
        Whether to set default offset values to 0, default is True.

    Returns
    -------
    scipy.sparse matrix
        The numerical Hamiltonian matrix.
    """
    return CircuitQ.get_numerical_hamiltonian(n_dim, grid_length, unit_cell,
                                             parameter_values, default_zero)

# Get eigen system
def cirGet_eigensystem(CircuitQ, n_eig=30):
    """
    Compute the eigenvalues and eigenvectors of the numerical Hamiltonian.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    n_eig : int, optional
        The number of eigenvalues to return, default is 30.

    Returns
    -------
    tuple
        A tuple containing the eigenvalues and eigenvectors.
    """
    return CircuitQ.get_eigensystem(n_eig)

# Get spectrum anharmonicity
def cirGet_spectrum_anharmonicity(CircuitQ, nbr_check_levels=3):
    """
    Compute the spectral anharmonicity.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    nbr_check_levels : int, optional
        The number of energy levels used for analysis, default is 3.

    Returns
    -------
    float
        The spectral anharmonicity.
    """
    return CircuitQ.get_spectrum_anharmonicity(nbr_check_levels)

# Transform charge basis states to flux basis states
def cirTransform_charge_to_flux(CircuitQ):
    """
    Transform eigenstates to the flux basis.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.

    Returns
    -------
    list
        A list of transformed eigenstates.
    """
    return CircuitQ.transform_charge_to_flux()

# Get T1 time due to quasiparticles
def cirGet_T1_quasiparticles(CircuitQ, excited_level=None):
    """
    Estimate the T1 time due to quasiparticles.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    excited_level : int, optional
        The index of the excited state, default is None.

    Returns
    -------
    float
        The T1 time.
    """
    return CircuitQ.get_T1_quasiparticles(excited_level)

# Get T1 time due to dielectric loss
def cirGet_T1_dielectric_loss(CircuitQ, excited_level=None):
    """
    Estimate the T1 time due to dielectric loss.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    excited_level : int, optional
        The index of the excited state, default is None.

    Returns
    -------
    float
        The T1 time.
    """
    return CircuitQ.get_T1_dielectric_loss(excited_level)

# Get T1 time due to flux noise
def cirGet_T1_flux(CircuitQ, excited_level=None, lower_bound=False):
    """
    Estimate the T1 time due to flux noise.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    excited_level : int, optional
        The index of the excited state, default is None.
    lower_bound : bool, optional
        Whether to calculate the lower bound, default is False.

    Returns
    -------
    float
        The T1 time.
    """
    return CircuitQ.get_T1_flux(excited_level, lower_bound)

# Visualize the circuit
def cirVisualize_circuit(CircuitQ, save_as):
    """
    Visualize the circuit.

    Parameters
    ----------
    CircuitQ : CircuitQ
        The circuit object.
    save_as : str
        The save path.
    """
    visualize_circuit_general(CircuitQ.circuit_graph, save_as)