# Streamlit Community Cloud dependency recovery

Investigated October 14, 2026, on main after merged PR #7. The owner's log excerpt
reports Python **3.14.8**, uv resolving **131 packages**, and a non-zero installer
exit during dependency processing. It does not name a failing package or contain
the first detailed build exception. The exact Cloud failure is therefore **not
confirmed**; dependency resolution alone does not prove successful installation.

## Verified compatibility evidence

The existing project, full dependency lock, CI and `.python-version` target
**Python 3.12**. The original root requirements also installed notebooks, Excel
tools, static plotting and Pytest into the dashboard deployment, although the app
only imports Pandas, Plotly and Streamlit (NumPy is retained as a pinned dependency
of the numerical stack).

Official PyPI release metadata was checked for the existing native package pins:

| Release | Python requirement metadata | CPython 3.12 wheels | CPython 3.14 wheels |
|---|---|---:|---:|
| [Pandas 2.2.3](https://pypi.org/pypi/pandas/2.2.3/json) | >=3.9 | 7 | 0 |
| [NumPy 2.2.3](https://pypi.org/pypi/numpy/2.2.3/json) | >=3.10 | 10 | 0 |
| [Matplotlib 3.10.1](https://pypi.org/pypi/matplotlib/3.10.1/json) | >=3.10 | 6 | 0 |

Wheel counts cover the published platforms, not only Linux. All three releases
also provide source archives. Their minimum-Python metadata does not guarantee
source-build compatibility with every later Python release. A wheels-only uv
resolution targeting 3.14 rejects the Pandas pin because no usable wheel exists.
This probe does **not** reproduce the Cloud installer: it deliberately disables
source builds and runs on a 3.12 host with a 3.14 resolver target.

Thus a **Python-runtime mismatch and required native source builds** are the
leading compatibility explanation for the reported installation failure.
The incomplete Cloud logs cannot establish which build failed, or exclude build
tool, platform, download or resource errors. uv itself is not evidence of a fault:
Streamlit documents its normal attempt to process requirements with uv.

The localhost-only server address was another configuration issue worth removing
for hosted access. It is applied **after installation** and does not explain a
dependency installer exit. Cloud may already override it; the fix leaves address
selection to the platform instead of assuming its startup configuration.

## Minimum changes

- `requirements.txt` contains only the existing Pandas, NumPy, Plotly and Streamlit
  pins needed at runtime. No package version is upgraded.
- `requirements-analysis.txt` includes the runtime plus the ten original analysis,
  notebook, Excel and test pins. All fourteen original direct dependencies remain
  available for project development.
- `requirements-lock.txt` and `.python-version` remain **unchanged**. The full
  validated analysis environment and data lineage are preserved.
- `.streamlit/config.toml` removes only the hard-coded localhost address. Local
  instructions explicitly pass `--server.address 127.0.0.1`; Cloud can manage its
  own bind address. Theme, headless mode and telemetry settings are preserved.
- CI adds a clean Python 3.12 runtime job: uv installs only the root requirements
  with `--no-build`, checks compatibility and renders all six pages. The existing
  full-analysis validation job is retained.

No datasets, record transformations, analytical values or app definitions are
changed. No remote Cloud deployment, deletion or merge is performed.

## Executed checks

| Check | Result |
|---|---|
| Clean Python 3.12.14 uv install of root requirements, `--no-build` | PASS; 39 packages resolved/installed without source compilation |
| `uv pip check` in that clean environment | PASS; all 39 installed packages compatible |
| All six pages through Streamlit AppTest in runtime-only environment | PASS; no rendered exceptions or errors |
| Runtime-only local headless server health endpoint | PASS; HTTP 200 `ok` |
| Pinned source checksums and source occurrence reconciliation | PASS; land 2022: 13,168; land 2024: 6,024; Muscat brokerage 2025: 9,366 |
| Full analysis environment `python -m pip check` | PASS |
| Full `python -m pytest -q` | 118 passed; 14 existing Matplotlib/Pyparsing deprecation warnings |
| Original direct dependencies versus the runtime + analysis files | PASS; same fourteen names/versions, consistent with the existing lock |

Actual Community Cloud Python 3.14.8 installation was not reproduced locally.
The local supported-version result and CI checks do not certify a remote deployment
before the owner recreates it with the supported interpreter.

## After merging

1. Record the failed app's GitHub coordinates, subdomain, access settings and any
   secrets before changing its deployment.
2. Streamlit says an existing app's interpreter cannot be changed in place. Delete
   **the failed Cloud app deployment**, then create it again. Keep the GitHub
   repository and all data files.
3. Select `abeerzanoun/oman-real-estate-market-analysis`, branch `main`, and
   `streamlit_app.py` as the entry point.
4. Open **Advanced settings → Python version**, select **3.12**, save, and deploy.
   Restore the retained subdomain/access settings as appropriate. No app secrets
   are currently required. Do not rely on `.python-version` or an added
   `runtime.txt` to change a deployed interpreter.
5. Confirm the build log shows Python **3.12**, successful dependency installation
   and app startup. Check all six pages. Merging alone or rebooting the existing
   3.14 app does not change its interpreter.
6. If installation still fails, retain the **first package-specific error** above
   the final installer summary, including the package/version and any wheel/build
   traceback. That evidence is needed to determine the remaining cause.

## Authoritative references

- [Select Python in Advanced settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy#optional-configure-secrets-and-python-version)
- [Change an existing app's Python version by deleting/redeploying](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python)
- [Dependency file detection and uv/pip behavior](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

The Streamlit instructions were verified in its official documentation repository
at commit `5cf5f8744e7245b1b7feeaee24112798b93c0c6d`:
[Python recovery source](https://github.com/streamlit/docs/blob/5cf5f8744e7245b1b7feeaee24112798b93c0c6d/content/deploy/community-cloud/manage-your-app/upgrade-python.md)
and [dependency source](https://github.com/streamlit/docs/blob/5cf5f8744e7245b1b7feeaee24112798b93c0c6d/content/deploy/community-cloud/deploy-your-app/app-dependencies.md).
