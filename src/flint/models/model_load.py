"""Data models for loading operations in the ingestion framework.

This module defines the data models and configuration structures used for
representing data loading operations. It includes:

- Enums for representing loading methods, modes, and formats
- Data classes for structuring loading configuration
- Utility methods for parsing and validating loading parameters
- Constants for standard configuration keys

These models serve as the configuration schema for the Load components
and provide a type-safe interface between configuration and implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Self

from flint.exceptions import DictKeyError

from . import Model

NAME: Final[str] = "name"
UPSTREAM_NAME: Final[str] = "upstream_name"
METHOD: Final[str] = "method"
MODE: Final[str] = "mode"
DATA_FORMAT: Final[str] = "data_format"
LOCATION: Final[str] = "location"
SCHEMA_LOCATION: Final[str] = "schema_location"
OPTIONS: Final[str] = "options"


class LoadMethod(Enum):
    """Enumeration of supported data loading methods.

    Defines the different methods that can be used to write data to destinations,
    such as batch processing or streaming.

    These values are used in configuration files to specify how data should
    be loaded to the destination.
    """

    BATCH = "batch"
    STREAMING = "streaming"


class LoadMode(Enum):
    """Enumeration of supported data loading modes/behaviors.

    Defines the different modes that can be used when writing data to destinations,
    controlling behavior like appending vs. overwriting existing data.

    Includes both batch and streaming write modes supported by PySpark.
    These values are used in configuration files to specify the behavior
    when data is written to the destination.
    """

    # pyspark batch
    APPEND = "append"
    OVERWRITE = "overwrite"
    ERROR = "error"
    ERROR_IF_EXISTS = "errorifexists"
    IGNORE = "ignore"

    # pyspark streaming
    # APPEND = "append"  # already added above for pyspark batch
    COMPLETE = "complete"
    UPDATE = "update"


class LoadFormat(Enum):
    """Enumeration of supported data formats for loading operations.

    Defines the different file formats that can be used when writing data
    to destinations, such as Parquet, JSON, and CSV.

    These values are used in configuration files to specify the format
    of the output data.
    """

    PARQUET = "parquet"
    JSON = "json"
    CSV = "csv"


@dataclass
class LoadModel(Model, ABC):
    """Abstract base class for load operation models.

    This class defines the configuration model for data loading operations,
    specifying the name, upstream source, method, and destination for the load.

    It serves as the foundation for more specific load model types based on
    the destination type (file, database, etc.).

    Attributes:
        name: Unique identifier for this load operation
        upstream_name: Identifier of the upstream component providing data
        method: Loading method (batch or streaming)
        location (str): URI that identifies where to load data in the modelified format.
        schema_location (str): URI that identifies where to load schema.
        options (dict[str, Any]): Options for the sink input.
    """

    name: str
    upstream_name: str
    method: LoadMethod
    location: str
    schema_location: str | None
    options: dict[str, str]

    @classmethod
    @abstractmethod
    def from_dict(cls, dict_: dict[str, Any]) -> Self:
        """
        Create a loading model from a configuration dictionary.

        Args:
            dict_: Configuration dictionary containing loading parameters

        Returns:
            An initialized loading model

        Raises:
            DictKeyError: If required keys are missing from the configuration
        """


@dataclass
class LoadModelFile(LoadModel):
    """Abstract base class for file-based load models."""

    mode: LoadMode
    data_format: LoadFormat

    @classmethod
    def from_dict(cls, dict_: dict[str, Any]) -> Self:
        """
        Create a LoadModelFilePyspark object from a dict_ dictionary.

        Args:
            dict_ (dict[str, Any]): The dict_ dictionary.

        Returns:
            LoadModelFilePyspark: LoadModelFilePyspark object.
        """
        try:
            name = dict_[NAME]
            upstream_name = dict_[UPSTREAM_NAME]
            method = LoadMethod(dict_[METHOD])
            mode = LoadMode(dict_[MODE])
            data_format = LoadFormat(dict_[DATA_FORMAT])
            location = dict_[LOCATION]
            schema_location = dict_.get(SCHEMA_LOCATION, None)
            options = dict_.get(OPTIONS, {})
        except KeyError as e:
            raise DictKeyError(key=e.args[0], dict_=dict_) from e

        return cls(
            name=name,
            upstream_name=upstream_name,
            method=method,
            mode=mode,
            data_format=data_format,
            location=location,
            schema_location=schema_location,
            options=options,
        )
