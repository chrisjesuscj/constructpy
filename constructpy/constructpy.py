import csv
import logging

import ifcopenshell
import ifcopenshell.util.element
import geopy.distance


class Constructability:
    """Main class for constructability assessment, holds all properties
    needed for a full assessment along with a few helper methods used in
    the child classes, this class instanciates all child classes

    :param ifc_obj: An IFC file object
    :type ifc_obj: ifcopenshell.file
    :param standardization_weight: The standardization weight value for
        use in the Standardization class, defaults to 1.0
    :type standardization_weight: float, optional
    :param simplicity_weight: The simplicity weight value for use in the
        Simplicity class, defaults to 1.0
    :type simplicity_weight: float, optional
    :param accessibility_weight: The accessibility weight value for use
        in the Accessibility class, defaults to 1.0
    :type accessibility_weight: float, optional
    :param structural_types_weight: The structural type weight value for
        use in the structural types standardization method, defaults to 1.0
    :type structural_types_weight: float, optional
    :param floor2floor_height_weight: The floor2florr weight value for use
        in the floor2floor height standardization method, defaults to 1.0
    :type floor2floor_height_weight: float, optional
    :param basement_weight: The basement weight value for use in the
        basement simplicity method, defaults to 1.0
    :type basement_weight: float, optional
    :param length_weight: The lenght of beams weight value for use in the
        lenght of beams simplicity method, defaults to 1.0
    :type length_weight: float, optional
    :param pcast_weight: The pcast weight value for use in the precast
        method, defaults to 1.0
    :type pcast_weight: float, optional
    :param area_weight: The built area weight value for use in the built
        area accessibility method, defaults to 1.0
    :type area_weight: float, optional
    :param location_weight: The location weight value for use in the
        location accessibility method, defaults to 1.0
    :type location_weight: float, optional
    """

    def __init__(
        self,
        ifc_obj: ifcopenshell.file,
        standardization_weight: float = 1.0,
        simplicity_weight: float = 1.0,
        accessibility_weight: float = 1.0,
        structural_types_weight: float = 1.0,
        floor2floor_height_weight: float = 1.0,
        basement_weight: float = 1.0,
        length_weight: float = 1.0,
        pcast_weight: float = 1.0,
        area_weight: float = 1.0,
        location_weight: float = 1.0,
    ) -> None:

        self.standardization_weight: float = standardization_weight
        self.simplicity_weight: float = simplicity_weight
        self.accessibility_weight: float = accessibility_weight
        self.standardization: Standardization = Standardization(
            ifc_obj, structural_types_weight, floor2floor_height_weight
        )
        self.standardization_score: float | None = (
            self.standardization.standardization_score
        )
        self.simplicity: Simplicity = Simplicity(
            ifc_obj, basement_weight, length_weight, pcast_weight
        )
        self.simplicity_score: float | None = self.simplicity.simplicity_score
        self.accessibility: Accessibility = Accessibility(
            ifc_obj, area_weight, location_weight
        )
        self.accessibility_score: float | None = self.accessibility.accessibility_score
        self.constructability_score: float | None = self.calculate_score(
            [
                (self.standardization_score, self.standardization_weight),
                (self.simplicity_score, self.simplicity_weight),
                (self.accessibility_score, self.accessibility_weight),
            ]
        )

    def ifc4_check(self, ifc_obj: ifcopenshell.file) -> ifcopenshell.file:
        """Checks IFC schema is of the correct version

        :param ifc_obj: An IFC file object
        :type ifc_obj: ifcopenshell.file
        :raises Exception: Not valid IFC schema
        :return: The same inputed IFC file object
        :rtype: ifcopenshell.file
        """

        if ifc_obj.schema == "IFC2X3":
            logging.error("IFC2X3 is not a valid schema")
            raise Exception("IFC2X3 is not a valid schema")
        else:
            return ifc_obj

    def calculate_score(self, scores: list[tuple]) -> float | None:
        """Calculate a total score based on list of parcial scores and weights

        :param scores: A list with scores and respective weights
        :type scores: list[tuple]
        :return: The calculated score
        :rtype: float | None
        """

        weight_list = []
        score_list = []
        for score in scores:
            if score[0] is None:
                scores.remove(score)
            elif score[1] == 0.0:
                scores.remove(score)
            else:
                score_list.append(float(score[0]) * float(score[1]))
                weight_list.append(float(score[1]))
        if score_list:
            return sum(score_list) / sum(weight_list)
        else:
            return None

    def get_load_bearing_elements(self, elements: list) -> list:
        """Filters a list of IFC elements based on the LoadBearing property

        :param elements: List of IFC elements
        :type elements: list
        :return: Filtered list with only LoadBearing elements
        :rtype: list
        """

        load_bearing = []
        for element in elements:
            if element.is_a("IfcBeam"):
                try:
                    if ifcopenshell.util.element.get_psets(element)["Pset_BeamCommon"][
                        "LoadBearing"
                    ]:
                        load_bearing.append(element)
                except KeyError:
                    logging.info(f"LoadBearing property not found in {element}")
            elif element.is_a("IfcColumn"):
                try:
                    if ifcopenshell.util.element.get_psets(element)[
                        "Pset_ColumnCommon"
                    ]["LoadBearing"]:
                        load_bearing.append(element)
                except KeyError:
                    logging.info(f"LoadBearing property not found in {element}")
        return load_bearing

    def dms_to_dd(
        self, degrees: int, minutes: int, seconds: int, microsseconds: int = 0
    ) -> float:
        """Converts a coordinate in degrees, as found in IfcCompoundPlaneAngleMeasure
        to degrees in decimals

        :param degrees: Degrees value
        :type degrees: float
        :param minutes: Minutes value
        :type minutes: float
        :param seconds: Seconds value
        :type seconds: float
        :param microsseconds: Microsseconds value, defaults to 0
        :type microsseconds: float, optional
        :return: Degrees in decimal value
        :rtype: float
        """
        return (
            degrees
            + minutes / 60
            + seconds / (60 * 60)
            + microsseconds / (60 * 60 * 60)
        )


