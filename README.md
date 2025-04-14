# 🔐 Security Incident Analysis Assistant

An interactive **Streamlit-based AI assistant** for **security incident investigation**. This app combines **LLMs**, **RAG (Retrieval-Augmented Generation)**, and a clean UI to help security analysts analyze incident data effectively.

---

## 📁 Project Structure

```text
.
├── main.py                          # Entry point for the Streamlit app
├── .env                             # Environment variable configuration
├── requirements.txt                 # Python dependencies

├── src/                             # Core application logic
│   ├── __init__.py
│   ├── config.py                    # Environment setup, Streamlit config
│   ├── conversation.py              # Conversational state and logic
│   ├── data_loader.py               # Data loading and preprocessing
│   ├── incident_manager.py          # Incident investigation logic
│   ├── rag_system.py                # RAG pipeline and vector retrieval
│   └── ui.py                        # UI rendering (chat + sidebar)

├── data/                            # Raw or processed incident-related data
│   └── (your CSV/JSON/log files)

├── faiss_index/                     # Vector store index for semantic search
│   ├── index.faiss
│   └── index.pkl

├── README.md                        # Project documentation
```

---

## 🚀 Getting Started

### 1. **Clone the Repository**

```bash
git clone https://github.com/kakarlapudiakhilvarma1/Security-Incident-Analysis.git
cd security-incident-analysis
```

### 2. **Set Up Virtual Environment**

```bash
conda create -p myenv python==3.10 -y
conda activate myenv/   # Windows
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Configure Environment**

Create a `.env` file in the root:

---

## 💻 Running the Application

```bash
streamlit run main.py
```

---

## ⚙️ Features

- 🤖 **LLM-powered Chat Assistant** – Natural language interface for incident analysis
- 📚 **Retrieval-Augmented Generation (RAG)** – Search documents via FAISS index
- 📂 **Incident Data Loader** – Easily pull in logs, CSVs, and structured data
- 🔐 **Modular Codebase** – Clean separation of logic for scalability and maintainability
- 🧠 **Session Management** – Retains conversational context for seamless analysis

---

## 🔧 Core Modules Explained

| Module                    | Purpose                                      |
|---------------------------|----------------------------------------------|
| `config.py`               | Loads environment variables and page settings |
| `conversation.py`         | Manages conversation state and logic         |
| `data_loader.py`          | Handles file loading, parsing, and formatting |
| `incident_manager.py`     | Provides business logic for incident handling |
| `rag_system.py`           | FAISS-powered document retrieval + LLM answer |
| `ui.py`                   | Sidebar and main interface rendering         |
| `faiss_index/`            | Precomputed FAISS and metadata index         |
| `data/`                   | Just given for storing  incidents data --for testing   |

---

## 🧱 Extending the Application

- Add more intelligence in `incident_manager.py` for specific threat scenarios
- Update `rag_system.py` to use other vector stores like Pinecone or Chroma
- Build visual dashboards with Streamlit components

---


## 📜 License

MIT License. See the [LICENSE](LICENSE) file for full terms.

