import os
import sys
import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import re

def ValidFilename(filename):
    #returns true if requested filename is valid
    pattern = r'^([A-Za-z0-9]+_\d+_){1,6}\d+bar(_\d+[CKck]{1,1})?\.gas$'
    return re.match(pattern, filename) is not None

def FileExists(filename):
    gas_dir = "Gasfiles"
    path = os.path.join(gas_dir, filename)
    if os.path.exists(path) or os.path.exists(filename):
        return True
    else:
        return False
        

def CheckExitConditions(filename):

    if not ValidFilename(filename):
        print("Invalid file name requested")
        print(
            "Generate New Gas Files: <gas>_<fraction>_<gas2>...<fraction-n>_<pressure>bar_<temp>C.gas"
        )
        sys.exit(0)
    
    gas_dir = "Gasfiles"
    path = os.path.join(gas_dir, filename)
    if FileExists(filename):
        print(f"Gas file already exists: {path}")
        sys.exit(0)

    
    return None

def GenerateGasFile(gasfile, ncoll=11,):
    # Check that the requested gas file is valid and does not already exist
    CheckExitConditions(gasfile)
    
    # Remove extension
    name = gasfile.replace(".gas", "")

    # Split on underscores
    parts = name.split("_")

    gases = []
    fractions = []
    T = None
    p = None

    i = 0
    while i < len(parts):
        token = parts[i].lower()

        # Temperature
        if token.endswith("c"):
            T = float(token[:-1]) + 273.15  # remove C and convert C->K
            i += 1
            continue
        elif token.endswith("k"):
            T = float(token[:-1])
            i += 1
            continue

        # Pressure
        if token.endswith("bar"):
            p = float(token[:-3])  # remove 'bar'
            i += 1
            continue

        # Gas + fraction pair
        gas = token
        frac = float(parts[i + 1])
        gases.append(gas)
        fractions.append(frac)
        i += 2

    # Easier to pad than handle different numbers of gases at magboltz init
    while len(gases) < 6:
        gases.append("")
        fractions.append(0.0)

    # Convert fractions to normalized percentages if needed
    total = sum(fractions)
    fractions = [f / total * 100 for f in fractions]

    # Initialize Magboltz gas media class to set parameters and
    # and compute swarm parameters
    gas = ROOT.Garfield.MediumMagboltz(
        gases[0], fractions[0],
        gases[1], fractions[1],
        gases[2], fractions[2],
        gases[3], fractions[3],
        gases[4], fractions[4],
        gases[5], fractions[5],
    )

    # Temperature
    if T is not None:
        gas.SetTemperature(T)
        gas.EnableThermalMotion(True)
    else:
        name += "_0K"
        
    if len(gases[1]) > 0:
        gas.EnablePenningTransfer()

    # Pressure
    if p is not None:
        gas.SetPressure(p * 760)  # bar → Torr

    
    gas.EnableAutoEnergyLimit(False)
    gas.SetMaxElectronEnergy(50)
    gas.SetFieldGrid(100,50000,20,True)
    #gas.PrintGas()
    
    gas.GenerateGasTable(ncoll)
    
    print("File will be written to:")
    print(f"Gasfiles/{name+".gas"}")
    output_directory = "Gasfiles/" if os.path.exists("Gasfiles") else ""
    gas.WriteGasFile(output_directory+name+".gas")

    return None


if __name__ == "__main__":

    try:
        filename = sys.argv[1]
    except:
        print(
            "Generate New Gas Files: <gas>_<fraction>_<gas2>...<fraction-n>_<pressure>bar_<temp>C.gas"
        )
        print("Available Gases:")
        ROOT.Garfield.MediumMagboltz.PrintGases()
        print(
            "Example: python genGasfile.py ar_93_co2_7_3bar_25C.gas"
        )
        exit(1)
    
    GenerateGasFile(filename)