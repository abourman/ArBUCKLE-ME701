#!/usr/bin/env bash
set -e

# ----------------------------
# Configuration
# ----------------------------
ENV_NAME="garfield"
GARFIELD_REPO="https://gitlab.cern.ch/garfield/garfieldpp.git"

# ----------------------------
# Check if conda command is available
# ----------------------------
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda is not installed or not on your PATH."
    echo ""
    echo "Please install Miniconda (recommended):"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    echo "After installation, run:"
    echo "  conda init bash"
    echo "  source ~/.bashrc"
    echo "  conda config --add channels conda-forge"
    echo "  conda config --set channel_priority strict"
    echo ""
    echo "Then re-run this script."
    exit 1
fi

# ----------------------------
# Check if environment exists
# ----------------------------
if conda env list | awk '{print $1}' | grep -q "^$ENV_NAME$"; then
    echo "The conda environment '$ENV_NAME' already exists."
    read -p "Do you want to delete and rebuild it? [y/N]: " REPLY

    case "$REPLY" in
        [yY]|[yY][eE][sS])
            echo "Removing environment '$ENV_NAME'..."
            conda remove -y -n "$ENV_NAME" --all
            echo "Environment removed. Rebuilding..."
            ;;
        *)
            echo "Aborting setup. No changes made."
            echo "Activate with:"
	        echo "    conda activate $ENV_NAME"
            exit 0
            ;;
    esac
fi

echo "==> Creating conda environment: $ENV_NAME"
conda config --set channel_priority strict
conda create -c conda-forge --name "$ENV_NAME" root cmake mpi4py # <------------- Add python packages here if needed ------------

echo "==> Activating environment"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# CONDA_PREFIX now points to the environment directory
GARFIELD_HOME="$CONDA_PREFIX/garfieldpp"

echo "==> Preparing Garfield++ directories: $GARFIELD_HOME"
mkdir -p "$GARFIELD_HOME"
cd "$GARFIELD_HOME"
mkdir build install source

# ----------------------------
# Clone and build Garfield++
# ----------------------------

echo "==> Cloning Garfield++"
git clone "$GARFIELD_REPO" "$GARFIELD_HOME/source"

cd "$GARFIELD_HOME/build"

echo "==> Configuring Garfield++ with Cmake"
echo "==> "
cmake -DWITH_EXAMPLES=OFF -DCMAKE_INSTALL_PREFIX="$GARFIELD_HOME/install" "$GARFIELD_HOME/source"

echo "==> Building Garfield++"
make -j "$(nproc)"

echo "==> Installing Garfield++"
make install

# ----------------------------
# Activation / Deactivation scripts
# ----------------------------
echo "==> Installing environment activation scripts"

ACTIVATE_DIR="$CONDA_PREFIX/etc/conda/activate.d"
DEACTIVATE_DIR="$CONDA_PREFIX/etc/conda/deactivate.d"
mkdir -p "$ACTIVATE_DIR" "$DEACTIVATE_DIR"

ACTIVATE_SCRIPT="$ACTIVATE_DIR/activate-garfield.sh"
DEACTIVATE_SCRIPT="$DEACTIVATE_DIR/deactivate-garfield.sh"

# Create activation script
cat > "$ACTIVATE_SCRIPT" <<EOF
#!/bin/bash
source "$(conda info --base)/envs/garfield/garfieldpp/install/share/Garfield/setupGarfield.sh"
EOF

# Create deactivation script
cat > "$DEACTIVATE_SCRIPT" <<EOF
#!/bin/bash
unset GARFIELD_INSTALL
export CMAKE_PREFIX_PATH=\$(echo "\$CMAKE_PREFIX_PATH" | sed "s|\$GARFIELD_HOME/install:||")
export LD_LIBRARY_PATH=\$(echo "\$LD_LIBRARY_PATH" | sed "s|\$GARFIELD_HOME/install/lib:||")
export PYTHONPATH=\$(echo "\$PYTHONPATH" | sed "s|\$GARFIELD_HOME/install/lib/python3.13/site-packages/:||")
EOF

#chmod +x "$ACTIVATE_SCRIPT" "$DEACTIVATE_SCRIPT" #not needed

echo "==> Setup complete!"
echo "Activate with:"
echo "    conda activate $ENV_NAME"
echo "Test evironment with:"
echo "    cd $GARFIELD_HOME/source/Examples/DriftTube"
echo "    python -i mdt.py"


