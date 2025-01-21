#!/usr/bin/env python3

import argparse
import ifcopenshell
from constructpy import Constructability


class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return self.start <= other <= self.end


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Constructability Report Utility"
    )
    parser.add_argument(
        "-i",
        "--ifc", 
        type=str, 
        required=True, 
        help="An IFC 4 file"
    )
    parser.add_argument(
        "--standardization",
        type=float,
        choices=[Range(0.0, 1.0)],
        default="1.0",
        help="Standardization weight [0.0-1.0]",
    )
    parser.add_argument(
        "--simplicity",
        type=float,
        choices=[Range(0.0, 1.0)],
        default="1.0",
        help="Simplicity weight [0.0-1.0]",
    )
    parser.add_argument(
        "--accessibility",
        type=float,
        choices=[Range(0.0, 1.0)],
        default="1.0",
        help="Accessibility weight [0.0-1.0]",
    )
    args = parser.parse_args()

    ifc = ifcopenshell.open(args.ifc)

    c = Constructability(
        ifc,
        standardization_weight=args.standardization,
        simplicity_weight=args.simplicity,
        accessibility_weight=args.accessibility,
    )

    print(f"Constructability Score: {c.constructability_score}")
    print(f"--- Standardization Score: {c.standardization_score}")
    print(f"--- Simplicity Score: {c.simplicity_score}")
    print(f"--- Accessibility Score: {c.accessibility_score}")
