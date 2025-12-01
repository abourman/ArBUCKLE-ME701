import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile as ggf


g = ROOT.Garfield


### The settings/variables that can be imported by reading text file

gasfile = "ar_93_co2_7_3bar.gas"
ionfile = "IonMobility_Ar+_Ar.txt"

plot_e_vel = True
plot_in_vel = True
plot_field = True

cmp_type = "COMSOL"

###


##set up gasious medium
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

##set
cmp = g.ComponentComsol()