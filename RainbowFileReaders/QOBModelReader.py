"""Provides classes that will read and parse QOB model files."""

from typing import List

from FileUtilities.BinaryConversionUtilities import BinaryFileDataStructure, FileFormatReader, BinaryFileReader, SizedCString
from RainbowFileReaders.RSEMaterialDefinition import RSEMaterialDefinition, RSEMaterialListHeader
from RainbowFileReaders.RSEGeometryDataStructures import R6QOBGeometryObject, RSEGeometryListHeader
from RainbowFileReaders.CXPMaterialPropertiesReader import CXPMaterialProperties, read_cxp


class QOBModelFile(FileFormatReader):
    """Class to read full QOB files"""
    def __init__(self):
        super(QOBModelFile, self).__init__()
        self.header: QOBHeader = None
        self.materialListHeader: RSEMaterialListHeader = None
        self.materials: List[RSEMaterialDefinition] = []
        self.geometryListHeader: RSEGeometryListHeader = None
        self.geometryObjects: List[R6GeometryObject] = []
        self.footer: QOBFooterDefinition = None

    def read_data(self):
        super().read_data()

        print("(QOBFModelReader) Invoked")

        fileReader = self._filereader

        print("(QOBFModelReader) 1. Going to read header")
        self.header = QOBHeader()
        self.header.read(fileReader)
        if self.verboseOutput:
            self.header.print_structure_info()
        print("(QOBFModelReader) 1. Header reading done")

        print("(QOBFModelReader) 2. Going to read materials list")
        self.materialListHeader = RSEMaterialListHeader()
        self.materialListHeader.read(fileReader)
        if self.verboseOutput:
            self.materialListHeader.print_structure_info()
        print(f"(QOBFModelReader) 2. Material list reading done (count: {self.materialListHeader.numMaterials})")

        print("(QOBFModelReader) 3. Going to find CXP Definitions")
        cxpFile = r'G:\Games\Rainbow Six Black Ops\data\texture\Rommel.CXP'
        CXPDefinitions: List[CXPMaterialProperties] = []
        CXPDefinitions.extend(read_cxp(cxpFile))
        print("(QOBFModelReader) 3. CXP Definitions acquired")

        print("(QOBFModelReader) 4. Going to read materials...")
        # self.materials = []
        for _ in range(self.materialListHeader.numMaterials):
            print("(QOBFModelReader)      Reading material %s" % _)
            newMaterial = RSEMaterialDefinition()
            newMaterial.read(fileReader)
            print(newMaterial)
            print("(QOBFModelReader)      Adding CXP info")
            newMaterial.add_CXP_information(CXPDefinitions)
            self.materials.append(newMaterial)
            if self.verboseOutput:
                newMaterial.print_structure_info()
        print("(QOBFModelReader) 4. All materials read done")

        print("(QOBFModelReader) 5. Going to read Geometry List...")
        self.geometryListHeader = RSEGeometryListHeader()
        self.geometryListHeader.read(fileReader)
        if self.verboseOutput:
            self.geometryListHeader.print_structure_info()
        print(f"(QOBFModelReader) 5. Geometry List read done (count: {self.geometryListHeader.count})")

        print("(QOBFModelReader) 6. Going to read Geometry objects...")
        for _ in range(self.geometryListHeader.count):
            newObj = R6QOBGeometryObject()
            newObj.read(fileReader)
            self.geometryObjects.append(newObj)
            if self.verboseOutput:
                newObj.print_structure_info()
        print("(QOBFModelReader) 6. All Geometry objects read done")

        print("(QOBFModelReader) 7. Going to read footer")
        self.footer = QOBFooterDefinition()
        self.footer.read(fileReader)
        if self.verboseOutput:
            self.footer.print_structure_info()
        print("(QOBFModelReader) 7. Footer reading done")


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
    
