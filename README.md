This is the repository to hold educational material for the 2026 VIPER Summer School on PTA GW Astrophysics.

The school runs over two weeks. Material is organized as `Week_<N>/Day_<M>/`, with each day split into `Lectures/` and `Tutorials/`.

```
Week_1/Day_1 ... Day_5
Week_2/Day_1 ... Day_5
```

Interactive browser-based demos that accompany the school live in a separate repository: https://github.com/stevertaylor/viper-2026-summer-school-demos (live at https://stevertaylor.github.io/viper-2026-summer-school-demos/).

# VIPER 2026 — Environment Setup

This project uses [`uv`](https://docs.astral.sh/uv/) to build a self-contained
virtual environment (`.venv`) with everything needed for the summer school,
including JupyterLab.

The one thing `uv` can't install for you is a **system C library, SuiteSparse**,
which `scikit-sparse` (a dependency of `enterprise-pulsar`) compiles against.
Install that first, then run `uv sync`.

---

## 1. Prerequisites

- **git**
- **A C/C++ compiler**
  - macOS: `xcode-select --install`
  - Linux: `sudo apt install build-essential`
- **uv** — install with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## 2. Install SuiteSparse (system dependency)

### macOS (Homebrew)

```bash
brew install suite-sparse
```

Homebrew installs the headers under a non-standard path, so you must tell the
compiler where to find them **for the build step only** (see step 3).

### Linux (Debian/Ubuntu)

```bash
sudo apt install libsuitesparse-dev
```

Headers land in `/usr/include/suitesparse`, which `scikit-sparse` finds
automatically — **no extra environment variables needed** on Linux. Skip the
`export` lines in step 3.

### Any platform (conda alternative — avoids compiling)

If you'd rather not compile `scikit-sparse` at all, install it (and SuiteSparse)
from conda-forge into your active environment *before* syncing:

```bash
conda install -c conda-forge scikit-sparse suitesparse
```

---

## 3. Sync the environment

From the project root:

### macOS

```bash
export CPATH="/opt/homebrew/opt/suite-sparse/include/suitesparse:$CPATH"
export LIBRARY_PATH="/opt/homebrew/opt/suite-sparse/lib:$LIBRARY_PATH"

uv sync --active
```

> On Intel Macs, Homebrew lives at `/usr/local` instead of `/opt/homebrew`.
> Use `$(brew --prefix suite-sparse)` to be safe:
> ```bash
> export CPATH="$(brew --prefix suite-sparse)/include/suitesparse:$CPATH"
> export LIBRARY_PATH="$(brew --prefix suite-sparse)/lib:$LIBRARY_PATH"
> ```

These variables are only needed while compiling (`uv sync`). You don't need them
to *run* anything afterward.

### Linux

```bash
uv sync --active
```

This downloads all dependencies, builds the git-based packages
(`defiant`, `holodeck-gw`, `jug-timing`), and creates `.venv/`. First run takes
a few minutes because several packages compile from source.

---

## 4. Launch JupyterLab

Always launch Jupyter **through the project's environment** so the notebook
kernel points at `.venv`:

```bash
uv run --active jupyter lab
```

The default **Python 3** kernel is already wired to `.venv/bin/python3`, so
`import holodeck`, `enterprise`, `defiant`, `sksparse`, etc. all work inside
notebooks.

### Optional: register a globally-visible kernel

If you prefer to launch Jupyter some other way (e.g. from a base conda env) and
still want this environment available as a kernel choice:

```bash
uv run --active python -m ipykernel install --user \
  --name viper-2026 --display-name "VIPER 2026"
```

It will then appear as **VIPER 2026** in any Jupyter install's kernel list.

---

## 5. Verify it works

```bash
uv run --active python -c "import holodeck, sksparse, enterprise, defiant; print('all imports OK')"
```

Expected output:

```
all imports OK
```

---

## Note on PyTorch

`zuko` requires PyTorch. This environment is pinned to **CPU-only PyTorch** for
everyone: on Linux/Windows it installs from PyTorch's CPU wheel index instead of
the default multi-GB CUDA build; on macOS the standard wheel is already
CPU/MPS-only. No GPU/CUDA setup is required.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'setuptools'` while building `holodeck-gw` | Missing build dependency | Already handled in `pyproject.toml` via `[tool.uv.extra-build-dependencies]`. Make sure you have the latest `pyproject.toml` and do **not** add `no-build-isolation-package` for `holodeck-gw`. |
| `fatal error: 'cholmod.h' file not found` | SuiteSparse not installed, or compiler can't find its headers | Do step 2, and on macOS set the `CPATH`/`LIBRARY_PATH` exports in step 3. |
| `brew --prefix suite-sparse` prints a path but the folder is empty / missing | Stale Homebrew symlink; package not actually installed | Re-run `brew install suite-sparse`. |
| Notebook can't import the packages | Jupyter launched outside the venv | Launch with `uv run --active jupyter lab`, or register the kernel (step 4). |