class Standardization(Constructability):
    """Holds all methods related to standardization assessment along with
    its respective scores and weights 

    :param ifc_obj: An IFC file object
    :type ifc_obj: ifcopenshell.file
    :param structural_types_weight: The structural type weight value for
        use in the structural types standardization method, defaults to 1.0
    :type structural_types_weight: float, optional
    :param floor2floor_height_weight: The floor2florr weight value for use
        in the floor2floor height standardization method, defaults to 1.0
    :type floor2floor_height_weight: float, optional
    """
    def __init__(
        self,
        ifc_obj: ifcopenshell.file,
        structural_types_weight: float = 1.0,
        floor2floor_height_weight: float = 1.0,
    ) -> None:
  
        self.structural_types_score: float | None = (
            self.structural_types_standartization(super().ifc4_check(ifc_obj))
        )
        self.structural_types_weight: float = structural_types_weight
        self.floor2floor_height_score: float | None = (
            self.floor2floor_height_standardization(super().ifc4_check(ifc_obj))
        )
        self.floor2floor_height_weight: float = floor2floor_height_weight
        self.standardization_score: float | None = self.calculate_score(
            [
                (self.structural_types_score, self.structural_types_weight),
                (self.floor2floor_height_score, self.floor2floor_height_weight),
            ]
        )

    def structural_types_standartization(self, ifc: ifcopenshell.file) -> float | None:
        beams = super().get_load_bearing_elements(ifc.by_type("IfcBeam"))
        beam_types = set()
        for beam in beams:
            beam_types.add(beam.ObjectType)

        columns = super().get_load_bearing_elements(ifc.by_type("IfcColumn"))
        column_types = set()
        for column in columns:
            column_types.add(column.ObjectType)

        if beam_types.union(column_types):
            return 1 - (
                (len(beam_types) + len(column_types)) / (len(beams) + len(columns))
            )
        else:
            return None

    def floor2floor_height_standardization(
        self, ifc: ifcopenshell.file
    ) -> float | None:
        if not (building_storeys := ifc.by_type("IfcBuildingStorey")):
            logging.warning("No IfcBuildingStorey object found")
            return None

        elevation_list = []

        for storey in building_storeys:
            if storey.Elevation not in elevation_list:
                elevation_list.append(storey.Elevation)

        if len(elevation_list) == 1:
            return 1.0
        else:
            difference_list = [
                j - i for i, j in zip(elevation_list[:-1], elevation_list[1:])
            ]
            n_floor2floor = len(set(difference_list)) - 1

            if n_floor2floor == 0:
                return 1.0
            elif n_floor2floor <= 3:
                return 0.75
            elif n_floor2floor <= 6:
                return 0.5
            elif n_floor2floor <= 9:
                return 0.25
            elif n_floor2floor > 9:
                return 0.0
            else:
                return None


