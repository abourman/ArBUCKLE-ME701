import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile as ggf


g = ROOT.Garfield


### The settings/variables that can be imported by reading text file

gasfile = "ar_100_5bar_25C.gas"
ionfile = "IonMobility_Ar+_Ar.txt"

plot_e_vel = True
plot_in_vel = True
plot_field = True

cmp_type = "COMSOL"
voltage = 600 # check if value is in set of available epots {1400,1200,1000,800,600} more to add?

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
if plot_in_vel:
    c2 = ROOT.TCanvas("c2","",600,600)
    gas.PlotVelocity("i",c2)

##set up the component class
cmp = g.ComponentComsol()
cmp.Initialise(
    "Comsol/mesh.mphtxt",
    "Comsol/mplist.txt", 
    "Comsol/epot"+str(voltage)+".txt", 
    "mm"
)
cmp.SetWeightingPotential(
    "Comsol/wpot.txt",
    "readout")
#Set the correct domains to belong to the medium class
nMat = cmp.GetNumberOfMaterials()
for i in range(nMat):
    eps = cmp.GetPermittivity(i)
    if eps == 1.0:
        cmp.SetMedium(i,gas)

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