# OLD Environment Setup
This is the repository to hold educational material for the 2026 VIPER Summer School on PTA GW Astrophysics.

The school runs over two weeks. Material is organized as `Week_<N>/Day_<M>/`, with each day split into `Lectures/` and `Tutorials/`.

```
Week_1/Day_1 ... Day_5
Week_2/Day_1 ... Day_5
```

Interactive browser-based demos that accompany the school live in a separate repository: https://github.com/stevertaylor/viper-2026-summer-school-demos (live at https://stevertaylor.github.io/viper-2026-summer-school-demos/).

How to install the PTA software (and its dependencies) on a LINUX machine:

  0) Install [Anaconda](https://docs.anaconda.com/anaconda/install/)
  1) `conda create -n viper -y -c conda-forge python=3.9`
  2) `conda activate viper`
  3) `conda install -y -c conda-forge enterprise-pulsar enterprise_extensions`
  4) `conda install -y -c conda-forge nb_conda jupyterlab`
  5) `pip install la-forge`
  6) `pip install tqdm`
  7) `pip install git+https://github.com/GersbachKa/defiant`

How to install the PTA software (and its dependencies) on a new MAC (M-series) machine:

  0) Install [Anaconda](https://docs.anaconda.com/anaconda/install/)
  1) `CONDA_SUBDIR=osx-64`
  2) `conda create -n viper -y -c conda-forge python=3.9`
  3) `conda activate viper`
  4) `conda config --env --set subdir osx-64`
  5) `conda install -y -c conda-forge enterprise-pulsar enterprise_extensions`
  6) `conda install -y -c conda-forge nb_conda jupyterlab`
  7) `pip install la-forge`
  8) `pip install tqdm`
  9) `pip install git+https://github.com/GersbachKa/defiant`

How to install the PTA software (and its dependencies) on a Windows machine:
  1) Use [WSL](https://learn.microsoft.com/en-us/windows/wsl/about) to install a LINUX instance on your Windows machine.
  2) Follow the instructions for LINUX. The software will not run on Windows natively!

To install [`holodeck`](https://github.com/nanograv/holodeck):

  0) Install [Anaconda](https://docs.anaconda.com/anaconda/install/) (or, better yet, [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)) and `git`.  Use either `conda` or `mamba` below, depending on which you have.
  1) Clone the repository and work in the dev branch
  
```bash
git clone https://github.com/nanograv/holodeck.git
cd holodeck
git switch dev
```

  2) Create the environment and install all dependencies.
  
```bash
mamba env create -f environment.yml       # fast; use `conda` if you prefer
mamba activate holopy
nbstripout --install
git config filter.nbstripout.extrakeys 'metadata.kernelspec metadata.language_info.version'
```

  3) If you later edit a `.pyx` file, rerun `pip install -e . --no-deps` to rebuild the C extensions.