class Simplicity(Constructability):
    """Holds all methods related to simplicity assessment along with
    its respective scores and weights 

    :param ifc_obj: An IFC file object
    :type ifc_obj: ifcopenshell.file
    :param basement_weight: The basement weight value for use in the
        basement simplicity method, defaults to 1.0
    :type basement_weight: float, optional
    :param length_weight: The lenght of beams weight value for use in the
        lenght of beams simplicity method, defaults to 1.0
    :type length_weight: float, optional
    :param pcast_weight: The pcast weight value for use in the precast
        method, defaults to 1.0
    :type pcast_weight: float, optional
    """
    def __init__(
        self,
        ifc_obj: ifcopenshell.file,
        basement_weight: float = 1.0,
        length_weight: float = 1.0,
        pcast_weight: float = 1.0,
    ) -> None:

        self.basement_score = self.basement_simplicity(super().ifc4_check(ifc_obj))
        self.basement_weight = basement_weight
        self.length_score, self.valid_beams = self.length_of_beams_simplicity(
            super().ifc4_check(ifc_obj)
        )
        self.length_weight: float = length_weight
        self.pcast_score: float | None = self.precast_simplicity(
            super().ifc4_check(ifc_obj)
        )
        self.pcast_weight: float = pcast_weight
        self.simplicity_score: float | None = self.calculate_score(
            [
                (self.basement_score, self.basement_weight),
                (self.length_score, self.length_weight),
                (self.pcast_score, self.pcast_weight),
            ]
        )

    def basement_simplicity(self, ifc: ifcopenshell.file) -> float | None:
        if not (building_storeys := ifc.by_type("IfcBuildingStorey")):
            logging.warning("IfcBuildingStorey object not found")
            return None

        basement_elevation_threshold = -2.5

        for storey in building_storeys:
            elevation = storey.Elevation
            if elevation < basement_elevation_threshold:
                return 0.0
        return 1.0

    def length_of_beams_simplicity(
        self, ifc: ifcopenshell.file
    ) -> tuple[float, list] | None:
        beams = super().get_load_bearing_elements(ifc.by_type("IfcBeam"))
        count = 0

        if len(beams) == 0:
            logging.warning("No LoadBearing IfcBeams found")
            return None

        valid_beams = []
        for beam in beams:
            try:
                length = ifcopenshell.util.element.get_psets(beam)["Pset_BeamCommon"][
                    "Span"
                ]
            except KeyError:
                logging.warning(f"Span property not found in {beam}")
                return None

            if 3.0 <= length <= 7.0:
                valid_beams.append(beam)
                count += 1

            score = count / len(beams)

        return score, valid_beams

    def precast_simplicity(self, ifc: ifcopenshell.file) -> float | None:
        elements = [
            e
            for e in ifc.by_type("IfcElement")
            if e.is_a("IfcBeam") or e.is_a("IfcColumn")
        ]
        if not elements:
            logging.warning("IfcBeam or IfcColumn objects not found")
            return None

        elements = super().get_load_bearing_elements(elements)
        if not elements:
            logging.warning("No LoadBearing IfcBeam or IfcColumn objects found")
            return None

        precast_elements, concrete_elements = [], []

        for element in elements:
            try:
                c_method = ifcopenshell.util.element.get_psets(element)[
                    "Pset_ConcreteElementGeneral"
                ]["CastingMethod"]
            except KeyError:
                continue
            concrete_elements.append(element)
            if c_method == "PRECAST":
                precast_elements.append(element)

        if len(concrete_elements) == 0:
            logging.warning(
                "No IfcBeam or IfcColumn with Pset_ConcreteElementGeneral found"
            )
            return None

        return len(precast_elements) / len(concrete_elements)


