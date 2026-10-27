# AI Research Paper Assistant 📚🤖

An AI-powered application that helps users research academic topics, discover relevant research papers, read PDF documents, and generate research summaries and reports.

## ✨ Features

- 🔍 **Research Assistance:** Helps users explore academic topics and research questions.
- 📄 **Research Paper Discovery:** Uses arXiv tools to find relevant academic papers.
- 📖 **PDF Reading:** Supports reading and extracting information from PDF documents.
- 🤖 **AI-Powered Analysis:** Assists with understanding research papers and generating useful insights.
- 📝 **PDF Report Generation:** Generates research reports in PDF format.
- 🌐 **User Interface:** Provides a frontend for interacting with the research assistant.

## 🛠️ Technologies Used

- Python
- AI/LLM API
- arXiv API or tools
- PDF processing libraries
- Python dependency management with `uv`

*Add the specific AI provider, libraries, and frontend framework used by your project.*

## 📂 Project Structure

```text
AI_Researcher/
├── src/
│   └── ai_researcher/
├── output/
├── ai_researcher.py
├── ai_researcher_2.py
├── arxiv_tool.py
├── frontend.py
├── generate_pdf.py
├── read_pdf.py
├── write_pdf.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/zohra-codes/ai-research-paper-assistant.git
```

### 2. Navigate to the project directory

```bash
cd ai-research-paper-assistant
```

### 3. Install dependencies

Make sure Python and `uv` are installed. Then run:

```bash
uv sync
```

This installs the dependencies defined by the project.

### 4. Configure environment variables

Create a `.env` file in the project root directory and add the API key required by the application.

```env
GOOGLE_API_KEY=your_api_key_here
```

Replace `YOUR_API_KEY_NAME` with the exact environment variable name used in your Python code, and replace `your_api_key_here` with your own API key.

**Security:** Never publish your actual API key or commit your `.env` file to GitHub.

## ▶️ Usage

Run the command appropriate for your application's frontend.

If your project uses Streamlit and `frontend.py` is the correct entry point, run:

```bash
uv run streamlit run frontend.py
```

If your application uses a different framework or entry point, use the appropriate command.

## 🔐 Security

- Keep API keys and credentials private.
- Store secrets in environment variables or a local `.env` file.
- Ensure `.env` is included in `.gitignore`.
- Never commit API keys, passwords, or other sensitive information to version control.
- Use your own API credentials when required.

## 🚧 Future Improvements

- Improve research paper ranking and filtering.
- Add paper citations and reference management.
- Enhance summaries with source references.
- Add support for more document formats.
- Improve the user interface and error handling.

## 👩‍💻 Author

**Zohra**

GitHub: [@zohra-codes](https://github.com/zohra-codes)

## 📄 License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software under the terms of the license.
