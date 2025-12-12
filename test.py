import sys
import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile
import Arbuckle.Factories as f
from Arbuckle.TxtInput import load_config

try:
    filename = sys.argv[1]
except:
    print("No Input File Given")
    print("Use: python test.py input.txt")
    exit()
cfg = load_config(filename=filename)

if not Gasfiles.genGasfile.FileExists(cfg["gasfile"]):
    Gasfiles.genGasfile.GenerateGasFile(cfg["gasfile"])

##set up gasious medium class
gas = f.Medium([cfg["gasfile"],
                cfg["ionfile"]])
cmp = f.Component([cfg["cmp_type"],
                   cfg["voltage"]], gas)
sens = f.Sensor([cfg["tmax"],
                 cfg["sim_detail"]], cmp)
vd = ROOT.Garfield.ViewDrift()
track = f.Track([cfg["srimfile"],
                 cfg["trackE"],
                 cfg["sim_detail"],
                 cfg["straggle"]], sens, vd)
drift = f.Drift([cfg["drift_mode"],
                 cfg["sim_detail"]], sens, vd)

#plot electron ion drift velocities from gas data
if cfg["plot_e_vel"]:
    c1 = ROOT.TCanvas("c1","",600,600)
    gas.PlotVelocity("e",c1)

if cfg["plot_ion_vel"]:
    c2 = ROOT.TCanvas("c2","",600,600)
    gas.PlotVelocity("i",c2)

if cfg["plot_mesh"]:
    vm = ROOT.Garfield.ViewFEMesh()
    vm.SetComponent(cmp)
    vm.SetPlane(0,-1,0,0,0,0)
    vm.SetFillMesh(True)
    vm.SetArea(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
    vm.Plot()

if cfg["plot_field"]:
    c3 = ROOT.TCanvas("c3","",600,600)
    vf = ROOT.Garfield.ViewField()
    vf.SetComponent(cmp)
    # Set the normal vector of the viewing plane (xz plane).
    vf.SetPlane(-1,0,0,0,0,0)
    # Set the plot limits in the current viewing plane.
    vf.SetArea(-.23,-.23, -0.04,.23,.23,0.34)
    vf.SetVoltageRange(-cfg["voltage"], 0.)
    c3.SetLeftMargin(0.16)
    vf.SetCanvas(c3)
    vf.PlotContour()

### Compute Signal
f.Compute([cfg["drift_mode"],
           cfg["src_type"]],sens,track,drift)


if cfg["plot_signal"]:
    c4 = ROOT.TCanvas("c4","",600,600)
    sens.PlotSignal("V",c4)

if cfg["plot_drift"]:
    c5 = ROOT.TCanvas("c5","",600,600)
    vd.SetPlane(-1,0,0,0,0,0)
    vd.SetArea(-.23,-.23, -0.04,.23,.23,0.34)
    vd.SetCanvas(c5)
    vd.Plot(True)

input("\nPress any key to quit.")