class Accessibility(Constructability):
    """Holds all methods related to accessibility assessment along with
    its respective scores and weights 

    :param ifc_obj: An IFC file object
    :type ifc_obj: ifcopenshell.file
    :param area_weight: The built area weight value for use in the built
        area accessibility method, defaults to 1.0
    :type area_weight: float, optional
    :param location_weight: The location weight value for use in the
        location accessibility method, defaults to 1.0
    :type location_weight: float, optional
    """
    def __init__(
        self,
        ifc_obj: ifcopenshell.file,
        area_weight: float = 1.0,
        location_weight: float = 1.0,
    ) -> None:
        
        self.area_score: float | None = self.built_area_accessibility(
            super().ifc4_check(ifc_obj)
        )
        self.area_weight: float = area_weight
        self.location_score, self.location_city = self.location_accessibility(
            super().ifc4_check(ifc_obj)
        )
        self.location_weight: float = location_weight
        self.accessibility_score: float | None = self.calculate_score(
            [
                (self.area_score, self.area_weight),
                (self.location_score, self.location_weight),
            ]
        )

    def built_area_accessibility(self, ifc: ifcopenshell.file) -> float | None:
        buildings = ifc.by_type("IfcBuilding")
        if not buildings:
            logging.warning("IfcBuilding object not found")
            return None

        buildings_areas = []
        for building in buildings:
            try:
                area = ifcopenshell.util.element.get_psets(building)[
                    "Pset_BuildingCommon"
                ]["GrossPlannedArea"]
            except KeyError:
                logging.warning("GrossPlannedArea property not found")
                return None
            buildings_areas.append(area)

        site = ifc.by_type("IfcSite")
        try:
            site_area = ifcopenshell.util.element.get_psets(site)["Pset_SiteCommon"][
                "TotalArea"
            ]
        except KeyError:
            logging.warning("TotalArea property not found")
            return None

        return sum(buildings_areas) / site_area

    def location_accessibility(
        self, ifc: ifcopenshell.file
    ) -> tuple[float, list] | None:
        if not (site := ifc.by_type("IfcSite")[0]):
            logging.warning("IfcSite object not found")
            return None

        site_lat = site.RefLatitude
        site_lng = site.RefLongitude
        site_lat = super().dms_to_dd(site_lat[0], site_lat[1], site_lat[2], site_lat[3])
        site_lng = super().dms_to_dd(site_lng[0], site_lng[1], site_lng[2], site_lng[3])
        site_coordinates = (site_lat, site_lng)

        cities = []
        with open("assets/worldcities.csv") as file:
            main_cities = csv.DictReader(file)
            for row in main_cities:
                cities.append(
                    {"city": row["city"], "lat": row["lat"], "lng": row["lng"]}
                )

        distance = 999999.99
        for city in cities:
            city_coordinates = (float(city["lat"]), float(city["lng"]))
            new_distance = geopy.distance.geodesic(
                site_coordinates, city_coordinates
            ).kilometers
            if new_distance < distance:
                nearest_city = city["city"]
                distance = new_distance

        score = 1 - (distance / 100)
        if score < 0.0:
            return 0.0
        return score, [nearest_city, distance]
