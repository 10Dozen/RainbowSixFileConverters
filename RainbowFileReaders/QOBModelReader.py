"""Provides classes that will read and parse QOB model files."""

from typing import List

from RainbowFileReaders import R6Settings
from FileUtilities.BinaryConversionUtilities import BinaryFileDataStructure, FileFormatReader, BinaryFileReader, SizedCString
from RainbowFileReaders.RSEMaterialDefinition import RSEMaterialDefinition, RSEMaterialListHeader
from RainbowFileReaders.RSEGeometryDataStructures import R6QOBGeometryObject, RSEGeometryListHeader
from RainbowFileReaders.CXPMaterialPropertiesReader import load_relevant_cxps


class QOBModelFile(FileFormatReader):
    """Class to read full QOB files"""
    def __init__(self):
        super(QOBModelFile, self).__init__()
        self.header: QOBHeader = None
        self.materialListHeader: RSEMaterialListHeader = None
        self.materials: List[RSEMaterialDefinition] = []
        self.geometryListHeader: RSEGeometryListHeader = None
        self.geometryObjects: List[R6QOBGeometryObject] = []
        self.footer: QOBFooterDefinition = None

    def read_data(self):
        super().read_data()

        print("(QOBModelReader) Invoked")

        fileReader = self._filereader

        print("(QOBModelReader) [>      ] Going to read header")
        self.header = QOBHeader()
        self.header.read(fileReader)
        if self.verboseOutput:
            self.header.print_structure_info()
        print("(QOBModelReader) [#      ] Header read")

        print("(QOBModelReader) [#>     ] Going to read materials list")
        self.materialListHeader = RSEMaterialListHeader()
        self.materialListHeader.read(fileReader)
        if self.verboseOutput:
            self.materialListHeader.print_structure_info()
        print(f"(QOBModelReader) [##     ] Material list reading done (count: {self.materialListHeader.numMaterials})")

        print("(QOBModelReader) [##>    ] Going to find and load CXP Definitions")
        _, gameDataPath, modPath = R6Settings.determine_data_paths_for_file(self.filepath)
        CXPDefinitions = load_relevant_cxps(gameDataPath, modPath)
        print("(QOBModelReader) [###    ] CXP Definitions acquired")

        print("(QOBModelReader) [###>   ] Going to read materials...")
        for _ in range(self.materialListHeader.numMaterials):
            print("(QOBModelReader)      Reading material %s" % _)
            newMaterial = RSEMaterialDefinition()
            newMaterial.read(fileReader)
            print("(QOBModelReader)      Adding CXP info")
            newMaterial.add_CXP_information(CXPDefinitions)
            self.materials.append(newMaterial)
            if self.verboseOutput:
                newMaterial.print_structure_info()
        print("(QOBModelReader) [####   ] All materials read done")

        print("(QOBModelReader) [####>  ] Going to read Geometry List...")
        self.geometryListHeader = RSEGeometryListHeader()
        self.geometryListHeader.read(fileReader)
        if self.verboseOutput:
            self.geometryListHeader.print_structure_info()
        print(f"(QOBModelReader) [#####  ] Geometry List read done (count: {self.geometryListHeader.count})")

        print("(QOBModelReader) [#####> ] Going to read Geometry objects...")
        for _ in range(self.geometryListHeader.count):
            newObj = R6QOBGeometryObject()
            newObj.read(fileReader)
            self.geometryObjects.append(newObj)
            if self.verboseOutput:
                newObj.print_structure_info()
        print("(QOBModelReader) [###### ] All Geometry objects read done")

        print("(QOBModelReader) [######>] Going to read footer")
        self.footer = QOBFooterDefinition()
        self.footer.read(fileReader)
        if self.verboseOutput:
            self.footer.print_structure_info()
        print("(QOBModelReader) [#######] Footer reading done")


class QOBHeader(BinaryFileDataStructure):
    """Contains the information stored in the file formats header structure"""
    def __init__(self):
        super(QOBHeader, self).__init__()

    def read(self, filereader: BinaryFileReader):
        super().read(filereader)
        self.header_begin_message = SizedCString(filereader)


class QOBFooterDefinition(BinaryFileDataStructure):
    """Contains the information stored in the file formats footer structure"""
    def __init__(self):
        super(QOBFooterDefinition, self).__init__()

    def read(self, filereader: BinaryFileReader):
        super().read(filereader)
        self.end_model_string = SizedCString(filereader)


if __name__ == "__main__":
    test = QOBModelFile()

