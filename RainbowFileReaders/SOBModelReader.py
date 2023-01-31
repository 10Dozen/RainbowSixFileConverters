"""Provides classes that will read and parse SOB model files."""

from typing import List

from FileUtilities.BinaryConversionUtilities import BinaryFileDataStructure, FileFormatReader, SizedCString, BinaryFileReader
from RainbowFileReaders import R6Settings
from RainbowFileReaders.RSEMaterialDefinition import RSEMaterialDefinition, RSEMaterialListHeader
from RainbowFileReaders.CXPMaterialPropertiesReader import load_relevant_cxps
from RainbowFileReaders.RSEGeometryDataStructures import R6SOBGeometryObject, RSEGeometryListHeader


class SOBModelFile(FileFormatReader):
    """Class to read full SOB files"""
    def __init__(self):
        super(SOBModelFile, self).__init__()
        self.header: SOBHeader = None
        self.materialListHeader: RSEMaterialListHeader = None
        self.materials: List[RSEMaterialDefinition] = []
        self.geometryListHeader: RSEGeometryListHeader = None
        self.geometryObjects: List[R6SOBGeometryObject] = []
        self.footer: SOBFooterDefinition = None

    def read_data(self):
        super().read_data()

        fileReader = self._filereader

        self.verboseOutput and print(f"({__name__}) [>      ] Going to read header")

        self.header = SOBHeader()
        self.header.read(fileReader)
        if self.verboseOutput:
            self.header.print_structure_info()
        self.verboseOutput and print(f"({__name__}) [#      ] Header read")

        self.verboseOutput and print(f"({__name__}) [#>     ] Going to read materials list")
        self.materialListHeader = RSEMaterialListHeader()
        self.materialListHeader.read(fileReader)
        if self.verboseOutput:
            self.materialListHeader.print_structure_info()
        self.verboseOutput and print(f"({__name__}) [##     ] Material list reading done (count: {self.materialListHeader.numMaterials})")

        self.verboseOutput and print(f"({__name__}) [##>    ] Going to find and load CXP Definitions")
        _, gameDataPath, modPath = R6Settings.determine_data_paths_for_file(self.filepath)
        CXPDefinitions = load_relevant_cxps(gameDataPath, modPath)
        self.verboseOutput and print(f"({__name__}) [###    ] CXP Definitions acquired")

        self.verboseOutput and print(f"({__name__}) [###>   ] Going to read materials...")
        self.materials = []
        for _ in range(self.materialListHeader.numMaterials):
            self.verboseOutput and print(f"({__name__})      Reading material %s" % _)
            newMaterial = RSEMaterialDefinition()
            newMaterial.read(fileReader)
            self.verboseOutput and print(f"({__name__})      Adding CXP info")
            newMaterial.add_CXP_information(CXPDefinitions)
            self.materials.append(newMaterial)
            if self.verboseOutput:
                newMaterial.print_structure_info()
        self.verboseOutput and print(f"({__name__}) [####   ] All materials read done")

        self.verboseOutput and print(f"({__name__}) [####>  ] Going to read Geometry List...")
        self.geometryListHeader = RSEGeometryListHeader()
        self.geometryListHeader.read(fileReader)
        if self.verboseOutput:
            self.geometryListHeader.print_structure_info()
        self.verboseOutput and print(f"({__name__}) [#####  ] Geometry List read done (count: {self.geometryListHeader.count})")

        self.verboseOutput and print(f"({__name__}) [#####> ] Going to read Geometry objects...")
        self.geometryObjects = []
        for _ in range(self.geometryListHeader.count):
            newObj = R6SOBGeometryObject()
            newObj.read(fileReader)
            self.geometryObjects.append(newObj)
            if self.verboseOutput:
                newObj.print_structure_info()
        self.verboseOutput and print(f"({__name__}) [###### ] All Geometry objects read done")

        self.verboseOutput and print(f"({__name__}) [######>] Going to read footer")
        self.footer = SOBFooterDefinition()
        self.footer.read(fileReader)
        if self.verboseOutput:
            self.footer.print_structure_info()
        self.verboseOutput and print(f"({__name__}) [#######] Footer reading done")


class SOBHeader(BinaryFileDataStructure):
    """Contains the information stored in the file formats header structure"""
    def __init__(self):
        super(SOBHeader, self).__init__()

    def read(self, filereader: BinaryFileReader):
        super().read(filereader)

        self.header_begin_message = SizedCString(filereader)


class SOBFooterDefinition(BinaryFileDataStructure):
    """Contains the information stored in the file formats footer structure"""
    def __init__(self):
        super(SOBFooterDefinition, self).__init__()

    def read(self, filereader: BinaryFileReader):
        super().read(filereader)
        self.end_model_string = SizedCString(filereader)


if __name__ == "__main__":
    test = SOBModelFile()
