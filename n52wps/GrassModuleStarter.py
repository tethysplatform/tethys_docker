################################################################################
# Author:	Soeren Gebbert
#               Parts of this code are from the great pyWPS from Jachym Cepicky:
#               http://pywps.wald.intevation.org/
#
# Copyright (C) 2009 Soeren Gebbert
#               mail to: soerengebbert <at> googlemail <dot> com
#
# License:
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA



# This module needs an input file for processing. All input and output parameter
# are defined within this file. The file parser expects an input file exactly as
# defined below. All key names must be specified.
# New-lines between the key names are forbidden.
#
# The format of the input file is defined as:
#
# [System]
#  WorkDir= temporal created locations and mapsets are put in this directory
#  OutputDir= The output of the grass module is put in tis directory
#
# [GRASS]
#  GISBASE= the gisbase directory of grass
#  GRASS_ADDON_PATH= path to addon modules
#  GRASS_VERSION= the version of grass
#  Module= the name of the module which should be executed
#  LOCATION=(optional, currently not used!)Name of an existing location with an existing mapset PERMANENT, which should be used for processing, the mapsets are generated temporaly
#  LinkInput=TRUE/FALSE Try to link the input into the generated/existing location, default is TRUE
#  IgnoreProjection=TRUE/FALSE Ignore the projection settings when trying to import the input data (ignored if LinkInput is true), default is FALSE
#  UseXYLocation=TRUE/FALSE create only a XY location/mapset and import all data ignoring the projection information. The resolution will be set based on LiteralData or based on the first input raster resolution, default is FALSE  (not implemented)
#
# [ComplexData]
#  Identifier=input
#  MaxOccurs=1
#  PathToFile=/tmp/srtm90.tiff
#  MimeType=text/xml
#  Encoding=UTF-8
#  Schema=http://schemas.opengis.net/gml/3.1.0/polygon.xsd
#
# [LiteralData]
#  Identifier=-p
#  DataType=boolean/integer/double/string
#  Value=true
#
# [ComplexOutput]
#  Identifier=output
#  PathToFile=/tmp/srtm90contour.gml
#  MimeType=text/xml
#  Encoding=UTF-8
#  Schema=http://schemas.opengis.net/gml/3.1.0/polygon.xsd
#

import subprocess
import shutil
from optparse import OptionParser
import os
import os.path
import tempfile
import zipfile

from ParameterParser import *
from GrassSettings import *
from ProcessLogging import *
from ErrorHandler import *

GRASS_LOCATION_NAME = "startLocation"
GRASS_WORK_LOCATION = "workLocation"
GRASS_MAPSET_NAME = "PERMANENT"
# This keyword list contains all grass related WPS keywords
GRASS_WPS_KEYWORD_LIST = ["grass_resolution_ns", "grass_resolution_ew",
                          "grass_band_number", "multi_output"]
# All supported import raster formats
RASTER_MIMETYPES = [{"MIMETYPE":"IMAGE/TIFF", "GDALID":"GTiff"},
                           {"MIMETYPE":"IMAGE/PNG", "GDALID":"PNG"}, \
                           {"MIMETYPE":"IMAGE/GIF", "GDALID":"GIF"}, \
                           {"MIMETYPE":"IMAGE/JPEG", "GDALID":"JPEG"}, \
                           {"MIMETYPE":"IMAGE/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-ERDAS-HFA", "GDALID":"HFA"}, \
                           {"MIMETYPE":"APPLICATION/NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/X-NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-GEOTIFF", "GDALID":"GTiff"}]
# All supported input vector formats [mime type, schema]
VECTOR_MIMETYPES = [{"MIMETYPE":"TEXT/XML", "SCHEMA":"GML", "GDALID":"GML"}, \
                           {"MIMETYPE":"TEXT/XML", "SCHEMA":"KML", "GDALID":"KML"}, \
                           {"MIMETYPE":"APPLICATION/XML", "SCHEMA":"GML", "GDALID":"GML"}, \
                           {"MIMETYPE":"APPLICATION/XML", "SCHEMA":"KML", "GDALID":"KML"}, \
                           {"MIMETYPE":"APPLICATION/DGN", "SCHEMA":"", "GDALID":"DGN"}, \
                           #{"MIMETYPE":"APPLICATION/X-ZIPPED-SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}, \
                           {"MIMETYPE":"APPLICATION/SHP", "SCHEMA":"", "GDALID":"ESRI_Shapefile"}, \
                           {"MIMETYPE":"APPLICATION/DXF", "SCHEMA":"", "GDALID":"DXF"}]
# All supported space time dataset formats
STDS_MIMETYPES = [ {"MIMETYPE":"APPLICATION/X-GRASS-STRDS-TAR", "STDSID":"STRDS", "COMPRESSION":"NO"}, \
                           {"MIMETYPE":"APPLICATION/X-GRASS-STRDS-TAR-GZ", "STDSID":"STRDS", "COMPRESSION":"GZIP"}, \
                           {"MIMETYPE":"APPLICATION/X-GRASS-STRDS-TAR-BZIP", "STDSID":"STRDS", "COMPRESSION":"BZIP2"}, \
                           {"MIMETYPE":"APPLICATION/X-GRASS-STVDS-TAR", "STDSID":"STVDS", "COMPRESSION":"NO"}, \
                           {"MIMETYPE":"APPLICATION/X-GRASS-STVDS-TAR-GZ", "STDSID":"STVDS", "COMPRESSION":"GZIP"}, \
                           {"MIMETYPE":"APPLICATION/X-GRASS-STVDS-TAR-BZIP", "STDSID":"STVDS", "COMPRESSION":"BZIP2"}]

