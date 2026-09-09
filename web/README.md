# NEXUS AI — Enterprise Operating System (Light/White Theme)

A pure **HTML5, Vanilla CSS, and JavaScript** frontend for the NEXUS AI-Native ERP and Business Operating System.

Designed with an ultra-clean **white / luminous light theme**, modern glassmorphic accents, high-contrast typography, and zero-build deployment.

---

## 🚀 Live Production & Local Previews

1. **Live Production Deployment (Vercel):**
   - URL: [https://nexus-ai-erp-hazel.vercel.app](https://nexus-ai-erp-hazel.vercel.app)
2. **Served directly via FastAPI backend:**
   - URL: [http://127.0.0.1:8000/app/](http://127.0.0.1:8000/app/)
3. **Served via Python static HTTP server:**
   - Run: `make run-web` or `python3 -m http.server 8080 -d web`
   - URL: [http://localhost:8080](http://localhost:8080)
4. **Served via Next.js frontend:**
   - URL: [http://localhost:3000](http://localhost:3000)

---

## 📦 Directory Structure

```text
web/
├── index.html         # Semantic HTML5 executive cockpit & ERP module views
├── style.css          # Vanilla CSS light/white design system (Plus Jakarta Sans + Outfit)
├── app.js             # Reactive client router, API connector, interactive AI Copilot
├── standalone.html    # 100% self-contained single-file bundle (HTML+CSS+JS in one file)
├── deploy.sh          # Interactive deployment script
├── vercel.json        # Vercel deployment configuration
└── netlify.toml       # Netlify deployment configuration
```

---

## 🌐 Deploy to Production (5 Easy Options)

### Option 1: Vercel (1-Click CLI or Drag-and-Drop)
Using Makefile or CLI:
```bash
make deploy-vercel
# Or manually:
cd web && npx vercel --prod
```
*Alternatively, drag and drop the `web` folder onto the [Vercel Dashboard](https://vercel.com/new).*

### Option 2: Netlify (1-Click CLI or Drag-and-Drop)
Using Makefile or CLI:
```bash
make deploy-netlify
# Or manually:
cd web && npx netlify deploy --prod --dir=.
```
*Alternatively, drag and drop the `web` folder into [Netlify Drop](https://app.netlify.com/drop).*

### Option 3: GitHub Pages
1. Push this repository to GitHub.
2. Go to **Repository Settings** > **Pages**.
3. Under **Source**, choose `Deploy from a branch` -> branch `main` / folder `/web`.
4. Click **Save**. Your site will be published at `https://<username>.github.io/<repo>/`.

### Option 4: Cloudflare Pages
1. In Cloudflare Dashboard, go to **Workers & Pages** > **Create application** > **Pages**.
2. Upload the `web/` folder directly or connect GitHub with build output directory `web`.

### Option 5: Single-File Offline / Standalone Distribution
Open `web/standalone.html` directly in any web browser (Chrome, Safari, Edge, Firefox) by double-clicking it. No web server, node, or python required!
