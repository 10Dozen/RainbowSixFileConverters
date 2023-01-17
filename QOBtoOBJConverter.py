
import logging

from RainbowFileReaders.QOBModelReader import QOBModelFile

log = logging.getLogger(__name__)

# TODO: Improve logging for async. Add write out to file handler, 
# which outputs txt for each file, and configure logging in each thread.
logging.basicConfig(level=logging.INFO)


def main():
    """Main function that converts test data files"""
    test = QOBModelFile()
    test.read_file(verboseOutput=True,
                   filepath=r"G:\VM_XP_SharedFolder\host_dta\mdl\rsw_sg551.qob"
                   )
    

if __name__ == "__main__":
    main()