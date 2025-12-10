import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile
import Factories as f

g = ROOT.Garfield


### The settings/variables that can be imported by reading text file

#blonging to cmp object
gasfile = "ar_100_5bar_25C.gas"
ionfile = "IonMobility_Ar+_Ar.txt"

cmp_type = "COMSOL"
voltage = 200 # check if value is in set of available epots {1400,1200,1000,800,600} more to add?

plot_e_vel = False
plot_ion_vel = False
plot_field = True
plot_mesh = False

tmax = 2000 #ns
sim_detail = "Coarse" #{"Coarse","Normal","Fine"} Set w bin and time step for drift MC

drift_mode = "MC"

#belonging to track object
srimfile = "Alpha_Ar_5bar.txt"
trackE = 5.5e6 # eV
straggle = True

plot_drift = True
plot_signal = True
###

if not Gasfiles.genGasfile.FileExists(gasfile):
    Gasfiles.genGasfile.GenerateGasFile(gasfile)

##set up gasious medium class
gas = f.Medium([gasfile,ionfile])
cmp = f.Component([cmp_type,str(voltage)], gas)
sens = f.Sensor([tmax,sim_detail], cmp)

vd = g.ViewDrift()
track = f.Track([srimfile,trackE,sim_detail,straggle], sens, vd)
drift = f.Drift([drift_mode,sim_detail], sens, vd)

#plot electron ion drift velocities from gas data
if plot_e_vel:
    c1 = ROOT.TCanvas("c1","",600,600)
    gas.PlotVelocity("e",c1)

if plot_ion_vel:
    c2 = ROOT.TCanvas("c2","",600,600)
    gas.PlotVelocity("i",c2)

if plot_mesh:
    vm = g.ViewFEMesh()
    vm.SetComponent(cmp)
    vm.SetPlane(0,-1,0,0,0,0)
    vm.SetFillMesh(True)
    vm.SetArea(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
    vm.Plot()

if plot_field:
    c3 = ROOT.TCanvas("c3","",600,600)
    vf = g.ViewField()
    vf.SetComponent(cmp)
    # Set the normal vector of the viewing plane (xz plane).
    vf.SetPlane(-1,0,0,0,0,0)
    # Set the plot limits in the current viewing plane.
    vf.SetArea(-.23,-.23, -0.04,.23,.23,0.34)
    vf.SetVoltageRange(-voltage, 0.)
    c3.SetLeftMargin(0.16)
    vf.SetCanvas(c3)
    vf.PlotContour()

### Compute Signal

track.NewTrack(0,.149,0.1,0,0,-1,0)

#nClstr = track.GetClusters().size()
for clstr in track.GetClusters():
    drift.SetElectronSignalScalingFactor(clstr.n)
    drift.DriftElectron(clstr.x,clstr.y,clstr.z,clstr.t)

#end paralellization but execute below for the first run of only one process
if plot_signal:
    c4 = ROOT.TCanvas("c4","",600,600)
    sens.PlotSignal("V",c4)

if plot_drift:
    c5 = ROOT.TCanvas("c5","",600,600)
    vd.SetPlane(-1,0,0,0,0,0)
    vd.SetArea(-.23,-.23, -0.04,.23,.23,0.34)
    vd.SetCanvas(c5)
    vd.Plot(True)

print(g.Random().Draw())

input("Press any key to quit.")