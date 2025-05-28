# Social Support AI Workflow Automation

A fully automated  application that streamlines the social support application process for a government department. From document ingestion (PDFs, images, and tabular data) through eligibility assessment, dynamic recommendations, and an interactive GenAI chatbot—this project showcases end-to-end Data & AI integration.

## Detailed documentation of the solution and Lessons learned - Click the link below

https://docs.google.com/document/d/1P2P26QVD78CSt_0S8Bu9ZovY46vxwGlvbezj5jCExCQ/edit?usp=sharing

---

## ⚙️ Prerequisites

* **Git**
* **Docker & Docker Compose** (v2+)
* **Python 3.9+**
* **Virtualenv** (for an isolated Python environment)

---

## 🛠️ Project Build Process

* `make all`   : Builds Docker images and starts all services (db, ChromaDB, LLM host, API, UI)
* `make clean` : Stops and removes containers & volumes, and deletes the local Python virtual environment

---

## 🚀 Local Setup & Run

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-org/social-support-ai.git
   cd social-support-ai
   ```

2. **Create & activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Build and start the application**

   ```bash
   make clean
   ```

   ```bash
   make all
   ```

   This runs `docker compose up --build`, launching:

   * **PostgreSQL** (service `db`) on port **5432**
   * **ChromaDB** (service `chromadb`)
   * **LLM host** (service `llm`) on port **11434**
   * **API server** (service `api`) on port **8000**
   * **Streamlit UI** (service `ui`) on port ***8501**



---
## 🔍 Check Service Logs

Run:

```bash
docker compose logs -f api
```

You should see output similar to:

```text
api-1  | 2025-05-27 15:37:10,327 INFO [sqlalchemy.engine.Engine] ...
api-1  | 2025-05-27 15:37:10,328 INFO [src.api.main] ✅ Database tables are ready
api-1  | INFO:     Application startup complete.
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Wait about 1 minute for the UI to be available in your browser, then refresh the Streamlit page and press the **Send** button.
---

## 🌐 Access the Application

* **Streamlit UI**:
  [http://localhost:\${UI\_PORT:-8501}](http://localhost:8000)
<img width="904" alt="Screenshot 2025-05-28 at 10 06 45 AM" src="https://github.com/user-attachments/assets/0ead4b8f-8382-4e8c-8697-beb16332d487" />


  • Submit applications, inspect DB entries, and chat with the GenAI bot.

  <img width="808" alt="Screenshot 2025-05-28 at 10 12 18 AM" src="https://github.com/user-attachments/assets/47d3e6cd-097b-4f57-9366-9d982d5a8503" />

---
---
docker compose exec db \
  psql -U postgres -d social_support \
  -c "SELECT * FROM applicants;"  
  
docker compose exec db \
  psql -U postgres -d social_support \
  -c "SELECT * FROM chat_history;"   


---

## 🧹 Tear Down & Cleanup

```bash
make clean
```

This stops all services, removes containers and volumes, and deletes the `.venv` directory.

---

## ✍️ Training ML Models

Place your training CSV at `data/processed/eligibility_training.csv` with columns: `income, family_size, doc_count, label`. Then run:

```bash
python src/models/training.py \
  --input-csv data/processed/eligibility_training.csv \
  --output-model src/models/eligibility_model.pkl
```

This generates `eligibility_model.pkl` for the `EligibilityEngine`.

---

