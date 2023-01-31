
import logging
import argparse

from RainbowFileReaders.QOBModelReader import QOBModelFile
from RainbowFileReaders.MathHelpers import Vector
from FileUtilities.Settings import load_settings
from FileUtilities import DirectoryProcessor
from FileUtilities import JSONMetaInfo, OBJModelWriter

parser = argparse.ArgumentParser(
                    prog="Rogue Spear QOB to OBJ Converter",
                    description="Parses Rogue Spear QOB file and export model data to OBJ file.",
                    epilog="""This script may be run in bulk (default, converts all .qob files found in the given gamePath) 
                                and specific directory/file mode (use --d or --f key)""")

parser.add_argument("--d",
                    metavar="dirs",
                    help="Directory to search for .qob files.",
                    action='store',
                    nargs='*')

parser.add_argument("--f",
                    metavar="files",
                    help="Path to .qob file that should be converted.",
                    action="store",
                    nargs='*')


log = logging.getLogger(__name__)

# TODO: Improve logging for async. Add write out to file handler, 
# which outputs txt for each file, and configure logging in each thread.
logging.basicConfig(level=logging.INFO)


def convert_QOB(filename):
    """ Reads an QOB file and then writes to OBJ format """
    log.info("Processing: %s", filename)

    modelFile = QOBModelFile()
    modelFile.read_file(verboseOutput=True, filepath=filename)

    meta = JSONMetaInfo.JSONMetaInfo()
    meta.add_info("filecontents", modelFile)
    meta.add_info("filename", filename)
    newFilename = filename + ".JSON"
    meta.writeJSON(newFilename)

    write_OBJ(filename + ".obj", modelFile)
    log.info("===============================================")


def write_OBJ(filename, QOBObject: QOBModelFile):
    log.info("\n\n======== WRITE OBJ ==========================")
    writer = OBJModelWriter.OBJModelWriter()
    writer.open_file(filename)

    try:
        for geoObject in QOBObject.geometryObjects:
            writer.begin_new_object(geoObject.name_string.string)

            # Dump vertices
            log.info("Going to write %d vertices", len(geoObject.vertices))
            for vertex in geoObject.vertices:
                writer.write_vertex(vertex)

            # In QOB vn and vt data is stored in separate meshes
            # These 2 caches will be used to collect and then write vn/vt sections in order
            vnData = []
            vtData = []

            # In QOB faces stored in separate meshes
            # so we need to merge data from all of them
            # This dict will have consolidated data for each face
            facesData = {
                "vIndices": [],
                "vtIndices": [],
                "vnIndices": []
            }

            # UV indices are 0-based per mesh, so we need to add offset for each mesh after the first one
            vnIdxCount = 0
            vtIdxCount = 0

            log.info("Going to write mesh's VN and VT data")
            for mesh in geoObject.meshes:
                log.info("  Mesh %s", mesh)
                log.info("  Face vertex indices: %s", mesh.facesVertices)

                # Vertex indices have continuos numeration, so just adding face's vertex info as is
                for vertexIndices in mesh.facesVertices:
                    log.info("  Map vertex indices to face: %s", vertexIndices)
                    facesData.get("vIndices").append(vertexIndices)

                # VN data is stored in mesh data, need to extract and manually map to specific face
                for vn in mesh.facesNormals:
                    log.info("  Adding vertex normal: %s", vn)
                    vnData.append(vn)  # Exctract VN data

                    log.info("  Map vn to face by index: %s", vnIdxCount)
                    facesData.get("vnIndices").append([vnIdxCount] * 3)  # Map same vn for each 3 face's vertices
                    vnIdxCount += 1

                # VT data is stored in mesh data and VT indices are mesh related
                # Extract VT data
                for vt in mesh.textureUVs:
                    log.info("  Adding UV coordinates: %s", vt)
                    vtData.append(vt)

                # Map vt data to faces, but update vtIndex with offset            
                for textureIndices in mesh.facesTextureIndices:
                    # Add shift to vt index to corespond with merged list of vts
                    shiftedTextureIndices = [(vtIdx + vtIdxCount) for vtIdx in textureIndices]

                    log.info("  Map vt to face. Offset [%d]. vt: %s", vtIdxCount, shiftedTextureIndices)
                    facesData.get("vtIndices").append(shiftedTextureIndices)

                # Update vt index offset
                vtIdxCount += len(mesh.textureUVs)
                log.info(" vtIndex offset now %d", vtIdxCount)

            log.info("Faces data:\n    V: %d\n   VT: %d\n   VN: %d",
                     len(facesData.get("vIndices")),
                     len(facesData.get("vtIndices")),
                     len(facesData.get("vnIndices"))
                     )
            log.info("%s", facesData)

            # Write vn data
            for vn in vnData:
                writer.write_normal(vn)

            # Write vt data
            for vt in vtData:
                writer.write_texture_coordinate(vt)

            # Write faces data: v/vt/vn
            for i in range(len(facesData.get('vIndices'))):
                writer.write_face(
                    vertex_indices=facesData.get("vIndices")[i],
                    texture_coord_indices=facesData.get("vtIndices")[i],
                    normal_indices=facesData.get("vnIndices")[i]
                )

            log.info("Finishing writing .OBJ")

    finally:
        writer.close_file()


def main():
    """Main function that converts test data files"""
    args = parser.parse_args()
    print(args)

    settings = load_settings()
    fp = DirectoryProcessor.DirectoryProcessor()
    fp.fileExt = ".QOB"
    fp.processFunction = convert_QOB

    # No arguments passed -> Read data from game path
    if not args.f and not args.d:
        # TODO: uncomment before final commit
        # fp.paths.append(settings["gamePath"])
        pass

    # Directories was passed -> append to list to find
    if args.d:
        print('Processing directories:')
        for d in args.d:
            print(f'   {d}')
            fp.paths.append(d)
        print()

    # Files was passed -> append to list of files
    if args.f:
        print('Processing files:')
        for f in args.f:
            print(f'   {f}')
            fp.includeFiles.append(f)
        print()

    fp.run(mode=settings["runMode"])


if __name__ == "__main__":
    main()
