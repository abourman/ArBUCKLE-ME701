import sys
import numpy as np
import matplotlib.pyplot as plt


def plot_histogram(
    filename,
    bins=100,
    density=False,
    range=None
):
    # Load data
    data = np.load(filename)

    # Flatten in case it isn't strictly 1D
    data = np.asarray(data).ravel()

    # Remove non-finite values (robustness)
    data = data[np.isfinite(data)]

    if data.size == 0:
        raise RuntimeError("No valid data found in file.")
    
    data = abs(data)

    # Plot
    plt.figure()
    plt.hist(data, bins=bins, density=density, range=range)
    plt.xlabel("Induced Charge (fC)")
    plt.xlim((0))
    plt.ylabel("Probability Density" if density else "Counts")
    #plt.title("Induced Charge Distribution")
    plt.grid(True)
    plt.tight_layout()
    #plt.show()
    plt.savefig("Histogram.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python histogram.py data.npy [bins]")
        sys.exit(1)

    filename = sys.argv[1]
    bins = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    plot_histogram(filename, bins=bins)
