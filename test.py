import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile as ggf


g = ROOT.Garfield


### The settings/variables that can be imported by reading text file

#blonging to cmp object
gasfile = "ar_100_5bar_25C.gas"
ionfile = "IonMobility_Ar+_Ar.txt"

plot_e_vel = False
plot_ion_vel = False
plot_field = True
plot_mesh = False
#belonging to track object
srimfile = "Alpha_Ar_5bar.txt"

plot_drift = True
plot_signal = True

cmp_type = "COMSOL"
voltage = 200 # check if value is in set of available epots {1400,1200,1000,800,600} more to add?

###


##set up gasious medium class
if not ggf.FileExists(gasfile):
    ggf.GenerateGasFile(gasfile)

gas = g.MediumMagboltz()
gas.LoadGasFile("Gasfiles/"+gasfile)
gas.LoadIonMobility(ionfile)

#plot electron ion drift velocities from gas data
if plot_e_vel:
    c1 = ROOT.TCanvas("c1","",600,600)
    gas.PlotVelocity("e",c1)
if plot_ion_vel:
    c2 = ROOT.TCanvas("c2","",600,600)
    gas.PlotVelocity("i",c2)

##set up the component class
cmp = g.ComponentComsol()
cmp.Initialise(
    "Comsol/mesh.mphtxt",
    "Comsol/mplist.txt", 
    "Comsol/epot"+str(voltage)+".txt" 
)
cmp.SetWeightingPotential(
    "Comsol/wpot.txt",
    "V")
#Set the correct domains to belong to the medium class
nMat = cmp.GetNumberOfMaterials()
for i in range(nMat):
    eps = cmp.GetPermittivity(i)
    if eps == 1.0:
        cmp.SetMedium(i,gas)

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
    vf.SetVoltageRange( -voltage, 0.)
    c3.SetLeftMargin(0.16)
    vf.SetCanvas(c3)
    vf.PlotContour()

##Start Parallelization
sens = g.Sensor()
sens.AddComponent(cmp)
sens.AddElectrode(cmp,"V")
nbin = 400
wbin = 5
sens.SetTimeWindow(0,wbin,nbin)

track = g.TrackSrim()
track.SetSensor(sens)
track.ReadFile("Srim/"+srimfile)
track.SetKineticEnergy(5.3e6) # eV
track.SetTargetClusterSize(25); # 50
track.EnableTransverseStraggling(False)
track.EnableLongitudinalStraggling(False)

drift = g.AvalancheMC()
drift.SetSensor(sens)
drift.SetTimeSteps(0.1)

vd = g.ViewDrift()
if plot_drift:
    drift.EnablePlotting(vd)
    track.EnablePlotting(vd)

#vs = g.ViewSignal()
#if plot_signal:
#    vs.SetSensor(sens)

### Compute Signal

track.NewTrack(0,.149,0.01,0,0,-1,0)

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