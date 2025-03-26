# Constructpy


[![image](https://img.shields.io/pypi/v/constructpy.svg)](https://pypi.python.org/pypi/constructpy)


Constructpy is a python library that performs constructability assessment tests on Industry Foundation Classes (IFC) BIM models.

## Features

Constructpy currently features 7 constructability tests divided into 3 categories (standardization, simplicity and accessibility). The tests are based on similar constructability assessment suite provided by the ECOS Revit plugin, described in Barros[1], but also takes into account some constructability assessment methods described in Tauriainen et al[2]. A short description of each test is provided below.

### Standardization

- **Structural types**: Checks the relation between the total number of load bearing beams and columns and the total number of its relative types;
- **Floor to floor height**: Checks the number of different floor to floor height in a building.

### Simplicity

- **Basement existence**: Checks whether a building has basement;
- **Length of beams**: Checks which percentage of beams meets a certain length criteria;
- **Precast structural elements**: Checks the percentage of precast concrete elements among load bearing beams and columns.

### Accessibility

- **Built area**: Checks the ratio of the footprint area and total available area in the site;
- **Location**: Checks the distance of the construction site and the nearest major city according to a provided database.

All tests query the IFC database and return a score between 0 and 1 where 0 is the minimum constructability score and 1 the maximum. The IFC objects queried and the specific test criteria are described in depth in the [documentation](https://chrisjesuscj.github.io/constructpy) (WIP).

## Installation

Use the [pip](https://pip.pypa.io/en/stable/) to install constructpy.

```bash
pip install constructpy
```

Constructpy depends on ifcopenshell and geopy libraries, if you intend to run the notebook provided in the example folder you also need jupyter-notebook, matplotlib and k3d to be installed. You can install the optional dependecies with the pip command below.

```bash
pip install constructpy[extra]
```

## Usage

To use constructpy you need an IFC4 file (prior versions of IFC are not supported). To perform a full constructability assessment you'll first need to load the IFC as an ifcopenshell object, then pass it to a Constructability object along with optional weights to be used in the calculation of the assessment scores.

```python
import ifcopenshell
from constructpy import Constructability

# Create an ifcopenshell ifc object
ifc_file = '<path_to/ifc_file.ifc>'
ifc = ifcopenshell.open(ifc_file)

# Set weights for constructability score calculation
stardardization_weight = 0.8
simplicity_weight = 1.0
accessibiliti_weight = 0.6

# Create a Constructability object passing the ifc and weights
con = Constructability(ifc, standardization_weight, simplicity_weight, accessibility_weight)

# Access the constructability scores as attributes of the object
constructability_score = con.constructability_score
standardization_score = con.standardization_score
simplicity_score = con.simplity_score
accessibility_score = con.accessibility_score
```

Aside from the general constructability score and the score for each category as shown in the snippet above, it is also possible to access the individual tests scores, which can also have individual weights set. For more in depth information on the library objects refer to the [documentation](https://chrisjesuscj.github.io/constructpy)(WIP). A jupyter notebook is also provided in the examples folder and showcases a basic usage of the library.

## License

Free software: MIT License

## References

- [1] B. A. F. S. Barros, “O Estudo Da Construtibilidade E Da Sustentabilidade Em Projetos Conceituais: Uma Abordagem Em BIM”, MESTRE EM ENGENHARIA CIVIL, PONTIFÍCIA UNIVERSIDADE CATÓLICA DO RIO DE JANEIRO, Rio de Janeiro, Brazil, 2021. doi: 10.17771/PUCRio.acad.55008.
- [2] M. K. Tauriainen, J. A. P. Puttonen, e A. J. Saari, “The Assessment of Constructability: BIM Cases”, Journal of Information Technology in Construction, vol. 20, p. 51–67, 2015.

