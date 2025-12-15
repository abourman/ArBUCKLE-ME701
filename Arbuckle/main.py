import sys
import os
import ROOT
import Garfield # pyright: ignore[reportMissingImports]
import Gasfiles.genGasfile
import Arbuckle.Factories as f
from Arbuckle.TxtInput import load_config
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank, size = comm.Get_rank(), comm.Get_size()

if rank > 1:
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)  # stdout
    os.dup2(devnull, 2)  # stderr

if rank == 0:
    # Look for input file on Master
    try:
        filename = sys.argv[1]
        exit_status = False
    except:
        print("No Input File Given")
        print("Use: python test.py input.txt")
        exit_status = True
else:
    exit_status = None
exit_status = comm.bcast(exit_status, root=0)
if exit_status:    
    # Exit on all workers
    MPI.Finalize()
    sys.exit()

if rank == 0:
    cfg = load_config(filename=filename)
    if not Gasfiles.genGasfile.FileExists(cfg["gasfile"]):
        Gasfiles.genGasfile.GenerateGasFile(cfg["gasfile"])
else: 
    cfg = None
# Broadcast configuration to each worker
cfg = comm.bcast(cfg,root=0)

## Set up Garfield Objects on each Worker
## if size is == 1 build on Master
gas = None
cmp = None
sens = None
vd = None
vm = None
track = None
drift = None
if size == 1 or rank != 0:
    if rank <= cfg["n_events"]:
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

# pre-compute plots should only happen for the first worker
# plot electron ion drift velocities from gas data
canvases = []
if (size > 1 and rank == 1) or (size == 1 and rank == 0):
    if cfg["plot_e_vel"]:
        c1 = ROOT.TCanvas("c1","",600,600)
        gas.PlotVelocity("e",c1)
        canvases.append(c1)

    if cfg["plot_ion_vel"]:
        c2 = ROOT.TCanvas("c2","",600,600)
        gas.PlotVelocity("i",c2)
        canvases.append(c2)

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

if size > 1 and rank == 0:
    n_wkrs = size-1
    n_events = cfg["n_events"]
    n_jobs_sent = 0
    n_active_wkrs = 0 
    avg_sig = 0
    one_sig = 0
    hist = []
    

    for rnk in range(1,size):
        if rnk <= n_events:
            comm.isend(1, dest=rnk, tag=1) #True -> compute tag = 1
            n_active_wkrs += 1
        if rnk > n_events:
            comm.isend(0, dest=rnk, tag=0) #False -> brake  tag =0

    while n_active_wkrs > 0:
        # Non-blocking probe for incoming messages
        if comm.Iprobe(source=MPI.ANY_SOURCE, tag=2):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=2)  # tag = 2  {"data":[],"worker:rank"}
            worker = data["worker"]

            if n_jobs_sent % 50 == 0:
                print(f"{n_jobs_sent} of {n_events} events complete")

            if n_jobs_sent < n_events:
                if n_jobs_sent == n_events-1:
                    comm.isend(11,dest=worker,tag=1) # produce post computation plots for last send
                else:
                    comm.isend(1,dest=worker,tag=1)   
                n_jobs_sent += 1
            else:
                comm.isend(0,dest=worker,tag=0)
                n_active_wkrs -= 1
            
            data_a = np.array(data["data"])
            if type(one_sig) != np.ndarray:
                one_sig += data_a
            avg_sig += data_a/n_events
            hist.append(sum(data_a))
    
    if cfg["f_timed_signal"] is not None:
        np.save("Outputs/"+cfg["f_timed_signal"],one_sig)

    if cfg["f_charge_hist"] is not None:
        np.save("Outputs/"+cfg["f_charge_hist"],np.array(hist))

elif rank != 0:
    while True:
        work = comm.recv(source=0,tag=MPI.ANY_TAG)

        if work:
            sig = 0
            vd.Clear()
            sig = f.Compute([cfg["drift_mode"],
                             cfg["src_type"]], sens, track, drift)
            if work == 11:
                if cfg["plot_signal"]:
                    c4 = ROOT.TCanvas("c4","",600,600)
                    sens.PlotSignal("W",c4)
                    canvases.append(c4)

                if cfg["plot_drift"]:
                    c5 = ROOT.TCanvas("c5","",600,600)
                    vd.SetPlane(-1,0,0,0,0,0)
                    vd.SetArea(-.23,-.23, -0.04,.23,.23,0.34)
                    vd.SetCanvas(c5)
                    vd.Plot(True)
                    canvases.append(c5)
            
            comm.isend({"data":sig,"worker":rank},dest=0,tag=2)
        else:
            break
else:
    avg_sig = 0
    one_sig = 0
    hist = []
    n_events = cfg["n_events"]
    
    for i in range(n_events):
        vd.Clear()
        data_a = np.array(f.Compute([cfg["drift_mode"],
                             cfg["src_type"]], sens, track, drift))
        if type(one_sig) != np.ndarray:
            one_sig += data_a
        avg_sig += data_a/n_events
        hist.append(sum(data_a))
        if i % 50 == 0:
            print(f"{i} of {n_events} events complete")
    
    if cfg["plot_signal"]:
        c4 = ROOT.TCanvas("c4","",600,600)
        sens.PlotSignal("W",c4)
        canvases.append(c4)

    if cfg["plot_drift"]:
        c5 = ROOT.TCanvas("c5","",600,600)
        vd.SetPlane(-1,0,0,0,0,0)
        vd.SetArea(-.23,-.23, -0.04,.23,.23,0.34)
        vd.SetCanvas(c5)
        vd.Plot(True)
        canvases.append(c5)

    if cfg["f_timed_signal"] is not None:
        np.save("Outputs/"+cfg["f_timed_signal"],one_sig)

    if cfg["f_charge_hist"] is not None:
        np.save("Outputs/"+cfg["f_charge_hist"],np.array(hist))

if rank == 0:
    input("Press any key to end\n")

comm.Barrier()
MPI.Finalize()
sys.exit(0)