GMS_DEBUG = False

###############################################################################
###############################################################################
###############################################################################

class GrassModuleStarter(ModuleLogging):
    """This class does the following:

     The goal is to process the input data within grass in its own coordinate system without import
       and export

     Main steps are:

     1.) Parse the input file (may be KVP from a WPS execution request)
     2.) Create the new grass location with r.in.gdal or v.in.ogr with the input coordinate system
     3.) Use r.in.gdal/v.in.ogr and v/r.external to import the data into a newly created grass location
     4.) Start the grass module within this location
     5.) Use r.external.out/r.out.gdal and v.out.ogr to export the result data
     6.) Cleanup

     The steps in more detail:
     
     1.) Parse the input parameter and create the parameter map (GISBASE; work dir, ...)
     2.) Create a temporal directory in the work-dir based on temporal directory creation of python
     3.) Create a temporal location and PERMANENT mapset to execute the ogr and gdal import modules
         * Create the environment for grass (GIS_LOCK, GISRC, GISBASE ...)
         * Write the gisrc file in the PERMANENT directory
         * create the WIND and DEFAULT_WIND file in the PERMANENT directory of the new location
     4.) Create a new location/mapset with the coordinate system of the first complex input
         * Use r.in.gdal, t.rast.import or v.in.ogr to create the new location without actually importing the map,
           log stdout and stderr of the import modules
         * Rewrite the gisrc with new location name (we work in PERMANENT mapset)
     5.) Link all other maps via r/v.external(TODO) into the new location, log stdout and stderr
         or import with r.in.gdal or v.in.org. This can be specified in the input file
     6.) Start the grass module, log stdout and stderr, provide the stdout as file
     7.) In case raster output should be created use r.out.gdal or use r.external.out(TODO) to force the direct creation
         of images output files, in case of vector maps export the output with v.out.ogr, 
         space time raster datasets are exported using t.rast.export, log stdout and stderr
     8.) Remove the temporal directory and exit properly

     In case an error occur, return an error code and write the error protocol to stderr
     Create meaningful log files, so the user will be informed properly what was going wrong
     in case of an error

    This Python script is based on the latest grass7 svn version
    """
    ############################################################################
    def __init__(self):

        self.inputFile = None

        self.inputCounter = 0
        self.outputCounter = 0
        # Handling of multi band raster input files
        self.multipleRasterImport = False
        self.multipleRasterProcessing = False
        self.bandNumber = 0

        # These maps are used to create the parameter for the grass command
        self.inputMap = {}
        self.outputMap = {}

        self.moduleStdout = ""
        self.moduleStderr = ""
        # the pid of the process which is currently executed, to be used for suspending
        self.runPID = -1

    ############################################################################
    ############# THIS METHOD DOES ALL THE WORK ################################
    ############################################################################
    def fromInputFile(self, input, logfile, module_output, module_error):
        """This function does all the work and must be called do read the input
        file. It will create the grass location, import the data, run the grass
        module and export the data. At finish all temporal data is removed."""

        self.inputFile = input

        # Initiate the logging mechanism and the logfiles
        ModuleLogging.__init__(self, logfile, module_output, module_error)

        try:
            # Parse the input parameter of the text file
            self.inputParameter = InputParameter(self.logfile)
            try:
                self.inputParameter.parseFile(self.inputFile)
            except:
                log = "Error parsing the input file"
                self.LogError(log)
                raise
            self._createInputOutputMaps()
            try:
                # Temporal directory must be created at the beginning
                self._createTemporalDir(self.inputParameter.workDir)
                self._setUpGrassLocation(self.inputParameter.grassGisBase, self.inputParameter.grassAddonPath)
                # Import all data, run the module and export the data
                # Before import check if zipped shape files are present in input and
                # Extract them and update the input map
                self._checkForZippedShapeFiles()
                # Create the new location based on the first valid input and import all maps
                # and space time datasets
                self._importData()
                # start the grass module one or multiple times, 
                # depending on the multiple import parameter
                self._startGrassModule()
                # now export the results
                self._exportOutput()
            except:
                raise
            finally:
                # Remove any temporary created data
                self._removeTempData()
        except:
            raise
        finally:
            self._closeLogfiles()

    ############################################################################
    def _createInputOutputMaps(self):
        # Create the input parameter of literal data
        self._createLiteralInputMap()
        # Create the output map for data export
        self._createOutputMap()
        # Check if multiple import is defined or a single band
        self._checkBandNumber()

        # In case no band number was provided, we check if the module supports multiple
        # files for each input parameter. If this is not the case, a switch will be set
        # to call the module for each band which was imported
        try:
            self._checkModuleForMultipleRasterInputs()
        except:
            log = "Unable to check for multiple raster inputs"
            self.LogError(log)
            raise

    ############################################################################
    def _createTemporalDir(self, workDir = None):
        """Create a temporary directory for the location and mapset creation"""
        if workDir != None:
            try:
                self.gisdbase = tempfile.mkdtemp(dir = workDir)
            except:
                log = "Unable create a temp-directory"
                self.LogError(log)
                raise
        else:
            try:
                self.gisdbase = tempfile.mkdtemp()
            except:
                log = "Unable create a temp-directory"
                self.LogError(log)
                raise

    ############################################################################
    def _setUpGrassLocation(self, grassGisBase, grassAddonPath):

        try:
            os.mkdir(os.path.join(self.gisdbase, GRASS_LOCATION_NAME))
            os.mkdir(os.path.join(self.gisdbase, GRASS_LOCATION_NAME, GRASS_MAPSET_NAME))
        except:
            raise

        self.fullmapsetpath = os.path.join(self.gisdbase, GRASS_LOCATION_NAME, GRASS_MAPSET_NAME)

        # set the environment variables for grass (Unix system only)
        try:
            self._setEnvironment(grassGisBase, grassAddonPath)
        except:
            raise

        # gisrc and wind file creation
        try:
            self.gisrc = GrassGisRC(self.gisdbase, GRASS_LOCATION_NAME, GRASS_MAPSET_NAME, self.logfile)
            self.gisrc.writeFile(tempdir = self.gisdbase)
            self.gisrcfile = self.gisrc.getFileName()
            self.LogInfo("Created gisrc file " + str(self.gisrcfile))
        except:
            raise

        try:
            self.wind = GrassWindFile(self.gisdbase, GRASS_LOCATION_NAME, GRASS_MAPSET_NAME, self.logfile)
            self.windfile = self.wind.getFileName()
            self.LogInfo("Created WIND file " + str(self.windfile))
        except:
            raise

        try:
            self.var = GrassVARFile(self.gisdbase, GRASS_LOCATION_NAME, GRASS_MAPSET_NAME, self.logfile)
            self.varfile = self.var.getFileName()
            self.LogInfo("Created VAR file " + str(self.varfile))
        except:
            raise

    ############################################################################
    def _checkForZippedShapeFiles(self):
        """ Zipped shape files can not be read by r.in.gdal directly, so we must unzip them
            and set the path and mime type accordingly """
        self.LogInfo("inputs")
        count = 0
        for input in self.inputParameter.complexDataList:
            self.LogInfo("Input file: " + str(input.pathToFile) + "\nMime type: " + str(input.mimeType).upper())
            # Check for zipped shape files
            if input.mimeType.upper() == "APPLICATION/X-ZIPPED-SHP":
                self.LogInfo("Found zipped shape file " + str(input.pathToFile))

                if zipfile.is_zipfile(input.pathToFile) == False:
                    log = "Input: " + input.pathToFile + " is not a zip file"
                    self.LogError(log)
                    raise GMSError(log)

                # Create a new path for each zipped shape file to avoid overwriting
                zpath = os.path.join(self.gisdbase, "input_" + str(count))

                # Create the zfile object
                zfile = zipfile.ZipFile(input.pathToFile)
                # Get the names of the zip file
                namelist = zfile.namelist()

                # Unzip all
                self.LogInfo("Extract zipped shape file to: " + zpath + ".")
                zfile.extractall(zpath)
                zfound = False
                # Set the shape file name for gdal import
                for name in namelist:
                    if name.upper().find(".SHP") >= 0:
                        input.pathToFile = os.path.join(zpath, name)
                        self.LogInfo("Extracted shape file path: " + input.pathToFile)
                        zfound = True
                        break
                # Set the mime type
                input.mimeType = "APPLICATION/SHP"

                if zfound == False:
                    log = "Shape file not found in zip file. Namelist: " + str(namelist)
                    self.LogError(log)
                    raise GMSError(log)

                # Directory counter
                count += 1

    ############################################################################
    def _checkModuleForMultipleRasterInputs(self):
        """ Check if the grass module supports multiple inputs """
        SingleInputCount = 0
        MultipleInputCount = 0
        self.LogInfo("Check for multiple import")
        for input in self.inputParameter.complexDataList:
            if self._isRaster(input):
                if(int(input.maxOccurs) > 1):
                    MultipleInputCount += 1
                else:
                    SingleInputCount += 1

        if MultipleInputCount > 0 and SingleInputCount > 0:
            self.multipleRasterProcessing = True
            self.multipleRasterImport = True
            self.LogInfo("Found Multiple and single inputs")
        elif MultipleInputCount == 0 and SingleInputCount > 0:
            self.multipleRasterProcessing = True
            self.multipleRasterImport = False
            self.LogInfo("Found only single inputs")
        elif MultipleInputCount > 0 and SingleInputCount == 0:
            self.multipleRasterProcessing = False
            self.multipleRasterImport = True
            self.LogInfo("Found only multiple inputs")
        else:
            self.multipleRasterProcessing = False
            self.multipleRasterImport = False
            self.bandNumber = 0
            self.LogInfo("No inputs found")


    ############################################################################
    def _checkBandNumber(self):
        """ Check if a band number is provided as literal data """
        self.LogInfo("Check if a band number is present")
        self.bandNumber = 0
        for i in self.inputMap:
            if i == "grass_band_number" and self.inputMap[i] != "":
                self.bandNumber = int(self.inputMap[i])
                self.LogInfo("Noticed grass_band_number: " + str(self.bandNumber))

        if self.bandNumber == 0:
            self.LogInfo("No band number found")

    ############################################################################
    def _closeLogfiles(self):
        """ Close all logfiles """
        self.logfile.close()
        self.module_output.close()
        self.module_error.close()

    ############################################################################
    def _removeTempData(self):
        """ remove the created temp directory """
        if os.path.isdir(str(self.gisdbase)):
            try:
                self.LogInfo("Remove " + str(self.gisdbase))
                shutil.rmtree(self.gisdbase)
            except:
                log = "Unable to remove temporary grass location " + str(self.gisdbase)
                self.LogError(log)
                raise

    ############################################################################
    def _setEnvironment(self, grassGisBase, grassAddonPath):
        """ Set the grass environment variables"""
        self.genv = GrassEnvironment(self.logfile)
        self.genv.env["HOME"] = "/var/grass/tmp/grass_home"
        self.genv.env["GIS_LOCK"] = str(os.getpid())
        self.genv.env["GISBASE"] = grassGisBase
        self.genv.env["GISRC"] = os.path.join(self.gisdbase, "gisrc")
        self.genv.env["LD_LIBRARY_PATH"] = str(os.path.join(self.genv.env["GISBASE"], "lib"))
        self.genv.env["GRASS_VERSION"] = "7.0.svn"
        self.genv.env["GRASS_ADDON_PATH"] = grassAddonPath
        if os.name != 'posix':
            self.genv.env["PATH"] = str(os.path.join(self.genv.env["GISBASE"], "bin") + ";" + os.path.join(self.genv.env["GISBASE"], "scripts") + ";" + os.path.join(self.genv.env["GISBASE"], "lib") + ";" + os.path.join(self.genv.env["GISBASE"], "extrabin"))
            self.genv.env["PYTHONPATH"] = str(self.genv.env["PYTHONPATH"] + ";" + os.path.join(self.genv.env["GISBASE"], "etc", "python"))
        else:
            self.genv.env["PATH"] = str(os.path.join(self.genv.env["GISBASE"], "bin") + ":" + os.path.join(self.genv.env["GISBASE"], "scripts"))
            self.genv.env["PYTHONPATH"] = str(self.genv.env["PYTHONPATH"] + ":" + os.path.join(self.genv.env["GISBASE"], "etc", "python"))

        self.genv.setEnvVariables()
        self.genv.getEnvVariables()

    ############################################################################
    def _runProcess(self, inputlist):
        """This function runs a process and logs its stdout and stderr output"""

        try:
            self.LogInfo("Run process: " + str(inputlist))
            proc = subprocess.Popen(args = inputlist, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            self.runPID = proc.pid
            self.LogInfo("Process pid: " + str(self.runPID))
            (stdout_buff, stderr_buff) = proc.communicate()
            self.LogInfo("Return code: " + str(proc.returncode))
            self.LogInfo(stdout_buff)
            self.LogInfo(stderr_buff)
        except:
            self.LogError("Unable to execute process: " + str(inputlist))
            raise

        return proc.returncode, stdout_buff, stderr_buff

    ############################################################################
    def _importData(self):
        """Import all ComplexData inputs which are raster, vector or space time dataset files. 
        Take care of multiple inputs and group generation"""
        list = self.inputParameter.complexDataList

        importedInput = None

        # The list may be empty in case no input is provided
        if len(list) == 0:
            return

        if GMS_DEBUG:
            parameter = [self._createGrassModulePath("g.region"), '-p']
            errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

        self.gisrc.printFile()

        # Create a new location based on the first valid raster or vector input 
        success = False

        # In case no complex input is provided use the default XY projection
        if len(list) == 0:
            success = True

        # Check for raster, vector and space time datasets
        # and use the first found to create the location.
        # Location creation without importing the files actually is only
        # supported for raster and space time raster datasets, since
        # raster maps can also be linked as maps
        if success == False:
            for input in list:
                if self._isRaster(input) or self._isVector(input) or self._isSTDS(input):
                    self._createInputLocation(input)
                    # Rewrite the gisrc file to enable the new created location
                    self.gisrc.locationName = GRASS_WORK_LOCATION
                    self.gisrc.rewriteFile()
                    success = True
                    break

        # In case of textual input, use the default location
        if success == False:
            for input in list:
                if self._isTextFile(input):
                    self._createInputLocation(input)
                    success = True
                    break

        # Error if location creation did not work
        if success == False:
            log = "Unsupported MimeType: \"" + str(input.mimeType) + "\". Unable to create input location from input " + str(input.pathToFile)
            self.LogError(log)
            raise GMSError(log)

        # Set the region resolution in case resolution values are provided as literal data
        self._setRegionResolution()

        if GMS_DEBUG:
            parameter = [self._createGrassModulePath("g.region"), '-p']
            errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

        # In case no band number was provided but the input has only one band, 
        # the data will be imported not linked
        link = True
        if self.inputParameter.linkInput == "FALSE":
            link = False
        # Import the files
        for i in list:
            self._importInput(i, link)

    ############################################################################
    def _isRaster(self, input):
        """Check for raster input
        
            @param input A complex input
            @return gdal id
        """
        # self.LogInfo("Check raster mimetype: " + str(input.mimeType.upper()))
        for rasterType in RASTER_MIMETYPES:
            if input.mimeType.upper() == rasterType["MIMETYPE"]:
                self.LogInfo("Raster map is of type " + str(rasterType["MIMETYPE"]))
                return rasterType["GDALID"]
        return None

    ############################################################################
    def _isVector(self, input):
        """Check for vector input. Zipped shapefiles must be extracted
        
            @param input A complex input
            @return the gdal id
        """

        # Adjust the schema definition
        if input.schema == None:
            input.schema = ""

        # self.LogInfo("Check vector mimetype: " + str(input.mimeType.upper()) + " schema: " + str(input.schema.upper()))
        for vectorType in VECTOR_MIMETYPES:
            if input.mimeType.upper() == vectorType["MIMETYPE"] \
               and input.schema.upper().find(vectorType["SCHEMA"]) != -1:
                self.LogInfo("Vector map is of type " + str(vectorType))
                return vectorType["GDALID"]
        return None

    ############################################################################
    def _isSTDS(self, input):
        """Check for space time datasets
        
            @param input A complex input
            @return (stds, compression) the space time dataset type and the compression type as a tuple
        """
        # self.LogInfo("Check space time dataset mimetype: " + str(input.mimeType.upper()))
        for stdsType in STDS_MIMETYPES:
            if input.mimeType.upper() == stdsType["MIMETYPE"]:
                self.LogInfo("Space time dataset is of type " + str(stdsType["MIMETYPE"]))
                return stdsType["STDSID"], stdsType["COMPRESSION"]
        return None

    ############################################################################
    def _isTextFile(self, input):
        """Check for text file input"""
        if input.mimeType.upper() == "TEXT/PLAIN":
            self.LogInfo("Text file recognized")
            return "TXT"
        else:
            return None

    ############################################################################
    def _createInputLocation(self, input):
        """Create a new work location based on an input dataset"""
        self.LogInfo("Creating input location")
        if self._isRaster(input) != None:
            parameter = [self._createGrassModulePath("r.in.gdal"), "input=" + input.pathToFile, "location=" + GRASS_WORK_LOCATION , "-ce", "output=undefined"]
            errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

            if errorid != 0:
                log = "GDLA error while import. Unable to create input location from input " + str(input.pathToFile) + " GDAL log: " + stderr_buff
                self.LogError(log)
                raise GMSError(log)

        elif self._isVector(input) != None:
            parameter = [self._createGrassModulePath("v.in.ogr"), "dsn=" + input.pathToFile, "location=" + GRASS_WORK_LOCATION , "-ie"] 
            errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

            if errorid != 0:
                log = "GDLA error while import. Unable to create input location from input " + str(input.pathToFile) + " OGR log: " + stderr_buff
                self.LogError(log)
                raise GMSError(log)

        elif self._isSTDS(input) != None:
            stype, compression = self._isSTDS(input)
            if stype == "STRDS":
                parameter = [self._createGrassModulePath("t.rast.import"), "input=" + input.pathToFile, "extrdir=unused", "location=" + GRASS_WORK_LOCATION , "-c", "output=undefined"]
                errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
            elif stype == "STVDS":
                # Well this module does not exists actually and needs to be implemented
                parameter = [self._createGrassModulePath("t.vect.import"), "input=" + input.pathToFile, "extrdir=unused", "location=" + GRASS_WORK_LOCATION , "-c", "output=undefined"]
                errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
            else:
                errorid = -1

            if errorid != 0:
                log = "Error while import. Unable to create input location from input " + str(input.pathToFile) + " log: " + stderr_buff
                self.LogError(log)
                raise GMSError(log)

        elif self._isTextFile(input) != None:
            log = "Using XY projection for data processing."
            self.LogError(log)
            return
        else:
            log = "Unsupported MimeType. Unable to create input location from input " + str(input.pathToFile)
            self.LogError(log)
            raise GMSError(log)


    ############################################################################
    def _setRegionResolution(self):
        # Set the region resolution accordingly to the literal input parameters
        values = 0
        ns = 0.0
        ew = 0.0
        for i in self.inputMap:
            if self.inputMap[i] != None or self.inputMap[i] != "NULL":
                if i == "grass_resolution_ns" and self.inputMap[i] != "":
                    self.LogInfo("Noticed grass_resolution_ns")
                    values += 1
                    ns = self.inputMap[i]
                if i == "grass_resolution_ew" and self.inputMap[i] != "":
                    self.LogInfo("Notices grass_resolution_ew")
                    values += 1
                    ew = self.inputMap[i]

                if values == 2:
                    parameter = [self._createGrassModulePath("g.region"), "ewres=" + str(ew), "nsres=" + str(ns)]
                    errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
                    if errorid != 0:
                        log = "Unable to set the region resolution. g.region log: " + stderr_buff
                        self.LogError(log)
                        raise GMSError(log)

    ############################################################################
    def _importInput(self, input, link=False):
        """Import or link raster, vector or space time datasets
           into the grass work location"""
        # Set the input name
        if self.multipleRasterImport == True:
            inputName = input.identifier + "_" + str(self.inputCounter)
        else:
            inputName = input.identifier

        errorid, stdout_buff, stderr_buff = self._runProcess([self._createGrassModulePath("db.connect"), "-d"])

        # import the raster data via gdal
        if self._isRaster(input) != None:
            self.LogInfo("Import raster map " + inputName)
            if link == True:
                parameter = [self._createGrassModulePath("r.external"), "input=" + input.pathToFile, "output=" + inputName]
                if self.inputParameter.ignoreProjection == "TRUE":
                    parameter.append("-o")
                if self.bandNumber > 0:
                    parameter.append("band=" + str(self.bandNumber))
            else:
                parameter = [self._createGrassModulePath("r.in.gdal"), "input=" + input.pathToFile, "output=" + inputName]
                if self.inputParameter.ignoreProjection == "TRUE":
                    parameter.append("-o")
                if self.bandNumber > 0:
                    parameter.append("band=" + str(self.bandNumber))
                else:
                    # Keep band numbers and create a group
                    parameter.append("-k")

            errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

            if errorid != 0:
                if link == True:
                    log = "Unable to link " + inputName + " r.external log: " + stderr_buff
                else:
                    log = "Unable to import " + inputName + " GDAL log: " + stderr_buff
                self.LogError(log)
                raise GMSError(log)

            # Check if r.in.gdal created a group and put these file names into inputName
            if self.bandNumber == 0:
                inputName = self._checkForRasterGroup(inputName)

            if GMS_DEBUG:
                for i in inputName.split(','):
                    parameter = [self._createGrassModulePath("r.info"), i ]
                    errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

        # import the vector data via ogr, linking is not supported
        elif self._isVector(input) != None:
            self.LogInfo("Import vector map " + inputName)
            parameter = [self._createGrassModulePath("v.in.ogr"), "dsn=" + input.pathToFile, "output=" + inputName]
            if self.inputParameter.ignoreProjection == "TRUE":
                parameter.append("-o")

            errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

            if errorid != 0:
                log = "Unable to import " + inputName + " OGR log: " + stderr_buff
                self.LogError(log)
                raise GMSError(log)

            if GMS_DEBUG:
                parameter = [self._createGrassModulePath("v.info"), inputName ]
                errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
                
        # Space time datasets can be imported or linked using the same import module
        elif self._isSTDS(input) != None:
            stype, compression = self._isSTDS(input)
            if stype == "STRDS":
                self.LogInfo("Import space time raster dataset " + inputName)
                # Create a data directory for extraction an linking
                extrdir = tempfile.mkdtemp(dir = self.gisdbase)
                parameter = [self._createGrassModulePath("t.rast.import"),
                                 "input=" + input.pathToFile, "extrdir=" + extrdir,
                                 "output=" + inputName, "-r"]
                if link == True:
                    parameter.append("-l")
                    
                errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

                if errorid != 0:
                    if link == True:
                        log = "Unable to link space time raster dataset " + input.pathToFile + " into the grass mapset" + " t.rast.import log: " + stderr_buff
                    else:
                        log = "Unable to import space time raster dataset " + input.pathToFile + " into the grass mapset" + " t.rast.import log: " + stderr_buff
                    self.LogError(log)
                    raise GMSError(log)
                
        # Text or other input file, no need to create a new name for import, use the path
        # to the file as input for the grass module
        else:
            inputName = input.pathToFile

        self._updateInputMap(input, inputName)

    ############################################################################
    def _checkForRasterGroup(self, inputName):
        """This function checks if inputName is a grass group and returns the
        raster map names of the group as single string connected via ,"""
        names = ""
        parameter = [self._createGrassModulePath("i.group"), "-g", "group=" + inputName]
        (errorid, stdout_buff, stderr_buff) = self._runProcess(parameter)

        if errorid > 0:
            # no group was found, maybe stderr_buff should be parsed for keywords?
            # We return the group name, which is the raster map name
            return inputName
        elif errorid < 0:
            log = "Error while imagery group detection. i.group aborted with an error: " + stderr_buff
            self.LogError(log)
            raise GMSError(log)
        else:
            count = 0
            for i in stdout_buff.split():

                if count > 0:
                    names += "," + str(i)
                else:
                    names = i
                count += 1

        self.LogInfo("Found maps " + names)

        # Currently multi - band input for single inputs is not supported
        if self.multipleRasterProcessing == True and count > 1:
            log = "The process does not support multi - band inputs. Please provide a band number."
            self.LogError(log)
            raise GMSError(log)

        return names

    ############################################################################
    def _updateInputMap(self, input, inputName):
        """ Update the input map and connect the inputs if multiple defined """
        if self.inputMap.has_key(input.identifier):
            self.inputMap[input.identifier] += "," + inputName
        else:
            self.inputMap[input.identifier] = inputName
        self.inputCounter += 1

    ############################################################################
    def _createLiteralInputMap(self):
        """Create the entries of the input map for literal data"""
        list = self.inputParameter.literalDataList

        # The list may be empty
        if len(list) == 0:
            return

        for i in list:
            # Values with no input are ignored
            if i.value != None and i.value != "NULL":
                # Boolean values are unique and have no values eg -p or --o
                if i.type.upper() == "BOOLEAN":
                    if i.value.upper() != "FALSE":
                        self.inputMap[i.identifier] = ""
                # Connect the values if multiple defined
                elif self.inputMap.has_key(i.identifier):
                    self.inputMap[i.identifier] += "," + i.value
                else:
                    self.inputMap[i.identifier] = i.value

    ############################################################################
    def _createOutputMap(self):
        """Create the entries of the output map"""
        list = self.inputParameter.complexOutputList

        # The list may be empty
        if len(list) == 0:
            return

        for i in list:
            # Use the same name as the output in case raster or vector data
            # is set. Otherwise write directly to the output file path
            if self._isRaster(i) != None or self._isVector(i) != None or self._isSTDS(i) != None:
                outputName = i.identifier
            else:
                outputName = i.pathToFile
            # Ignore if multiple defined
            if self.outputMap.has_key(i.identifier):
                pass
            else:
                self.outputMap[i.identifier] = outputName

            self.outputCounter += 1
            
    def _parse_key_val(self, s):
        """!Parse a string into a dictionary, where entries are separated
        by newlines and the key and value are separated by `sep' (default: `=')
    
        @param s string to be parsed
    
        @return parsed input (dictionary of keys/values)
        
        This method was lend from GRASS 7 Python library lib/python/core.py
        """
        result = {}
        sep = "="
    
        if not s:
            return result
        
        lines = s.splitlines()
        
        for line in lines:
            kv = line.split(sep, 1)
            k = kv[0].strip()
            if len(kv) > 1:
                v = kv[1].strip()
            else:
                v = None
                
            result[k] = v
        
        return result

    ############################################################################
    def _exportOutput(self):
        """Export the complex outputs"""
        try:
            for output in self.inputParameter.complexOutputList:
                outputName = self.outputMap[output.identifier]

                # export the data via gdal
                if self._isRaster(output) != None:
                    parameter = [self._createGrassModulePath("r.out.gdal"), "-c", 
                                 "input=" + outputName, "format=" + self._isRaster(output), 
                                 "output=" + output.pathToFile]
                    errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

                    if errorid != 0:
                        log = "Unable to export " + outputName + "   r.out.gdal error:\n" + stderr_buff
                        self.LogError(log)
                        raise GMSError(log)

                # export the data via ogr
                elif self._isVector(output) != None:
                    # First we need to check for empty vectors since v.out.ogr is not able
                    # to export empty maps
                    parameter = [self._createGrassModulePath("v.info"), 
                                 "map=" + outputName, "-t"]
                    errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
                    if errorid != 0:
                        log = "Unable to check vector map " + outputName + "    error:\n" + stderr_buff
                        self.LogError(log)
                        raise GMSError(log)

                    kv = self._parse_key_val(stdout_buff)

                    if kv["primitives"] == '0':
                        # Create an empty file
                        empty_file = open(output.pathToFile, "w")
                        empty_file.close()
                        self.LogWarning("Empty vector map for export detected. Will create an empty file.")
                    else:
                        # Export the vector map
                        parameter = [self._createGrassModulePath("v.out.ogr"), 
                                     "input=" + outputName, "format=" + self._isVector(output), 
                                     "dsn=" + output.pathToFile]
                        self.LogWarning("MUlti output: " +  str(self.inputParameter.multiOutput))
                        
                        if self.inputParameter.multiOutput:
                            parameter.append("-m")
                        errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
    
                        if errorid != 0:
                            log = "Unable to export " + outputName + "   v.out.ogr error:\n" + stderr_buff
                            self.LogError(log)
                            raise GMSError(log)

                # Export the space time dataset
                elif self._isSTDS(output) != None:
                    stype, compression = self._isSTDS(output)

                    if stype == "STRDS":
                        workdir = tempfile.mkdtemp(dir = self.gisdbase)
                        parameter = [self._createGrassModulePath("t.rast.export"), 
                                     "input=" + outputName, "compression=" + compression.lower(), 
                                     "workdir=" + workdir, "output=" + output.pathToFile]
                        errorid, stdout_buff, stderr_buff = self._runProcess(parameter)
                    else:
                        log = "Only space time raster datasets are supported for export\n"
                        self.LogError(log)
                        raise GMSError(log)

                    if errorid != 0:
                        log = "Unable to export " + outputName + "   t.rast.export error:\n" + stderr_buff
                        self.LogError(log)
                        raise GMSError(log)
                    
                # In case stdout was logged, we need to write the content to the output file
                elif output.identifier.lower() == "stdout":
                    try:
                        # Copy the stdout to output.pathToFile
                        self.LogInfo("Write grass module stdout to file: " + output.pathToFile)
                        outFile = open(output.pathToFile, 'w')
                        outFile.write(self.moduleStdout)
                        outFile.close()
                    except:
                        log = "Unable to export " + outputName + " to file: " + output.pathToFile + " with content:\n" + self.moduleStdout
                        self.LogError(log)
                        raise GMSError(log)
                # In case a text or other binary file was created, we do not need to do anything
                # In case the input is not a vector or raster map the output path is used
                # directly for writing
                else:
                    if os.path.isfile(output.pathToFile) == True:
                        pass
                    else:
                        log = "Unable to export " + outputName + ". output file " + output.pathToFile + " was not created"
                        self.LogError(log)
                        raise GMSError(log)
        except:
            log = "Unable to export " + outputName
            self.LogError(log)
            raise

    ############################################################################
    def _createGrassModulePath(self, grassModule):
        """Create the parameter list and start the grass module. Search for grass
        modules in different grass specific directories"""

        if os.name != "posix":
            grassModule = grassModule + ".exe"

        pathList = []

        # Search the module in the bin directory
        grassModulePath = os.path.join(self.inputParameter.grassGisBase, "bin", grassModule)
        pathList.append(grassModulePath)
        self.LogInfo("Looking for ##%s##"%grassModulePath)

        if os.path.isfile(grassModulePath) is not True:
            grassModulePath = os.path.join(self.inputParameter.grassGisBase, "scripts", grassModule)
            pathList.append(grassModulePath)
            self.LogInfo("Looking for " + grassModulePath)
            # if the module was not found in the bin dir, test the script directory
            if os.path.isfile(grassModulePath) is not True:
                grassModulePath = os.path.join(self.inputParameter.grassAddonPath, grassModule)
                pathList.append(grassModulePath)
                self.LogInfo("Looking for " + grassModulePath)
                # if the module was not found in the script dir, test the addon path
                if os.path.isfile(grassModulePath) is not True:
                    log = "GRASS module " + grassModule + " not found in " + str(pathList)
                    self.LogError(log)
                    raise GMSError(log)

        self.LogInfo("GRASS module path is " + grassModulePath)

        return grassModulePath


    ############################################################################
    def _startGrassModule(self):
        """Set all input and output options and start the module"""
        parameter = []
        grassModulePath = self._createGrassModulePath(self.inputParameter.grassModule)
        parameter.append(grassModulePath)

        for i in self.inputMap:
            # filter special WPS keywords from the argument list (resolution, band number, BBOX, ...)
            if i not in GRASS_WPS_KEYWORD_LIST:
                # Check for flags
                if self.inputMap[i] != "":
                    parameter.append(i + "=" + str(self.inputMap[i]))
                else:
                    parameter.append(i)

        for i in self.outputMap:
            # Check for stdout identifier, this should not be added to the parameter list
            if i.lower() != "stdout":
                parameter.append(i + "=" + self.outputMap[i])

        errorid, stdout_buff, stderr_buff = self._runProcess(parameter)

        self.moduleStdout = stdout_buff
        self.moduleStderr = stderr_buff

        self.LogModuleStdout(stdout_buff)
        self.LogModuleStderr(stderr_buff)

        if errorid != 0:
            log = "Error while executing the grass module. The following error message was logged:\n" + stderr_buff.replace("<", "&#60;").replace(">", "&#62;")
            self.LogError(log)
            raise GMSError(log)

###############################################################################
###############################################################################
###############################################################################

def main():
    """The main function which will be called if the script is executed directly"""

    usage = "usage: %prog [-help,--help] --file inputfile.txt [--logfile log.txt] [--module_output mout.txt] [--module_error merror.txt]"
    description = "Use %prog to process geo-data with grass without the need to explicitely " + \
                  "generate a grass location and the import/export of the input and output geo-data. " + \
                  "This may helpful for WPS server or other web services providing grass geo-processing."
    parser = OptionParser(usage = usage, description = description)
    parser.add_option("-f", "--file", dest = "filename",
                      help = "The path to the input file", metavar = "FILE")
    parser.add_option("-p", "--printmime", dest = "printmime",
                      help = "Print supported input and output mime types and exit.")
    parser.add_option("-l", "--logfile", dest = "logfile", default = "logfile.txt", \
                      help = "The name to the logfile. This file logs everything "\
                      "which happens in this module (import, export, location creation ...).", metavar = "FILE")
    parser.add_option("-o", "--module_output", dest = "module_output", default = "logfile_module_stdout.txt",
                      help = "The name to the file logging the messages to stdout "\
                      "of the called grass processing module (textual module output).", metavar = "FILE")
    parser.add_option("-e", "--module_error", dest = "module_error", default = "logfile_module_stderr.txt", \
                      help = "The name to the file logging the messages to stderr"\
                      " of the called grass processing module (warnings and errors).", metavar = "FILE")

    (options, args) = parser.parse_args()

    if options.printmime != None:
        print "Supported raster mime types: "
        print RASTER_MIMETYPES
        print "Supported vector mime types: "
        print VECTOR_MIMETYPES
        exit(0)

    if options.filename == None:
        parser.print_help()
        parser.error("A file name must be provided")

    starter = GrassModuleStarter()
    starter.fromInputFile(options.filename, options.logfile, options.module_output, options.module_error)
    exit(0)

###############################################################################
if __name__ == "__main__":
    main()
