import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile

def Medium(inputs):
    gas = ROOT.Garfield.MediumMagboltz()
    gas.LoadGasFile("Gasfiles/"+inputs[0])
    gas.LoadIonMobility(inputs[0])
    
    return gas

def Component(inputs,gas):
    cmp = None
    if inputs[0] == "COMSOL":
        cmp = ROOT.Garfield.ComponentComsol()
        cmp.Initialise(
            "Comsol/mesh.mphtxt",
            "Comsol/mplist.txt", 
            "Comsol/epot"+inputs[1]+".txt" 
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
    
    return cmp

def Sensor(inputs,cmp):
    sens = ROOT.Garfield.Sensor()
    sens.AddComponent(cmp)
    sens.AddElectrode(cmp,"V")
    wbin = {"Coarse":10,"Normal":5,"Fine":2}
    nbin = int(inputs[0]/wbin[inputs[1]])
    sens.SetTimeWindow(0,wbin[inputs[1]],nbin)
    
    return sens

def Track(inputs,sens,vd):
    track = ROOT.Garfield.TrackSrim()
    track.ReadFile("Srim/"+inputs[0])
    track.SetKineticEnergy(inputs[1]) # eV
    csize = {"Coarse":200,"Normal":50,"Fine":20}
    track.SetTargetClusterSize(csize[inputs[2]]); # 50
    track.EnableTransverseStraggling(inputs[3])
    track.EnableLongitudinalStraggling(inputs[3])
    track.EnablePlotting(vd)
    track.SetSensor(sens)

    return track

def Drift(inputs,sens,vd):
    '''
    inputs = [Mode, Fidelity]
    '''
    drift = None
    
    if inputs[0].lower() == "mc":
        drift = ROOT.Garfield.AvalancheMC()
        
        drift.SetTimeSteps(0.1)
        csteps = {"Coarse":1,"Normal":0.1,"Fine":0.01} # ns
        drift.SetTimeSteps(csteps[inputs[1]])
    
    elif inputs[0].lower() == "micro":
        drift = ROOT.Garfield.AvalancheMicroscopic()
    
    elif inputs[0].lowwer() == "rkf":
        drift = ROOT.Garfield.DriftLineRKF()
        
        stepsize = {"Coarse":0.3/10,"Normal":0.3/15,"Fine":0.3/20}
        drift.SetMaximumStepSize(stepsize[inputs[1]])
    
    else:
        raise Exception("Invalid drift mode. Select from: \"MC\",\"Micro\",\"RKF\".")
    
    drift.SetSensor(sens)
    drift.EnablePlotting(vd)
    
    return drift


if __name__ == '__main__':
    quit()