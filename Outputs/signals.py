import sys
import numpy as np
import matplotlib.pyplot as plt


def plot_signal(
    filename,
    t_max=2000.0,
    dt=None
):
    """
    filename : .npy file with current samples [fC/ns]
    t_max    : maximum time in ns (default 2000 ns)
    dt       : optional time step in ns (if None, inferred)
    """

    # Load data
    current = np.load(filename)
    current = np.asarray(current).ravel()

    if current.size == 0:
        raise RuntimeError("Empty waveform.")

    current = abs(current)

    # Infer dt if not provided
    if dt is None:
        dt = t_max / current.size

    # Time axis
    time = np.arange(current.size) * dt

    # Trim to t_max
    mask = time <= t_max
    time = time[mask]
    current = current[mask]

    # Accumulated charge (discrete integral)
    # current [fC/ns] * dt [ns] → fC
    charge = np.cumsum(current * dt)

    # ---- Plot with twin y-axis ----
    fig, ax1 = plt.subplots()

    ax1.plot(time, current, label="Current")
    ax1.set_xlabel("Time (ns)")
    ax1.set_ylabel("Induced Current ($\mu$A)")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(time, charge, linestyle="--", label="Accumulated Charge")
    ax2.set_ylabel("Accumulated Charge (fC)")

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right")

    #plt.title("Induced Current and Accumulated Charge vs Time")
    fig.tight_layout()
    plt.savefig("Signal.png")
    #plt.show()

    # ---- Plot current ----
    #plt.figure()
    #plt.plot(time, current)
    #plt.xlabel("Time (ns)")
    #plt.ylabel("Induced Current ($\mu$A)")
    #plt.grid(True)
    #plt.tight_layout()

    # ---- Plot accumulated charge ----
    #plt.figure()
    #plt.plot(time, charge)
    #plt.xlabel("Time (ns)")
    #plt.ylabel("Accumulated Charge (fC)")
    #plt.title("Accumulated Induced Charge vs Time")
    #plt.grid(True)
    #plt.tight_layout()

    #plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python signals.py waveform.npy [t_max] [dt]")
        sys.exit(1)

    filename = sys.argv[1]
    t_max = float(sys.argv[2]) if len(sys.argv) > 2 else 2000.0
    dt = float(sys.argv[3]) if len(sys.argv) > 3 else None

    plot_signal(filename, t_max=t_max, dt=dt)
