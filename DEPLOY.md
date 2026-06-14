# Deploying to the Internet (Free)

End result: a public URL like `https://airesume.vercel.app` that anyone can
open from any device.

**Architecture**

```
User browser
   │
   ▼
Vercel  ────────►  React/Vite static build
   │
   │  (fetch calls VITE_API_BASE_URL)
   ▼
Render  ────────►  FastAPI backend
   │
   ▼
Groq API
```

**What you need (all free, ~10 minutes to sign up)**

- GitHub account — <https://github.com/signup>
- Render account — <https://render.com> (sign in with GitHub)
- Vercel account — <https://vercel.com> (sign in with GitHub)
- Your existing Groq API key

---

## Step 1 — Put both halves into one folder

We currently have:

```
D:\AI Resume & Cover Letter Generator\backend\    ← backend
D:\airesume-frontend\                              ← frontend (moved earlier)
```

Render and Vercel deploy from one GitHub repo with subdirectories, so let's
consolidate into a clean folder.

In PowerShell:

```powershell
# 1. Make a fresh deploy folder
New-Item -ItemType Directory -Path D:\airesume-deploy -Force

# 2. Copy backend (skip the venv — it does not deploy)
Copy-Item -Recurse -Force `
  "D:\AI Resume & Cover Letter Generator\backend" `
  "D:\airesume-deploy\backend"
Remove-Item -Recurse -Force "D:\airesume-deploy\backend\.venv" -ErrorAction SilentlyContinue
Remove-Item -Force          "D:\airesume-deploy\backend\.env" -ErrorAction SilentlyContinue

# 3. Copy frontend (skip node_modules)
Copy-Item -Recurse -Force "D:\airesume-frontend" "D:\airesume-deploy\frontend"
Remove-Item -Recurse -Force "D:\airesume-deploy\frontend\node_modules" -ErrorAction SilentlyContinue
Remove-Item -Force          "D:\airesume-deploy\frontend\.env" -ErrorAction SilentlyContinue

# 4. Copy the repo-level files
Copy-Item "D:\AI Resume & Cover Letter Generator\.gitignore"   "D:\airesume-deploy\.gitignore"
Copy-Item "D:\AI Resume & Cover Letter Generator\README.md"    "D:\airesume-deploy\README.md"
Copy-Item "D:\AI Resume & Cover Letter Generator\render.yaml"  "D:\airesume-deploy\render.yaml"
Copy-Item "D:\AI Resume & Cover Letter Generator\DEPLOY.md"    "D:\airesume-deploy\DEPLOY.md"

cd D:\airesume-deploy
```

You should see:

```
D:\airesume-deploy\
├── backend\
├── frontend\
├── render.yaml
├── README.md
├── DEPLOY.md
└── .gitignore
```

## Step 2 — Push to GitHub

```powershell
cd D:\airesume-deploy
git init
git add .
git status        # sanity-check: should NOT list .env or node_modules or .venv
git commit -m "Initial commit"
```

Then on GitHub:

1. Go to <https://github.com/new>.
2. Repository name: `airesume` (or whatever you like). **Public** is fine —
   no secrets are in the code as long as `.env` is `.gitignore`d.
3. **Do not** initialize with README / .gitignore / license — leave it empty.
4. Click **Create repository**.

GitHub shows you a URL like `https://github.com/<you>/airesume.git`. Back in
PowerShell:

```powershell
git branch -M main
git remote add origin https://github.com/<you>/airesume.git
git push -u origin main
```

It will prompt you to sign in via your browser the first time. After that, the
code is on GitHub.

## Step 3 — Deploy the backend on Render

1. Open <https://dashboard.render.com>, sign in with GitHub.
2. Click **New +** → **Blueprint**.
3. Pick the `airesume` repo. Render reads `render.yaml` and shows the
   `airesume-backend` service.
4. Click **Apply**. Render starts building (~3–5 min on first build).
5. Once it says **Live**, the service has a URL like
   `https://airesume-backend.onrender.com`. Click **Environment** in the left
   nav and set:

   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | your Groq key (starts with `gsk_`) |
   | `CORS_ORIGINS` | leave blank for now — we'll fill it after Vercel is up |

6. After saving env vars Render redeploys automatically.
7. Verify: open `https://airesume-backend.onrender.com/api/health` → should
   show `{"ok":true}`.

> **Free-tier caveat.** Render's free instance sleeps after ~15 minutes of
> inactivity. The first request after a sleep takes ~30–60 s to wake up
> (subsequent requests are fast). Acceptable for a personal project.

## Step 4 — Deploy the frontend on Vercel

1. Open <https://vercel.com/new>, sign in with GitHub.
2. Pick the `airesume` repo, click **Import**.
3. Configure:

   | Setting | Value |
   |---|---|
   | Framework Preset | `Vite` (auto-detected) |
   | Root Directory | `frontend` |
   | Build Command | leave default (`npm run build`) |
   | Output Directory | leave default (`dist`) |

4. Expand **Environment Variables** and add:

   | Key | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://airesume-backend.onrender.com` (your Render URL from Step 3) |

5. Click **Deploy**. ~1 minute later you have a URL like
   `https://airesume-xyz.vercel.app`.

## Step 5 — Wire CORS so the two halves can talk

Back in Render → your backend service → **Environment**:

| Key | Value |
|---|---|
| `CORS_ORIGINS` | `https://airesume-xyz.vercel.app` (your Vercel URL) |

(Optional: also set `CORS_ORIGIN_REGEX` to
`^https://airesume-.*\.vercel\.app$` so Vercel preview deployments also work.)

Save → Render redeploys → done.

## Step 6 — Try it

Open your Vercel URL in any browser. Upload a resume, paste a JD, generate.
First request will be slow (Render cold start); subsequent are fast.

---

## Updating later

Whenever you change code locally in `D:\airesume-deploy`:

```powershell
cd D:\airesume-deploy
git add .
git commit -m "Describe what changed"
git push
```

Both Render and Vercel detect the push and auto-redeploy. No further config.

## Troubleshooting

- **Render build fails on WeasyPrint / pango / cairo** — shouldn't happen
  because we use `xhtml2pdf` (pure Python). If you see it, verify
  `requirements.txt` does not list `weasyprint`.
- **Vercel build fails on TypeScript errors** — `npm run build` runs `tsc -b`.
  Fix the type errors locally first (`npm run build` will tell you which).
- **"CORS error" in the browser console** — backend's `CORS_ORIGINS` doesn't
  match the frontend's URL exactly. Copy the URL from the browser bar
  (without trailing slash) into the env var and redeploy.
- **Slow first request** — Render free instance was asleep. Hit `/api/health`
  to warm it up before clicking Generate, or upgrade Render to $7/month
  Starter to keep it always-on.
- **"GROQ_API_KEY is not set"** — env var wasn't saved or you spelled it
  differently. Re-check Render env settings.
