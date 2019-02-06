"""
This file contains a base class describing material properties.
"""

from typing import List, Union, Dict, Any
from pathlib import Path

import toml

from beamdesign.const import MatType


class Material:
    """
    This is intended to be a very basic material class to store a material object.

    NOTE: this class should store very little information and have few methods as many
    of the material properties etc. are determined by specific code rules.

    This results in a very simple object that could easily have been a named tuple etc.
    however this has been designed as a class to allow it to be extended in future
    if required and to allow for the use of a classmethod for loading material objects
    from a TOML file.
    """

    def __init__(
        self,
        *,
        type: Union[MatType, str],
        name: str,
        standard: str,
        properties: Dict[str, Any],
    ):
        """
        Constructor for a Material object.

        :param type: The type of the material.
        :param name: The name of the material.
        :param standard: The standard that the material complies with.
        :param properties: The properties of the material. This should be a dictionary
            containing appropriate properties that the relevant design standards would
            understand.
        """

        if isinstance(type, str):
            type = MatType(type)

        self.type = type
        self.name = name
        self.standard = standard
        self.properties = properties

    def __eq__(self, other):
        """
        Override the equality test.
        """

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

        return NotImplemented

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"type={self.type}, "
            + f"name={self.name}, "
            + f"standard={self.standard}"
            + f")"
        )

    @classmethod
    def load_material(
        cls, *, file_path: str = None, name: str = None
    ) -> Union["Material", Dict[str, "Material"]]:
        """
        This class method creates ``Steel`` objects from a JSON file stored in the
        specified location. If not specified, the default values stored in the package
        are loaded.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded.
        :param name: The name of the material to load. If None, a dict of all
            possible ``Material`` objects are returned.
        :return: A ``Material`` object or a dictionary of them.
        """

        vals = cls._load_helper(file_path=file_path)

        ret_dict = {}

        for k, v in vals.items():

            kwargs = {}
            kwargs["type"] = v.pop("type")
            kwargs["name"] = v.pop("name")
            kwargs["standard"] = v.pop("standard")
            kwargs["properties"] = v

            ret_dict[k] = cls(**kwargs)

        if name is not None:

            return ret_dict[name]

        return ret_dict

    @classmethod
    def load_list(cls, *, file_path: str = None) -> List[str]:
        """
        This class method loads a JSON file stored in the specified location and
        returns a list of available materials that can be loaded into a steel object.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded.
        :return: A list of all the Steel objects that could be loaded.
        """

        return list(cls._load_helper(file_path=file_path))

    @classmethod
    def _load_helper(cls, *, file_path) -> Dict[str, Any]:
        """
        This class method loads a JSON file stored in the specified location.
        If not specified, the default values stored in the package are loaded.

        This is used as a helper method for the load_xxx classmethods.

        :param file_path: The file_path to load the values from. If not specified, the
            default values will be loaded from the file in the package.
        :return: A dictionary containing the parsed JSON file.
        """

        if file_path is None:
            mod_file = Path(__file__)
            file_path = mod_file.parent / "material.toml"

        else:
            file_path = Path(file_path)

        with file_path.open(mode="r") as f:
            vals = toml.load(f=f)

        return vals
