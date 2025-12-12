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
            "Comsol/epot"+str(inputs[1])+".txt" 
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
    wbin = {"Coarse":20,"Normal":10,"Fine":5}
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

def Source(src_type):
    import math
    
    r = 0.149

    if src_type.lower() == "plated":
        
        phi_max = 0.45*math.pi
        z = 0.01

        rho = r * math.sqrt(ROOT.Garfield.Random.Draw())
        angle = 2*math.pi * ROOT.Garfield.Random.Draw()
        x = rho * math.cos(angle)
        y = rho * math.sin(angle)
        z = z

        # --- 2. Random direction inside a cone facing +z ---
        phi = phi_max * ROOT.Garfield.Random.Draw()     # 0 → phi_max
        theta = 2*math.pi * ROOT.Garfield.Random.Draw()

        dx = math.sin(phi) * math.cos(theta)
        dy = math.sin(phi) * math.sin(theta)
        dz = math.cos(phi) 

    elif src_type.lower() == "collimated":
        
        x_min = -0.05
        x_max = 0.05
        z_min = 0.001
        z_max = 0.15
        phi_max=math.pi * 0.125

        # --- 1. Sample uniformly from the rectangle in (x, z) ---
        x = x_min + (x_max - x_min) * ROOT.Garfield.Random.Draw()
        z = z_min + (z_max - z_min) * ROOT.Garfield.Random.Draw()

        # --- 2. Project onto cylinder using your mapping ---
        # theta = arccos(x / r)
        # X = x
        # Y = r*sin(theta) = sqrt(r^2 - x^2)
        # -> ensures point lies on +y side (Y >= 0)
        theta = math.acos(x / r)
        y = r * math.sin(theta)

        # --- 3. Sample direction inside cone facing -y ---
        phi = phi_max * ROOT.Garfield.Random.Draw()           # 0 → phi_max
        alpha = 2.0 * math.pi * ROOT.Garfield.Random.Draw()   # azimuth

        dx =  math.sin(phi) * math.cos(alpha)
        dy = -math.cos(phi)                       # axis along -y
        dz =  math.sin(phi) * math.sin(alpha)

    else:
        raise Exception("Invalid Source Type")
    
    return [x, y, z, dx, dy, dz]

def Compute(inputs,sens,track,drift):
    import ctypes

    t0 = ctypes.c_double(0.0)
    tstep = ctypes.c_double(0.0)
    nbin = ctypes.c_size_t(0)

    sens.GetTimeWindow(t0, tstep, nbin)
    nbin = nbin.value
    
    x, y, z, dx, dy, dz = Source(inputs[1])
    
    sens.ClearSignal()
    track.NewTrack(x,y,z,t0,dx,dy,dz)

    if inputs[0].lower() == "mc":
        for clstr in track.GetClusters():
            drift.AvalancheElectron(clstr.x,
                                    clstr.y,
                                    clstr.z,
                                    clstr.t,
                                    True,
                                    clstr.n)
            #drift.SetElectronSignalScalingFactor(clstr.n)
            #drift.DriftElectron(clstr.x,clstr.y,clstr.z,clstr.t)

    elif inputs[0].lower() == "micro":
        for clstr in track.GetClusters():
            drift.AvalancheElectron(clstr.x,
                                    clstr.y,
                                    clstr.z,
                                    clstr.t,
                                    0.1,
                                    w = clstr.n)
    #elif inputs[0].lower() == "RKF":
    #    pass
    else:
        # Should never happen
        print("Invalid drift module")
    
    return 0 

if __name__ == '__main__':
    quit()