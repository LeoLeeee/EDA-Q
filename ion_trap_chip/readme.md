# Ion Trap Chip Generator

A Python-based 3D modeling tool for generating ion trap chips with precise electrode configurations and routing structures using OpenCASCADE Technology.

## Overview

This project generates ion trap chips with multi-layered cavity structures, precisely positioned electrodes, and sophisticated routing groove systems. The architecture is modular and configurable, making it suitable for research and development of ion trap quantum computing devices.

## Features

- **Multi-layer chip design** with configurable thickness and spacing
- **Tapered cavity structures** for optimal ion confinement
- **Automated electrode placement** with customizable patterns
- **Routing groove generation** for electrode connections
- **Circular cavity support** for additional functionality
- **3D visualization** and STEP file export
- **Modular, configurable architecture**

## Architecture

```
ion_trap_chip_generator/
├── main.py                          # Main entry point
├── config/                          # Configuration modules
│   ├── __init__.py
│   └── chip_parameters.py           # Parameter definitions
├── core/                            # Core functionality
│   ├── __init__.py
│   ├── chip_builder.py              # Main chip builder
│   ├── coordinate_system.py         # Coordinate management
│   ├── geometry/                    # 3D geometry generation
│   │   ├── __init__.py
│   │   ├── base_shapes.py           # Basic shape primitives
│   │   ├── cavities.py              # Ion trap cavities
│   │   └── electrodes.py            # Electrode structures
│   └── routing/                     # Routing path calculation
│       ├── __init__.py
│       ├── path_calculator.py       # Path planning
│       └── groove_generator.py      # Groove geometry
├── utils/                           # Utility functions
│   ├── __init__.py
│   ├── visualization.py            # 3D visualization
│   └── export.py                   # File export
└── requirements.txt                 # Dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenCASCADE Technology (OCE or OpenCASCADE Community Edition)

### Install Dependencies

```bash
pip install -r requirements.txt
```

The main dependency is `pythonocc-core`, which provides Python bindings for OpenCASCADE:

```bash
pip install pythonocc-core
```

### Alternative Installation Methods

For conda users:

```bash
conda install -c conda-forge pythonocc-core
```

## Quick Start

### Basic Usage

```python
from core.chip_builder import IonTrapChipGenerator

# Create chip generator
generator = IonTrapChipGenerator()

# Generate complete chip with routing
chip = generator.create_complete_ion_trap_chip()

# Visualize the result
generator.visualize_chip_with_points()

# Export to STEP file
generator.export_to_step("my_ion_trap_chip.step")
```

## Configuration

### Chip Parameters

Modify `config/chip_parameters.py` to customize chip dimensions:

```python
class ChipParameters:
    def __init__(self):
        self.chip_params = {
            'base_length': 20.0,           # mm - Chip length
            'base_width': 15.0,            # mm - Chip width
            'layer_thickness': 0.5,        # mm - Layer thickness
            'trap_long_length': 8.0,       # mm - Long cavity length
            'trap_short_length': 4.0,      # mm - Short cavity length
            # ... additional parameters
        }
```

### Electrode Configuration

Customize electrode patterns and dimensions:

```python
class ElectrodeParameters:
    def __init__(self):
        self.electrode_params = {
            'electrode_depth': 0.1,        # mm - Electrode depth
            'electrode_width': 0.060,      # mm - Electrode width
            'gap_width': 0.040,           # mm - Gap between electrodes
            'electrode_height': 1.0,       # mm - Electrode height
        }
  
        # Number of electrodes per region
        self.electrode_region_counts = {
            'left_top_left': 8,
            'left_top_up': 8,
            'right_top_right': 8,
            # ... additional regions
        }
```

### Routing Parameters

Configure routing groove generation:

```python
class RoutingParameters:
    def __init__(self):
        self.routing_params = {
            'chamfer_offset': 0.01,        # mm - Groove edge offset
            'left_turning_offset': 2.0,    # mm - Turning point offset
            'right_turning_offset': 2.0,   # mm - Turning point offset
        }
```

## Key Components

### Coordinate System

- Centers the coordinate system at the middle layer
- Handles Z-axis transformations for proper layer alignment
- Manages original and adjusted coordinate systems

### Cavity Generator

- Creates tapered pyramid structures for ion confinement
- Supports multi-layer designs with varying widths
- Generates circular holes for additional functionality

### Electrode Generator

- Calculates intersection points for electrode placement
- Generates electrode chains in 8 directional regions
- Creates routing connection points

### Routing System

- Calculates optimal routing paths from electrodes to chip edges
- Generates 3D groove geometries for electrical connections
- Supports both diagonal and planar routing segments

## Customization Examples

### Modify Chip Dimensions

```python
from config.chip_parameters import ChipParameters

# Create custom parameters
params = ChipParameters()
params.chip_params['base_length'] = 25.0  # Larger chip
params.chip_params['base_width'] = 20.0
params.chip_params['layer_thickness'] = 0.3  # Thinner layers
```

### Add More Electrodes

```python
from config.chip_parameters import ElectrodeParameters

electrode_config = ElectrodeParameters()
# Increase electrode count in specific regions
electrode_config.electrode_region_counts['left_top_left'] = 12
electrode_config.electrode_region_counts['right_bottom_right'] = 12
```

### Enable Circular Holes

```python
# In chip_parameters.py
'circular_holes': {
    'enabled': True,
    'radius': 1.5,                    # mm - Larger radius
    'positions': [
        (-8.0, -6.0),                 # Custom positions
        (8.0, 6.0),
        (0.0, -7.0)                   # Additional hole
    ],
    'through_all_layers': True,
}
```

## File Export

The generator supports STEP file export for CAD software compatibility:

```python
# Export with custom filename
generator.export_to_step("custom_chip_design.step")

# The STEP file can be imported into:
# - SolidWorks
# - AutoCAD
# - FreeCAD
# - Other CAD software
```

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```
   ImportError: No module named 'OCC'
   ```

   Solution: Install pythonocc-core properly:

   ```bash
   pip install --upgrade pythonocc-core
   ```
2. **Display Issues**

   ```
   OpenCASCADE display not available
   ```

   Solution: Install additional display dependencies or run in headless mode for export only.
3. **Geometry Generation Failures**

   - Check parameter values are positive and reasonable
   - Ensure electrode dimensions don't exceed cavity sizes
   - Verify layer thicknesses are sufficient for electrode heights

### Performance Considerations

- Complex designs with many electrodes may take several minutes to generate
- Large numbers of routing grooves increase computation time
- Consider reducing electrode counts for faster iteration during development

## Dependencies

- **pythonocc-core**: OpenCASCADE Python bindings for 3D modeling
- **matplotlib**: Optional, for enhanced visualization
- **numpy**: Optional, for numerical operations

## Contributing

The modular architecture makes it easy to extend functionality:

1. **Add new cavity types**: Extend `CavityGenerator` class
2. **Create custom electrode patterns**: Modify `ElectrodeGenerator`
3. **Implement new routing algorithms**: Extend `RoutingPathCalculator`
4. **Add export formats**: Extend `ChipExporter` class
