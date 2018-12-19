from RainbowFileReaders.R6Constants import RSEGameVersions, RSEMaterialFormatConstants
from RainbowFileReaders.BinaryConversionUtilities import BinaryFileDataStructure
import pprint

class RSEMaterialListHeader(BinaryFileDataStructure):
    def __init__(self):
        super().__init__()
        self.size = None
        self.unknown1 = None
        self.materialListBeginMessageLength = None
        self.materialListBeginMessageRaw = None
        self.materialListBeginMessage = None
        self.numMaterials = None

    def read(self, filereader):
        super().read(filereader)

        self.size = filereader.read_uint()
        self.unknown1 = filereader.read_uint()
        self.materialListBeginMessageLength = filereader.read_uint()
        self.materialListBeginMessageRaw = filereader.read_bytes(self.materialListBeginMessageLength)
        self.materialListBeginMessage = self.materialListBeginMessageRaw[:-1].decode("utf-8")
        self.numMaterials = filereader.read_uint()


class RSEMaterialDefinition(BinaryFileDataStructure):
    def __init__(self):
        super(RSEMaterialDefinition, self).__init__()
        self.size = None
        self.ID = None
        self.versionStringLength = None
        self.versionNumber = None
        self.versionStringRaw = None
        self.materialNameLength = None
        self.materialName = None
        self.materialNameRaw = None
        self.textureNameLength = None
        self.textureName = None
        self.textureNameRaw = None
        self.opacity = None
        self.unknown2 = None
        self.alphaMethod = None
        self.ambientColor = None
        self.diffuseColor = None
        self.specularColor = None
        self.specularLevel = None
        self.twoSidedRaw = None
        self.twoSided = None
        self.normalizedColors = None
        self.CXPMaterialProperties = None

    def get_material_game_version(self):
        """Returns the game this type of material is used in"""
        sizeWithoutStrings = self.size
        sizeWithoutStrings -= self.materialNameLength
        sizeWithoutStrings -= self.versionStringLength
        sizeWithoutStrings -= self.textureNameLength

        #check if it's a rainbow six file, or rogue spear file
        if sizeWithoutStrings == RSEMaterialFormatConstants.RSE_MATERIAL_SIZE_NO_STRINGS_RAINBOW_SIX or self.versionNumber is None:
            # Rainbow Six files typically have material sizes this size, or contain no version number
            return RSEGameVersions.RAINBOW_SIX
        else:
            #It's probably a Rogue Spear file
            #Material sizes in rogue spear files seem to be very inconsistent, so there needs to be a better detection method for future versions of the file
            #Actually, material sizes in rogue spear appear consistently as 69 if you just remove the texturename string length
            sizeWithoutStrings = self.size
            sizeWithoutStrings -= self.textureNameLength
            if sizeWithoutStrings == RSEMaterialFormatConstants.RSE_MATERIAL_SIZE_NO_STRINGS_ROGUE_SPEAR:
                return RSEGameVersions.ROGUE_SPEAR
            
        return RSEGameVersions.UNKNOWN

    def add_CXP_information(self, CXPDefinitions):
        """Takes a list of CXPMaterialProperties, and adds matching information"""
        for cxp in CXPDefinitions:
            #Match on lowercase since it's a windows game and windows has no concept of case sensitive filenames
            if cxp.materialName.lower() == self.textureName.lower():
                print("Matched CXP: " + cxp.materialName)
                self.CXPMaterialProperties = cxp

    def read(self, filereader):
        super().read(filereader)

        self.size = filereader.read_uint()
        self.ID = filereader.read_uint()

        self.versionStringLength = filereader.read_uint()
        self.versionNumber = None
        if self.versionStringLength == 8:
            self.versionStringRaw = filereader.read_bytes(self.versionStringLength)
            if self.versionStringRaw[:-1] == b'Version':
                self.versionNumber = filereader.read_uint()
                self.materialNameLength = filereader.read_uint()
                self.materialNameRaw = filereader.read_bytes(self.materialNameLength)
            else:
                self.materialNameLength = self.versionStringLength
                self.materialNameRaw = self.versionStringRaw
        else:
            self.materialNameLength = self.versionStringLength
            self.materialNameRaw = filereader.read_bytes(self.materialNameLength)

        self.textureNameLength = filereader.read_uint()
        self.textureNameRaw = filereader.read_bytes(self.textureNameLength)

        self.opacity = filereader.read_float()
        self.unknown2 = filereader.read_float() # Full lit?
        self.alphaMethod = filereader.read_uint() # Smoothing according to AK? Transparency method? Best guess at the moment is transparency method. 1 = SOLID, 2 = MASKED, 3 = ALPHA_BLEND

        gameVer = self.get_material_game_version()

        #check if it's a rainbow six file, or rogue spear file
        if gameVer == RSEGameVersions.RAINBOW_SIX:
            # Rainbow Six files typically have material sizes this size, or contain no version number
            self.ambientColor = filereader.read_rgb_color_24bpp_uint()
            self.diffuseColor = filereader.read_rgb_color_24bpp_uint()
            self.specularColor = filereader.read_rgb_color_24bpp_uint()
            self.normalizedColors = False
        elif gameVer == RSEGameVersions.ROGUE_SPEAR:
            #It's probably a Rogue Spear file
            self.ambientColor = filereader.read_rgba_color_32bpp_float()
            self.diffuseColor = filereader.read_rgba_color_32bpp_float()
            self.specularColor = filereader.read_rgba_color_32bpp_float()
            self.normalizedColors = True
        else:
            print("Unhandled case")
            
        self.specularLevel = filereader.read_float()
        self.twoSidedRaw = filereader.read_bytes(1)
        self.twoSidedRaw = int.from_bytes(self.twoSidedRaw, byteorder='little')
        self.twoSided = False
        if self.twoSidedRaw > 0:
            self.twoSided = True

        self.textureName = self.textureNameRaw[:-1].decode("utf-8")
        self.materialName = self.materialNameRaw[:-1].decode("utf-8")
