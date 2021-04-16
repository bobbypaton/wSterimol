#!/usr/bin/python
from __future__ import print_function, absolute_import

#Python Libraries
import subprocess, sys, os
from os import listdir
from os.path import isfile, join
import datetime

#Pymol API
from pymol import cmd

########################################
########### S T E R I M O L ############
########################################

# Generate the Sterimol parameters from the optimised structures
# Use in Pymol command prompt:
# run wSterimol.py
# run setup.py
# run sterimoltools.py
# run sterimol.py
# sterimol atomid1, atomid2, (directory, setup_path, verbose)

def Sterimol(atomid1 = "id 1", atomid2 = "id 2", directory = "temp", setup_path = "default", verbose = "False", classic = "False"):
    # If the directory exists
    if os.path.exists(directory):
        # Log generation
        log = Log()
        log.write("\n\n########################################\n########### S T E R I M O L ############\n########################################\n\n")
        # Check arguments to avoid an error later
        if verbose.lower() in ['true', '1', 't', 'y', 'yes']:
            verbose = True
        else:
            verbose = False
        if classic.lower() in ['true', '1', 't', 'y', 'yes']:
            classic = True
        else:
            classic = False
        try:
            atomid1 = int(atomid1.strip().strip('id '))
            atomid2 = int(atomid2.strip().strip('id '))
        except ValueError:
            log.write("FATAL ERROR: An atom ID must be provided for the primary bond. Correct syntax is\n Sterimol id 1, id 2\n You provided atomid1 = %s and atomid2 = %s." % (atomid1, atomid2))
            return False
        # Retrieve all the files in the directory
        files = [f for f in listdir(directory) if isfile(join(directory, f)) and (f.split(".")[-1] == "log" or f.split(".")[-1] == "out") and len(f.split(".")) > 1 ]
        if len(files) > 0:
            # get setup.ini
            setup = Setup(log, setup_path)
            if setup.isLoaded() == True:
                output = open("Sterimol.txt", 'w' )
                output.write("*******************************************************************************\n")
                output.write("**                                                                           **\n")
                output.write("**                             S T E R I M O L                               **\n")
                output.write("**                                                                           **\n")
                output.write("*******************************************************************************\n")
                output.write("* sterimol -a1 %-3s -a2 %-3s -radii %-6s                                      *\n" % (atomid1, atomid2, setup.radii) )
                output.write("* Clusterisation cut-off was set at: %4.2f Angstroms                           *\n" % setup.rmsd_cutoff )
                output.write("* Angle count: %-3.f      | Atomic model: %-5s      | Temperature: %4.f K      *\n" % (setup.angle_count,setup.radii,setup.Temperature))
                output.write("*******************************************************************************\n")
                output.write(" File created on %s | A for Angstroms\n\n" % str(datetime.date.today()))
                message = " Structure                          L1 (A)   B1 (A)   B5 (A) \n"
                output.write(message)
                log.write(message, verbose)
                for filename in files:
                    filesplit = filename.split(".")
                    #prepare the job
                    try:
                        file_Params = calcSterimol(join(directory, filename), setup.radii, atomid1, atomid2, verbose, classic)
                    except ValueError:
                        log.write("FATAL ERROR: An error occured in Sterimol calculation.\n\n%s\n\n" % ValueError)
                        return False
                    if file_Params.lval == None and file_Params.B1 == None and file_Params.newB5 == None:
                        return False
                    lval = file_Params.lval; B1 = file_Params.B1; B5 = file_Params.newB5
                    message = " %-31s " % filename+" %8.2f" % lval+ " %8.2f" % B1+ " %8.2f" % B5
                    log.write(message, verbose)
                    output.write("%s\n" % message)
                output.close()
                log.write("----------------------------\n---- Normal Termination ----\n----------------------------\n")
                log.finalize()
                return True
            else: 
                log.write("Error: Failed to load setup.ini in [%s]. Fix it to continue." % setup_path)
                return False
        else: 
            log.write("Error: No file in the directory [%s]" % directory)
            return False
    else: 
        print("FATAL ERROR: Specified directory doesn't exist [%s]" % directory)
        return False

cmd.extend("sterimol",Sterimol)
