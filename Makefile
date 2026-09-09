.PHONY: help install run-backend run-frontend run-web docker-up docker-down test seed lint clean bundle-singlefile deploy-vercel deploy-netlify setup-ollama run-llm

help:
	@echo "NEXUS AI - Development & Deployment Commands:"
	@echo "  make install         Install backend and frontend dependencies"
	@echo "  make run-web         Serve light-themed (white) HTML/CSS/JS frontend on http://localhost:8080"
	@echo "  make run-backend     Run FastAPI dev server on http://127.0.0.1:8000"
	@echo "  make run-frontend    Run Next.js dev server on http://localhost:3000"
	@echo "  make setup-ollama    Install/configure Ollama and pull open-source Llama 3.1"
	@echo "  make run-llm         Run local open-source LLM (Ollama Llama 3.1)"
	@echo "  make bundle-singlefile  Generate single-file self-contained HTML (web/standalone.html)"
	@echo "  make deploy-vercel   Deploy light white web application to Vercel"
	@echo "  make deploy-netlify  Deploy light white web application to Netlify"
	@echo "  make docker-up       Start PostgreSQL, Redis, Backend, Frontend via Docker"
	@echo "  make docker-down     Stop all running containers"
	@echo "  make test            Run backend test suite"
	@echo "  make seed            Populate synthetic enterprise demo data (Nexus Retail)"
	@echo "  make lint            Run linters (Ruff, MyPy)"

setup-ollama:
	@echo "Setting up open-source Ollama and pulling Llama 3.1..."
	@which ollama > /dev/null || (echo "Installing Ollama via brew..." && brew install ollama)
	ollama pull llama3.1

run-llm:
	@echo "Starting open-source Llama 3.1 model via Ollama..."
	ollama run llama3.1


install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

run-web:
	@echo "Serving NEXUS AI Light Website on http://localhost:8080 ..."
	python3 -m http.server 8080 -d web

bundle-singlefile:
	@echo "Bundling web/index.html + style.css + app.js -> web/standalone.html ..."
	python3 -c 'html=open("web/index.html").read().replace("<link rel=\"stylesheet\" href=\"style.css\">", "<style>\n"+open("web/style.css").read()+"\n</style>").replace("<script src=\"app.js\"></script>", "<script>\n"+open("web/app.js").read()+"\n</script>"); open("web/standalone.html", "w").write(html); print("Bundled successfully: web/standalone.html")'

deploy-vercel: bundle-singlefile
	@echo "Deploying web/ directory to Vercel..."
	cd web && npx -y vercel --prod

deploy-netlify: bundle-singlefile
	@echo "Deploying web/ directory to Netlify..."
	cd web && npx -y netlify deploy --prod --dir=.

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

test:
	cd backend && pytest -v

seed:
	cd backend && python -m app.seed

lint:
	cd backend && ruff check .

