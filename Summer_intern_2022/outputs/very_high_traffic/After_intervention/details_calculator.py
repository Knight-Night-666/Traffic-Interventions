#!/usr/bin/env python

from operator import truediv
import os
import sys
import optparse
import pandas as pd
import networkx as nx

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

def check(arr,str1):
    flag=0
    for i in arr:
        if(i==str1):
            flag=1
    if(flag==1):
        return True
    else:
        return False

# contains TraCI control loop
def run():
    step = 0
            
    while step<=3600:
        traci.simulationStep()
        step += 1

    traci.close()
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", 'osm.sumocfg',
                             "--statistic-output", "TripDetails_after"])                       
    run()
