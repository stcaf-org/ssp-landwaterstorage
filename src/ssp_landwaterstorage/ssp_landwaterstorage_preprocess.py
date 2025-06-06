import numpy as np
import csv
import argparse

""" ssp_preprocess_landwaterstorage.py

Code generated 17-09-2019, by Tim Hermans

This script runs the land water storage pre-processing task for the SSP LWS workflow. 
This task generates the data and variables needed to configure the LWS submodel.

Parameters:
scen				The RCP or SSP scenario (default: rcp85) 
dotriangular		Logical 0 or 1, to use triangular distribution for gwd [1,1]
includepokhrel		Logical 0 or 1, to include Pokhrel data for gwd [1,1]
pipeline_id			Unique identifier for the pipeline running this module

Output:
"%PIPELINE_ID%_data.pkl" = Contains the LWS data
"%PIPELINE_ID%_config.pkl" = Contains the configuration parameters

Note: %PIPELINE_ID% is replaced with 'pipeline_id' at run time
"""


def ssp_preprocess_landwaterstorage(
    pophist_file,
    reservoir_file,
    popscen_file,
    gwd_files,
    scen,
    dotriangular,
    includepokhrel,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
    pipeline_id,
):
    ##################################################
    # configure run (could be separate script)
    dgwd_dt_dpop_pcterr = 0.25  # error on gwd slope
    dam_pcterr = 0.25  # error on sigmoidal function reservoirs
    # baseyear = 2005					# Base year to which projetions are centered
    yrs = np.arange(pyear_start, pyear_end + 1, pyear_step)  # target years projections
    yrs = np.union1d(yrs, baseyear)

    # # paths to data
    # pophist_file = "UNWPP2012 population historical.csv"
    # reservoir_file = "Chao2008 groundwater impoundment.csv"
    # gwd_files = ["Konikow2011 GWD.csv", "Wada2012 GWD.csv", "Pokhrel2012 GWD.csv"]
    # popscen_file = "ssp_iam_baseline_popscenarios2100.csv"

    if len(gwd_files) != 3:
        dotriangular = 0

    ##################################################
    # read population history .csv file
    with open(pophist_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        row_count = sum(1 for row in popdata)

    with open(pophist_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        _ = next(popdata)
        i = 0
        t = np.zeros(row_count - 1)
        pop = np.zeros(row_count - 1)

        for row in popdata:
            t[i] = row[0]  # store years
            pop[i] = row[1]  # store population
            i += 1

    t0 = t
    pop0 = pop

    # sample with 5 year steps
    t = t[::5]
    pop = pop[::5]

    ##################################################
    # read reservoir impoundment .csv file
    with open(reservoir_file, "r", newline="") as csvfile:
        damdata = csv.reader(csvfile)
        row_count = sum(1 for row in damdata)

    with open(reservoir_file, "r", newline="") as csvfile:
        damdata = csv.reader(csvfile)
        _ = next(damdata)
        i = 0
        tdams = dams = np.zeros(row_count - 1)
        dams = np.zeros(row_count - 1)

        for row in damdata:
            tdams[i] = row[0]  # store years
            dams[i] = row[1]  # store reservoir impoundment
            i += 1

    ##################################################
    # read groundwater depletion .csv files

    # Define function to count lines in a .csv file
    def countlines(f):
        with open(f, "r", newline="") as csvfile:
            gwddata = csv.reader(csvfile)
            row_count = sum(1 for row in gwddata)
        return row_count

    # Count the lines in all the GWD files
    nlines = [countlines(f) for f in gwd_files]

    # Initialize a multi-dimensional array to store GWD data
    gwd = np.full((len(gwd_files), np.max(nlines)), np.nan)
    tgwd = np.full((len(gwd_files), np.max(nlines)), np.nan)

    for j in np.arange(0, 2 + includepokhrel):  # for different datasets
        path = gwd_files[j]
        with open(path, "r", newline="") as csvfile:
            gwddata = csv.reader(csvfile)
            _ = next(gwddata)
            i = 0

            for row in gwddata:
                tgwd[j, i] = row[0]  # store years
                gwd[j, i] = row[1]  # store gwd
                i += 1

    ##################################################
    # read population scenarios .csv file
    with open(popscen_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        row_count = sum(1 for row in popdata)

    with open(popscen_file, "r", newline="") as csvfile:
        popdata = csv.reader(csvfile)
        _ = next(popdata)
        i = 0
        popscenyr = np.zeros(row_count - 1)
        popscen = np.zeros([row_count - 1, 5])  # 5 SSPs

        for row in popdata:
            popscenyr[i] = row[0]  # store years
            popscen[i, :] = row[1:6]  # store population projections
            i += 1

    ###################################################
    # Store the data in a pickle
    output = {
        "t": t,
        "pop": pop,
        "tdams": tdams,
        "dams": dams,
        "tgwd": tgwd,
        "gwd": gwd,
        "popscen": popscen,
        "popscenyr": popscenyr,
    }

    # Store the configuration in a pickle
    output_conf = {
        "dgwd_dt_dpop_pcterr": dgwd_dt_dpop_pcterr,
        "dam_pcterr": dam_pcterr,
        "yrs": yrs,
        "scen": scen,
        "dotriangular": dotriangular,
        "includepokhrel": includepokhrel,
        "pop0": pop0,
        "t0": t0,
        "baseyear": baseyear,
        "targyears": yrs,
    }

    return output, output_conf


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the land water storage pre-processing stage for the SSP LWS SLR projection workflow",
        epilog="Note: This is meant to be run as part of the SSP LWS module within the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--scenario",
        help="Use RCP or SSP scenario[default=rcp85]",
        choices=[
            "rcp19",
            "rcp26",
            "rcp45",
            "rcp60",
            "rcp70",
            "rcp85",
            "ssp1",
            "ssp2",
            "ssp3",
            "ssp4",
            "ssp5",
        ],
        default="rcp85",
    )
    parser.add_argument(
        "--dotriangular",
        help="Use triangular distribution for GWD [default=0]",
        choices=[0, 1],
        default=0,
        type=int,
    )
    parser.add_argument(
        "--includepokherl",
        help="Include Pokherl data for GWD [default=0]",
        choices=[0, 1],
        default=0,
        type=int,
    )
    parser.add_argument(
        "--baseyear",
        help="Base year to which projections are centered [default=2000]",
        default=2000,
        type=int,
    )
    parser.add_argument(
        "--pyear_start",
        help="Year for which projections start [default=2000]",
        default=2000,
        type=int,
    )
    parser.add_argument(
        "--pyear_end",
        help="Year for which projections end [default=2100]",
        default=2100,
        type=int,
    )
    parser.add_argument(
        "--pyear_step",
        help="Step size in years between pyear_start and pyear_end at which projections are produced [default=10]",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Make sure the base year and target years are within data limits for this module
    if args.baseyear < 2000:
        raise Exception(
            "Base year cannot be less than year 2000: baseyear = {}".format(
                args.baseyear
            )
        )
    if args.baseyear > 2010:
        raise Exception(
            "Base year cannot be greater than year 2010: baseyear = {}".format(
                args.baseyear
            )
        )
    if args.baseyear > 2300:
        raise Exception(
            "Base year cannot be greater than year 2300: baseyear = {}".format(
                args.baseyear
            )
        )
    if args.pyear_start < 2000:
        raise Exception(
            "Projection year cannot be less than year 2000: pyear_start = {}".format(
                args.pyear_start
            )
        )
    if args.pyear_end > 2300:
        raise Exception(
            "Projection year cannot be greater than year 2300: pyear_end = {}".format(
                args.pyear_end
            )
        )

    # Make sure the target year stepping is positive
    if args.pyear_step < 1:
        raise Exception(
            "Projection year step must be greater than 0: pyear_step = {}".format(
                args.pyear_step
            )
        )

    # Run the preprocessing stage with the provided arguments
    ssp_preprocess_landwaterstorage(
        args.scenario,
        args.dotriangular,
        args.includepokherl,
        args.baseyear,
        args.pyear_start,
        args.pyear_end,
        args.pyear_step,
        args.pipeline_id,
    )

    exit()
