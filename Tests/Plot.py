import re
import matplotlib.pyplot as plt

def parse_time_to_seconds(timestr):
    """Convert 'XmY.s' to seconds."""
    match = re.match(r"(\d+)m([\d.]+)s", timestr.strip())
    if not match:
        raise ValueError(f"Unrecognized time format: {timestr}")
    minutes = int(match.group(1))
    seconds = float(match.group(2))
    return 60 * minutes + seconds


def read_scaling_file(filename):
    nprocs = []
    real_times = []

    current_n = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line.isdigit():
                current_n = int(line)
                continue

            if line.startswith("real") and current_n is not None:
                time_str = line.split()[-1]
                real_sec = parse_time_to_seconds(time_str)

                nprocs.append(current_n)
                real_times.append(real_sec)

                current_n = None

    return nprocs, real_times


def normalize_by_serial(times, nprocs):
    """Normalize times by the NPROCS=1 value."""
    try:
        t1 = times[nprocs.index(1)]
    except ValueError:
        raise RuntimeError("No NPROCS=1 entry found for normalization.")

    return [t / t1 for t in times]


if __name__ == "__main__":
    file1 = "mpi_time_study_1.txt" # 200 Coarse
    file2 = "mpi_time_study.txt"   # 25 Normal

    n1, t1 = read_scaling_file(file1)
    n2, t2 = read_scaling_file(file2)

    t1_norm = normalize_by_serial(t1, n1)
    t2_norm = normalize_by_serial(t2, n2)

    id_x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    id_t = [1/x for x in id_x]


    plt.figure()
    plt.plot(n1, t1_norm, marker="o", label="Coarse")
    plt.plot(n2, t2_norm, marker="s", label="Normal")
    plt.plot(id_x,id_t,'-k',label="Ideal Scailing")

    plt.xlabel("Number of MPI Processes")
    plt.ylabel("Normalized Real Time (T / T₁)")
    #plt.title("MPI Strong Scaling Comparison")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.xlim((0,15))
    plt.ylim((0,1.2))

    #plt.show()
    plt.savefig("MPIScailing.png")

