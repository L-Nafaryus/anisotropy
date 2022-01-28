# -*- coding: utf-8 -*-

import pathlib
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator
import numpy as np

from . import utils


def read_foamfile(filename: str) -> tuple[dict, dict]:
    """Read a FoamFile.

    :param filename:
        Path to the file.
    :return:
        Two dictionaries that contains header and content information
        of the FoamFile.
    """
    path = pathlib.Path(filename).resolve()
    ppf = ParsedParameterFile(path)
    header = ppf.header or {}
    content = ppf.content or {}

    return header, content


def write_foamfile(header: dict, content: dict, filename: str):
    """Write a FoamFile to the file.

    :param header:
        Header block with the FoamFile metadata.
    :param content:
        Content block of the FoamFile.
    :param filename:
        Path to the file.
    """
    path = pathlib.Path(filename).resolve()

    #   preformat
    header = (
        FoamFileGenerator({}, header = header)
        .makeString()[ :-2]
        .replace("\n ", "\n" + 4 * " ")
    )
    content = (
        FoamFileGenerator(content)
        .makeString()[ :-1]
        .replace("\n  ", "\n" + 4 * " ")
        .replace(" \t// " + 73 * "*" + " //", "")
        .replace(" /* empty */ ", "")
    )

    with open(path, "w") as outfile:
        outfile.write(utils.template(header, content) + "\n")


def read_dat(filename: str):
    """Read dat file.

    :param filename:
        Path to the file.
    :return:
        Dictionary with arrays. Keys are created according file header
        block or numerated with string numbers if header is not found.
    """
    path = pathlib.Path(filename).resolve()
    header = []
    content = []

    with open(path, "r") as infile:
        for line in infile.readlines():
            if line.startswith("#"):
                header.append(line)

            else:
                content.append(line)

    columns = []

    if header[-1].find(":") < 0:
        for column in header[-1].replace("#", "").split("\t"):
            columns.append(column.strip())

        header.pop(-1)

    else:
        for column in range(len(content[0].split("\t"))):
            columns.append(str(column))

    output = {}

    for row in header:
        key, value = row.replace("#", "").split(":")

        try:
            value = float(value.strip())

        except Exception:
            value = value.strip()

        output[key.strip()] = value

    for column in columns:
        output[column] = []

    for row in content:
        values = row.split("\t")

        for column, value in zip(columns, values):
            output[column].append(float(value))

    for key in output.keys():
        output[key] = np.asarray(output[key])

    return output
