# CI/CD Practice Project

A deliberately tiny Python API (FastAPI) wrapped in a real-world pipeline built on **GitHub Actions**.
The app is boring on purpose — the pipeline is what you're here to learn.

```
push / PR ──► CI ──► lint ─┐
                    test ──┼──► docker build + smoke test
               (3 Python   │
                versions) ─┘

tag v1.2.3 ──► CD ──► test ──► build image ──► push to ghcr.io ──► GitHub Release
```

## Project layout

| Path | What it is |
|---|---|
| `app/main.py` | The API: `/health`, `/add`, `/divide` |
| `tests/test_main.py` | Unit tests + API tests |
| `pyproject.toml` | pytest (with 80% coverage gate) and ruff (linter/formatter) config |
| `Dockerfile` | Container image, runs as non-root, has a healthcheck |
| `.github/workflows/ci.yml` | **CI** — runs on every push and pull request to `main` |
| `.github/workflows/cd.yml` | **CD** — runs when you push a version tag like `v1.0.0` |

---

## 1. Run it locally first

Always make sure you can run the pipeline's steps yourself before trusting a robot to do it.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

ruff check .                       # lint
ruff format --check .              # formatting
pytest                             # tests + coverage
uvicorn app.main:app --reload      # then open http://localhost:8000/docs
```

Optional, if you have Docker:

```bash
docker build -t cicd-practice .
docker run -p 8000:8000 cicd-practice
curl http://localhost:8000/health
```

## 2. Put it on GitHub

1. Create a new **empty** repository on GitHub (no README, no .gitignore).
2. In this folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
3. Open the **Actions** tab. You'll see the CI workflow running. Click into it and watch
   `lint` and the three `test` jobs run in parallel, then `docker-build` wait for them.

---

## 3. Exercises

Do these in order. Each one teaches a specific CI/CD concept.

### Exercise 1 — Break the build (CI basics)
Change `test_add` to expect `6`, commit, push. Watch CI go red. Read the log and find the failure.
Fix it and push again.
**Learn:** CI's job is fast, automatic feedback.

### Exercise 2 — Work through a pull request
```bash
git checkout -b feature/multiply
```
Add a `multiply` function and `/multiply` endpoint — but **don't write tests** yet. Push the branch and
open a PR. The coverage gate (`--cov-fail-under=80`) may fail. Add tests until it passes.
**Learn:** CI runs on PRs so problems are caught *before* merging.

### Exercise 3 — Protect `main`
Repo **Settings → Branches → Add branch ruleset** (or "branch protection rule") for `main`:
require a pull request and require the `lint`, `test`, and `docker-build` status checks to pass.
Now try pushing directly to `main` — it should be blocked.
**Learn:** a pipeline only matters if it's enforced.

### Exercise 4 — Read the matrix
Look at the `test` job in `ci.yml`. Add `"3.10"` to the matrix. Does it pass? (Hint: check
`requires-python` in `pyproject.toml`.) Decide whether to support it or remove it.
**Learn:** matrix builds test many environments at once.

### Exercise 5 — Ship a release (CD)
```bash
git tag v1.0.0
git push origin v1.0.0
```
Watch the CD workflow. When it finishes:
- Your repo page will show a **Release** with auto-generated notes.
- Under **Packages** you'll find the image, tagged `1.0.0`, `1.0`, and `latest`.

Pull and run your released image (make the package public in its settings, or `docker login ghcr.io` first):
```bash
docker run -p 8000:8000 ghcr.io/<your-username>/<repo-name>:1.0.0
curl http://localhost:8000/health    # → {"status":"ok","version":"v1.0.0"}
```
**Learn:** CD turns a tagged commit into a versioned, deployable artifact.

### Exercise 6 — Add a manual approval gate
The `publish` job uses `environment: production`. Go to **Settings → Environments → production** and
add yourself as a **required reviewer**. Tag `v1.0.1` and notice the pipeline pauses until you approve.
**Learn:** continuous *delivery* (human approves) vs continuous *deployment* (fully automatic).

### Exercise 7 — Speed it up
Compare run times with and without `cache: pip` in `setup-python`. Then try adding Docker layer caching
to `build-push-action` (`cache-from: type=gha` and `cache-to: type=gha,mode=max`).
**Learn:** fast pipelines get used; slow ones get bypassed.

### Exercise 8 — Actually deploy (stretch goal)
Add a `deploy` job after `publish` that deploys the image to a free host — e.g. Render, Fly.io, or
Google Cloud Run. Store the host's API token as a repo **secret** (Settings → Secrets and variables →
Actions) and reference it with `${{ secrets.YOUR_TOKEN }}`. Finish the job with a smoke test that
curls `/health` on the live URL.
**Learn:** secrets management and post-deploy verification.

---

## Cheat sheet: key GitHub Actions ideas used here

| Concept | Where to see it |
|---|---|
| Triggers (`on:`) | Top of both workflow files |
| Parallel jobs | `lint` and `test` in `ci.yml` |
| Job dependencies (`needs:`) | `docker-build` needs `lint` + `test` |
| Matrix builds | `strategy.matrix` in `ci.yml` |
| Caching | `cache: pip` |
| Artifacts | `upload-artifact` for the coverage report |
| Built-in token & permissions | `GITHUB_TOKEN`, `permissions:` in `cd.yml` |
| Environments & approvals | `environment: production` in `cd.yml` |
| Quality gates | Coverage minimum in `pyproject.toml`, `ruff format --check` |
