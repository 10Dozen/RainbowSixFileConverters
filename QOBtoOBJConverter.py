
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


def write_OBJ(output_filename, input_modelfile):
    pass


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

    # convert_QOB(filepath=r"G:\VM_XP_SharedFolder\host_dta\mdl\rsw_sg551.qob")
    # test = QOBModelFile()
    # test.read_file(verboseOutput=True,
    #                filepath=r"G:\VM_XP_SharedFolder\host_dta\mdl\rsw_sg551.qob"
    #                )


if __name__ == "__main__":
    main()
