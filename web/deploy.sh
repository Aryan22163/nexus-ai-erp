#!/bin/bash
set -e

# ==============================================================================
# NEXUS AI Enterprise Operating System - Web Deployment Script
# Light-Themed (White) Pure HTML5 / CSS / Vanilla JS Frontend
# ==============================================================================

echo "================================================================="
echo "  NEXUS AI - Light Themed Frontend Deployment Manager"
echo "================================================================="
echo ""
echo "Choose deployment target:"
echo "  1) Deploy to Vercel (npx vercel --prod)"
echo "  2) Deploy to Netlify (npx netlify deploy --prod)"
echo "  3) Test Locally on http://localhost:8080 (python3 http.server)"
echo "  4) Bundle Standalone Single File (web/standalone.html)"
echo "  5) Deploy via Docker Nginx Container (port 8080)"
echo ""
read -p "Enter choice [1-5]: " choice

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

case $choice in
  1)
    echo "Deploying web/ directory to Vercel..."
    npx -y vercel --prod
    ;;
  2)
    echo "Deploying web/ directory to Netlify..."
    npx -y netlify deploy --prod --dir=.
    ;;
  3)
    echo "Starting local light web server on http://localhost:8080 ..."
    python3 -m http.server 8080
    ;;
  4)
    echo "Generating single-file standalone package..."
    python3 -c '
html = open("index.html").read()
css = open("style.css").read()
js = open("app.js").read()
html = html.replace("<link rel=\"stylesheet\" href=\"style.css\">", f"<style>\n{css}\n</style>")
html = html.replace("<script src=\"app.js\"></script>", f"<script>\n{js}\n</script>")
open("standalone.html", "w").write(html)
print("Saved standalone.html (72KB) - 100% self-contained!")
'
    ;;
  5)
    echo "Running Nginx Docker container..."
    docker run --rm -d -p 8080:80 -v "$DIR":/usr/share/nginx/html:ro --name nexus-light-web nginx:alpine
    echo "NEXUS AI Light Web is live at http://localhost:8080"
    ;;
  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac
