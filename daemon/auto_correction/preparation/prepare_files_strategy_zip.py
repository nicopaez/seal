from auto_correction.preparation.prepare_files_strategy import PrepareFilesStrategy
from zipfile import ZipFile
from auto_correction.exceptions.illegal_state_exception import IllegalStateException
from auto_correction.log.logger_manager import LoggerManager
import os

class PrepareFilesStrategyZip(PrepareFilesStrategy):
    """
    
    Strategy meant to obtain the files to be "auto-checked" from a zip file uploaded to the app.
    
    """


    def __init__(self):
        """Initializes the zip file path to None"""
        self.zip = None
        self.log = LoggerManager().get_new_logger("preparation")
    
    def prepare_files(self, destination_path):
        self.log.debug("preparing files for automatic correction process...")
        if (self.zip is None):
            raise IllegalStateException(reason="In order to prepare the files by unzipping them, you must set the zip file as source.\
                                                Try setting the zip attribute for this object.")
        zipfile = ZipFile(self.zip)
        zipfile.extractall(destination_path)
        
        self.log.debug("\n\nWalking destination path...")
        for path, directories, files in os.walk(destination_path):
            self.log.debug("path: %s", path)
            for directory in directories:
                self.log.debug("directory: %s", directory)
            for a_file in files:
                self.log.debug("file: %s", a_file)
        self.log.debug("\n\n")
        
        self.log.debug("zip file extracted to %s.", destination_path)
    