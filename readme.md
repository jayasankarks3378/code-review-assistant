# Code Review Assistant

An AI-powered Python code review assistant that combines deterministic static analysis with a locally hosted Large Language Model to generate clear, structured, and actionable review feedback.

The application uses Ruff and Bandit to identify code-quality and security findings, then supplies those findings as structured context to a local Ollama model. The generated response is validated with Pydantic before being presented as a Markdown or JSON report.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/jayasankarks3378/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb
)

## Features

* Reviews Python source files of up to 500 lines
* Detects common bugs and code-quality issues using Ruff
* Detects potential security vulnerabilities using Bandit
* Generates contextual explanations using a local LLM
* Keeps reviewed source code on the local machine
* Validates LLM output against a strict JSON contract
* Produces Markdown and JSON reports
* Provides a command-line interface
* Supports configurable Ollama models and timeouts
* Handles partial analyzer failures gracefully
* Includes unit, integration, CLI, and performance tests

## Project Architecture

The project follows a modular-monolith architecture with dependency injection and clearly separated responsibilities.

```text
Python Source File
        │
        ▼
   PythonParser
        │
        ▼
  AnalysisService
   ┌────┴─────┐
   ▼          ▼
RuffAnalyzer BanditAnalyzer
   │          │
   └────┬─────┘
        ▼
 AnalysisResult
        │
        ▼
ReviewPromptBuilder
        │
        ▼
     BaseLLM
   ┌────┴─────┐
   ▼          ▼
 MockLLM    OllamaLLM
        │
        ▼
ReviewResponseParser
        │
        ▼
  ReviewResponse
        │
        ▼
   ReportService
   ┌────┴─────┐
   ▼          ▼
 Markdown    JSON
```

### Main Components

| Component              | Responsibility                                                    |
| ---------------------- | ----------------------------------------------------------------- |
| `PythonParser`         | Validates Python syntax and source-file size                      |
| `RuffAnalyzer`         | Detects style, readability, performance, and bug-related findings |
| `BanditAnalyzer`       | Detects potential Python security vulnerabilities                 |
| `AnalysisService`      | Executes analyzers and combines normalized findings               |
| `ReviewPromptBuilder`  | Creates structured LLM prompts from source and findings           |
| `BaseLLM`              | Defines the common interface for LLM providers                    |
| `MockLLM`              | Provides deterministic responses for automated testing            |
| `OllamaLLM`            | Communicates with a locally running Ollama server                 |
| `ReviewResponseParser` | Validates raw LLM responses using Pydantic                        |
| `ReviewService`        | Coordinates prompt creation, model generation, and validation     |
| `ReportService`        | Generates and optionally saves Markdown or JSON reports           |
| `ApplicationContainer` | Creates and wires application dependencies                        |
| CLI                    | Accepts user input and invokes the complete review workflow       |

## Technology Stack

* Python 3.11 or later
* Ruff
* Bandit
* Ollama
* Qwen2.5-Coder
* Pydantic
* Pydantic Settings
* Typer
* Rich
* pytest
* Black
* requests

## Repository Structure

```text
code-review-assistant/
├── app/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── examples/
├── tests/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── integration/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── performance/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── docs/
├── notebooks/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following before running the project:

* Python 3.11 or later
* Git
* Ollama

Confirm the installations:

```bash
python --version
git --version
ollama --version
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jayasankarks3378/code-review-assistant.git
cd code-review-assistant
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install an Ollama model

```bash
ollama pull qwen2.5-coder:3b
```

Confirm that the model is available:

```bash
ollama list
```

### 5. Configure the application

Copy the example environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Default configuration:

```dotenv
CODE_REVIEW_OLLAMA_BASE_URL=http://localhost:11434
CODE_REVIEW_OLLAMA_MODEL=qwen2.5-coder:3b
CODE_REVIEW_OLLAMA_TIMEOUT_SECONDS=120
CODE_REVIEW_MAX_SOURCE_LINES=500
CODE_REVIEW_MAX_PROMPT_FINDINGS=50
CODE_REVIEW_ALLOW_EXTERNAL_API=false
CODE_REVIEW_LOG_LEVEL=INFO
```

The `.env` file is ignored by Git and should not be committed.

## Usage

Run all commands from the repository root.

### Review a Python file

```bash
python -m app.cli.main examples/vulnerable_example.py
```

The generated Markdown report is printed to the terminal.

### Save a Markdown report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format markdown `
  --output output/review.md
```

Linux or macOS:

```bash
python -m app.cli.main examples/vulnerable_example.py \
  --format markdown \
  --output output/review.md
```

### Save a JSON report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format json `
  --output output/review.json
```

### Replace an existing report

```bash
python -m app.cli.main examples/vulnerable_example.py --output output/review.md --overwrite
```

### Display CLI help

```bash
python -m app.cli.main --help
```

## Review Workflow

1. The CLI reads the requested Python file.
2. `PythonParser` validates the language, syntax, and line count.
3. `AnalysisService` executes Ruff and Bandit.
4. Analyzer outputs are normalized into shared `Finding` models.
5. `ReviewPromptBuilder` combines source code and findings.
6. `OllamaLLM` sends the prompt to the locally running model.
7. `ReviewResponseParser` validates the returned JSON.
8. `ReportService` produces Markdown or JSON output.
9. The CLI prints or saves the generated report.

## Privacy

The default implementation uses Ollama for local inference.

Reviewed source code is sent only to the locally configured Ollama endpoint:

```text
http://localhost:11434
```

The application does not require an external LLM API.

External-provider support should require explicit user permission before transmitting source code outside the local environment.

## Testing

### Run the complete test suite

```bash
pytest -v
```

### Run unit tests only

```bash
pytest -m "not integration and not performance" -v
```

### Run integration tests

```bash
pytest -m integration -v
```

### Run performance tests

```bash
pytest -m performance -v
```

### Run CLI tests

```bash
pytest tests/cli -v
```

### Run analyzer tests

```bash
pytest tests/analyzers -v
```

The automated test suite uses `MockLLM` wherever deterministic model output is required. Ruff and Bandit are exercised directly in integration tests.

## Code Quality Checks

Format the project:

```bash
black app tests
```

Verify formatting:

```bash
black --check app tests
```

Run Ruff:

```bash
ruff check app tests
```

Run all tests:

```bash
pytest -v
```

## Performance

The performance test validates Python parsing plus Ruff and Bandit analysis against a synthetic source file of approximately 500 lines.

Run:

```bash
pytest tests/performance -v -s
```

Measured result on the development machine:

```text
Parser + Ruff + Bandit: <replace with measured result> seconds
Environment: Windows, Python 3.13, <CPU/RAM details if available>
```

LLM inference latency is documented separately because it varies significantly based on model size, CPU, GPU, RAM, and Ollama configuration.

## Error Handling

The application handles expected failures such as:

* unsupported file extensions,
* invalid Python syntax,
* files exceeding the configured line limit,
* Ruff or Bandit execution failures,
* Ollama connection failures,
* Ollama request timeouts,
* missing Ollama models,
* malformed LLM JSON,
* invalid structured review responses,
* existing output files,
* UTF-8 decoding errors.

Independent analyzer failures use graceful degradation. Findings from successful analyzers are retained while failures are recorded in the report.

## Prompt Engineering Approach

The prompt instructs the model to:

* treat static-analysis findings as evidence rather than guaranteed defects,
* verify findings against the supplied source,
* avoid inventing unsupported issues,
* prioritize security and correctness,
* assign low priority to ordinary style findings,
* merge overlapping findings,
* suppress duplicate comments,
* avoid unrelated library recommendations,
* distinguish command-injection prevention from process error handling,
* return only JSON that follows the required schema.

The prompt also treats source code as untrusted data and instructs the model not to follow instructions embedded inside the reviewed source.

## Limitations

* Only Python is currently supported.
* Static analyzers may produce false positives or miss context-dependent defects.
* LLM recommendations can still be incomplete or technically inaccurate.
* Pydantic validates response structure, not the factual correctness of recommendations.
* Output quality depends on the selected Ollama model.
* LLM inference speed depends on local hardware.
* The system does not automatically modify source code.
* The application does not currently review complete repositories or Git diffs.
* The current implementation does not integrate directly with GitHub pull requests or IDEs.
* Prompt-injection resistance is limited and should not be considered a complete security boundary.
* Files larger than the configured line limit are rejected rather than chunked.

## Future Work

* Support JavaScript, Java, C++, and other languages
* Add repository and directory-level reviews
* Review Git diffs instead of complete files
* Add GitHub pull-request integration
* Add a VS Code extension
* Add SARIF and HTML report formats
* Add confidence scoring and finding traceability
* Introduce safe automatic-fix previews
* Add rule-specific remediation guidance
* Add model selection through the CLI
* Support streaming model responses
* Add structured logging and observability
* Add prompt-version tracking
* Add human feedback collection
* Evaluate precision, recall, and false-positive rates on labeled datasets

## Design Principles

The project applies several software-engineering principles:

* Separation of concerns
* Dependency inversion
* Dependency injection
* Adapter pattern
* Single Responsibility Principle
* Open/Closed Principle
* Graceful degradation
* Canonical internal data models
* Configuration externalization
* Deterministic unit testing
* Explicit validation at external boundaries

## License

Add the selected open-source license to the repository and update this section.

Example:

```text
This project is licensed under the MIT License.
```

## Author

**Jayasankar K S**

## Submission Links

* GitHub Repository: `https://github.com/jayasankarks3378/code-review-assistant`
* Colab Notebook: `https://colab.research.google.com/github/jayasankarks3378/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb`
* Unlisted YouTube Demo: `# Code Review Assistant

An AI-powered Python code review assistant that combines deterministic static analysis with a locally hosted Large Language Model to generate clear, structured, and actionable review feedback.

The application uses Ruff and Bandit to identify code-quality and security findings, then supplies those findings as structured context to a local Ollama model. The generated response is validated with Pydantic before being presented as a Markdown or JSON report.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/<jayasankarks3378>/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb
)

## Features

* Reviews Python source files of up to 500 lines
* Detects common bugs and code-quality issues using Ruff
* Detects potential security vulnerabilities using Bandit
* Generates contextual explanations using a local LLM
* Keeps reviewed source code on the local machine
* Validates LLM output against a strict JSON contract
* Produces Markdown and JSON reports
* Provides a command-line interface
* Supports configurable Ollama models and timeouts
* Handles partial analyzer failures gracefully
* Includes unit, integration, CLI, and performance tests

## Project Architecture

The project follows a modular-monolith architecture with dependency injection and clearly separated responsibilities.

```text
Python Source File
        │
        ▼
   PythonParser
        │
        ▼
  AnalysisService
   ┌────┴─────┐
   ▼          ▼
RuffAnalyzer BanditAnalyzer
   │          │
   └────┬─────┘
        ▼
 AnalysisResult
        │
        ▼
ReviewPromptBuilder
        │
        ▼
     BaseLLM
   ┌────┴─────┐
   ▼          ▼
 MockLLM    OllamaLLM
        │
        ▼
ReviewResponseParser
        │
        ▼
  ReviewResponse
        │
        ▼
   ReportService
   ┌────┴─────┐
   ▼          ▼
 Markdown    JSON
```

### Main Components

| Component              | Responsibility                                                    |
| ---------------------- | ----------------------------------------------------------------- |
| `PythonParser`         | Validates Python syntax and source-file size                      |
| `RuffAnalyzer`         | Detects style, readability, performance, and bug-related findings |
| `BanditAnalyzer`       | Detects potential Python security vulnerabilities                 |
| `AnalysisService`      | Executes analyzers and combines normalized findings               |
| `ReviewPromptBuilder`  | Creates structured LLM prompts from source and findings           |
| `BaseLLM`              | Defines the common interface for LLM providers                    |
| `MockLLM`              | Provides deterministic responses for automated testing            |
| `OllamaLLM`            | Communicates with a locally running Ollama server                 |
| `ReviewResponseParser` | Validates raw LLM responses using Pydantic                        |
| `ReviewService`        | Coordinates prompt creation, model generation, and validation     |
| `ReportService`        | Generates and optionally saves Markdown or JSON reports           |
| `ApplicationContainer` | Creates and wires application dependencies                        |
| CLI                    | Accepts user input and invokes the complete review workflow       |

## Technology Stack

* Python 3.11 or later
* Ruff
* Bandit
* Ollama
* Qwen2.5-Coder
* Pydantic
* Pydantic Settings
* Typer
* Rich
* pytest
* Black
* requests

## Repository Structure

```text
code-review-assistant/
├── app/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── examples/
├── tests/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── integration/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── performance/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── docs/
├── notebooks/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following before running the project:

* Python 3.11 or later
* Git
* Ollama

Confirm the installations:

```bash
python --version
git --version
ollama --version
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jayasankarks3378/code-review-assistant.git
cd code-review-assistant
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install an Ollama model

```bash
ollama pull qwen2.5-coder:3b
```

Confirm that the model is available:

```bash
ollama list
```

### 5. Configure the application

Copy the example environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Default configuration:

```dotenv
CODE_REVIEW_OLLAMA_BASE_URL=http://localhost:11434
CODE_REVIEW_OLLAMA_MODEL=qwen2.5-coder:3b
CODE_REVIEW_OLLAMA_TIMEOUT_SECONDS=120
CODE_REVIEW_MAX_SOURCE_LINES=500
CODE_REVIEW_MAX_PROMPT_FINDINGS=50
CODE_REVIEW_ALLOW_EXTERNAL_API=false
CODE_REVIEW_LOG_LEVEL=INFO
```

The `.env` file is ignored by Git and should not be committed.

## Usage

Run all commands from the repository root.

### Review a Python file

```bash
python -m app.cli.main examples/vulnerable_example.py
```

The generated Markdown report is printed to the terminal.

### Save a Markdown report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format markdown `
  --output output/review.md
```

Linux or macOS:

```bash
python -m app.cli.main examples/vulnerable_example.py \
  --format markdown \
  --output output/review.md
```

### Save a JSON report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format json `
  --output output/review.json
```

### Replace an existing report

```bash
python -m app.cli.main examples/vulnerable_example.py --output output/review.md --overwrite
```

### Display CLI help

```bash
python -m app.cli.main --help
```

## Review Workflow

1. The CLI reads the requested Python file.
2. `PythonParser` validates the language, syntax, and line count.
3. `AnalysisService` executes Ruff and Bandit.
4. Analyzer outputs are normalized into shared `Finding` models.
5. `ReviewPromptBuilder` combines source code and findings.
6. `OllamaLLM` sends the prompt to the locally running model.
7. `ReviewResponseParser` validates the returned JSON.
8. `ReportService` produces Markdown or JSON output.
9. The CLI prints or saves the generated report.

## Privacy

The default implementation uses Ollama for local inference.

Reviewed source code is sent only to the locally configured Ollama endpoint:

```text
http://localhost:11434
```

The application does not require an external LLM API.

External-provider support should require explicit user permission before transmitting source code outside the local environment.

## Testing

### Run the complete test suite

```bash
pytest -v
```

### Run unit tests only

```bash
pytest -m "not integration and not performance" -v
```

### Run integration tests

```bash
pytest -m integration -v
```

### Run performance tests

```bash
pytest -m performance -v
```

### Run CLI tests

```bash
pytest tests/cli -v
```

### Run analyzer tests

```bash
pytest tests/analyzers -v
```

The automated test suite uses `MockLLM` wherever deterministic model output is required. Ruff and Bandit are exercised directly in integration tests.

## Code Quality Checks

Format the project:

```bash
black app tests
```

Verify formatting:

```bash
black --check app tests
```

Run Ruff:

```bash
ruff check app tests
```

Run all tests:

```bash
pytest -v
```

## Performance

The performance test validates Python parsing plus Ruff and Bandit analysis against a synthetic source file of approximately 500 lines.

Run:

```bash
pytest tests/performance -v -s
```

Measured result on the development machine:

```text
Parser + Ruff + Bandit: <replace with measured result> seconds
Environment: Windows, Python 3.13, <CPU/RAM details if available>
```

LLM inference latency is documented separately because it varies significantly based on model size, CPU, GPU, RAM, and Ollama configuration.

## Error Handling

The application handles expected failures such as:

* unsupported file extensions,
* invalid Python syntax,
* files exceeding the configured line limit,
* Ruff or Bandit execution failures,
* Ollama connection failures,
* Ollama request timeouts,
* missing Ollama models,
* malformed LLM JSON,
* invalid structured review responses,
* existing output files,
* UTF-8 decoding errors.

Independent analyzer failures use graceful degradation. Findings from successful analyzers are retained while failures are recorded in the report.

## Prompt Engineering Approach

The prompt instructs the model to:

* treat static-analysis findings as evidence rather than guaranteed defects,
* verify findings against the supplied source,
* avoid inventing unsupported issues,
* prioritize security and correctness,
* assign low priority to ordinary style findings,
* merge overlapping findings,
* suppress duplicate comments,
* avoid unrelated library recommendations,
* distinguish command-injection prevention from process error handling,
* return only JSON that follows the required schema.

The prompt also treats source code as untrusted data and instructs the model not to follow instructions embedded inside the reviewed source.

## Limitations

* Only Python is currently supported.
* Static analyzers may produce false positives or miss context-dependent defects.
* LLM recommendations can still be incomplete or technically inaccurate.
* Pydantic validates response structure, not the factual correctness of recommendations.
* Output quality depends on the selected Ollama model.
* LLM inference speed depends on local hardware.
* The system does not automatically modify source code.
* The application does not currently review complete repositories or Git diffs.
* The current implementation does not integrate directly with GitHub pull requests or IDEs.
* Prompt-injection resistance is limited and should not be considered a complete security boundary.
* Files larger than the configured line limit are rejected rather than chunked.

## Future Work

* Support JavaScript, Java, C++, and other languages
* Add repository and directory-level reviews
* Review Git diffs instead of complete files
* Add GitHub pull-request integration
* Add a VS Code extension
* Add SARIF and HTML report formats
* Add confidence scoring and finding traceability
* Introduce safe automatic-fix previews
* Add rule-specific remediation guidance
* Add model selection through the CLI
* Support streaming model responses
* Add structured logging and observability
* Add prompt-version tracking
* Add human feedback collection
* Evaluate precision, recall, and false-positive rates on labeled datasets

## Design Principles

The project applies several software-engineering principles:

* Separation of concerns
* Dependency inversion
* Dependency injection
* Adapter pattern
* Single Responsibility Principle
* Open/Closed Principle
* Graceful degradation
* Canonical internal data models
* Configuration externalization
* Deterministic unit testing
* Explicit validation at external boundaries

## License

Add the selected open-source license to the repository and update this section.

Example:

```text
This project is licensed under the MIT License.
```

## Author

**Jayasankar K S**

## Submission Links

* GitHub Repository: `https://github.com/jayasankarks3378/code-review-assistant`
* Colab Notebook: `https://colab.research.google.com/github/jayasankarks3378/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb`
* Unlisted YouTube Demo: `# Code Review Assistant

An AI-powered Python code review assistant that combines deterministic static analysis with a locally hosted Large Language Model to generate clear, structured, and actionable review feedback.

The application uses Ruff and Bandit to identify code-quality and security findings, then supplies those findings as structured context to a local Ollama model. The generated response is validated with Pydantic before being presented as a Markdown or JSON report.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/<jayasankarks3378>/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb
)

## Features

* Reviews Python source files of up to 500 lines
* Detects common bugs and code-quality issues using Ruff
* Detects potential security vulnerabilities using Bandit
* Generates contextual explanations using a local LLM
* Keeps reviewed source code on the local machine
* Validates LLM output against a strict JSON contract
* Produces Markdown and JSON reports
* Provides a command-line interface
* Supports configurable Ollama models and timeouts
* Handles partial analyzer failures gracefully
* Includes unit, integration, CLI, and performance tests

## Project Architecture

The project follows a modular-monolith architecture with dependency injection and clearly separated responsibilities.

```text
Python Source File
        │
        ▼
   PythonParser
        │
        ▼
  AnalysisService
   ┌────┴─────┐
   ▼          ▼
RuffAnalyzer BanditAnalyzer
   │          │
   └────┬─────┘
        ▼
 AnalysisResult
        │
        ▼
ReviewPromptBuilder
        │
        ▼
     BaseLLM
   ┌────┴─────┐
   ▼          ▼
 MockLLM    OllamaLLM
        │
        ▼
ReviewResponseParser
        │
        ▼
  ReviewResponse
        │
        ▼
   ReportService
   ┌────┴─────┐
   ▼          ▼
 Markdown    JSON
```

### Main Components

| Component              | Responsibility                                                    |
| ---------------------- | ----------------------------------------------------------------- |
| `PythonParser`         | Validates Python syntax and source-file size                      |
| `RuffAnalyzer`         | Detects style, readability, performance, and bug-related findings |
| `BanditAnalyzer`       | Detects potential Python security vulnerabilities                 |
| `AnalysisService`      | Executes analyzers and combines normalized findings               |
| `ReviewPromptBuilder`  | Creates structured LLM prompts from source and findings           |
| `BaseLLM`              | Defines the common interface for LLM providers                    |
| `MockLLM`              | Provides deterministic responses for automated testing            |
| `OllamaLLM`            | Communicates with a locally running Ollama server                 |
| `ReviewResponseParser` | Validates raw LLM responses using Pydantic                        |
| `ReviewService`        | Coordinates prompt creation, model generation, and validation     |
| `ReportService`        | Generates and optionally saves Markdown or JSON reports           |
| `ApplicationContainer` | Creates and wires application dependencies                        |
| CLI                    | Accepts user input and invokes the complete review workflow       |

## Technology Stack

* Python 3.11 or later
* Ruff
* Bandit
* Ollama
* Qwen2.5-Coder
* Pydantic
* Pydantic Settings
* Typer
* Rich
* pytest
* Black
* requests

## Repository Structure

```text
code-review-assistant/
├── app/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── examples/
├── tests/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── integration/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── performance/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── docs/
├── notebooks/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following before running the project:

* Python 3.11 or later
* Git
* Ollama

Confirm the installations:

```bash
python --version
git --version
ollama --version
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jayasankarks3378/code-review-assistant.git
cd code-review-assistant
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install an Ollama model

```bash
ollama pull qwen2.5-coder:3b
```

Confirm that the model is available:

```bash
ollama list
```

### 5. Configure the application

Copy the example environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Default configuration:

```dotenv
CODE_REVIEW_OLLAMA_BASE_URL=http://localhost:11434
CODE_REVIEW_OLLAMA_MODEL=qwen2.5-coder:3b
CODE_REVIEW_OLLAMA_TIMEOUT_SECONDS=120
CODE_REVIEW_MAX_SOURCE_LINES=500
CODE_REVIEW_MAX_PROMPT_FINDINGS=50
CODE_REVIEW_ALLOW_EXTERNAL_API=false
CODE_REVIEW_LOG_LEVEL=INFO
```

The `.env` file is ignored by Git and should not be committed.

## Usage

Run all commands from the repository root.

### Review a Python file

```bash
python -m app.cli.main examples/vulnerable_example.py
```

The generated Markdown report is printed to the terminal.

### Save a Markdown report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format markdown `
  --output output/review.md
```

Linux or macOS:

```bash
python -m app.cli.main examples/vulnerable_example.py \
  --format markdown \
  --output output/review.md
```

### Save a JSON report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format json `
  --output output/review.json
```

### Replace an existing report

```bash
python -m app.cli.main examples/vulnerable_example.py --output output/review.md --overwrite
```

### Display CLI help

```bash
python -m app.cli.main --help
```

## Review Workflow

1. The CLI reads the requested Python file.
2. `PythonParser` validates the language, syntax, and line count.
3. `AnalysisService` executes Ruff and Bandit.
4. Analyzer outputs are normalized into shared `Finding` models.
5. `ReviewPromptBuilder` combines source code and findings.
6. `OllamaLLM` sends the prompt to the locally running model.
7. `ReviewResponseParser` validates the returned JSON.
8. `ReportService` produces Markdown or JSON output.
9. The CLI prints or saves the generated report.

## Privacy

The default implementation uses Ollama for local inference.

Reviewed source code is sent only to the locally configured Ollama endpoint:

```text
http://localhost:11434
```

The application does not require an external LLM API.

External-provider support should require explicit user permission before transmitting source code outside the local environment.

## Testing

### Run the complete test suite

```bash
pytest -v
```

### Run unit tests only

```bash
pytest -m "not integration and not performance" -v
```

### Run integration tests

```bash
pytest -m integration -v
```

### Run performance tests

```bash
pytest -m performance -v
```

### Run CLI tests

```bash
pytest tests/cli -v
```

### Run analyzer tests

```bash
pytest tests/analyzers -v
```

The automated test suite uses `MockLLM` wherever deterministic model output is required. Ruff and Bandit are exercised directly in integration tests.

## Code Quality Checks

Format the project:

```bash
black app tests
```

Verify formatting:

```bash
black --check app tests
```

Run Ruff:

```bash
ruff check app tests
```

Run all tests:

```bash
pytest -v
```

## Performance

The performance test validates Python parsing plus Ruff and Bandit analysis against a synthetic source file of approximately 500 lines.

Run:

```bash
pytest tests/performance -v -s
```

Measured result on the development machine:

```text
Parser + Ruff + Bandit: <replace with measured result> seconds
Environment: Windows, Python 3.13, <CPU/RAM details if available>
```

LLM inference latency is documented separately because it varies significantly based on model size, CPU, GPU, RAM, and Ollama configuration.

## Error Handling

The application handles expected failures such as:

* unsupported file extensions,
* invalid Python syntax,
* files exceeding the configured line limit,
* Ruff or Bandit execution failures,
* Ollama connection failures,
* Ollama request timeouts,
* missing Ollama models,
* malformed LLM JSON,
* invalid structured review responses,
* existing output files,
* UTF-8 decoding errors.

Independent analyzer failures use graceful degradation. Findings from successful analyzers are retained while failures are recorded in the report.

## Prompt Engineering Approach

The prompt instructs the model to:

* treat static-analysis findings as evidence rather than guaranteed defects,
* verify findings against the supplied source,
* avoid inventing unsupported issues,
* prioritize security and correctness,
* assign low priority to ordinary style findings,
* merge overlapping findings,
* suppress duplicate comments,
* avoid unrelated library recommendations,
* distinguish command-injection prevention from process error handling,
* return only JSON that follows the required schema.

The prompt also treats source code as untrusted data and instructs the model not to follow instructions embedded inside the reviewed source.

## Limitations

* Only Python is currently supported.
* Static analyzers may produce false positives or miss context-dependent defects.
* LLM recommendations can still be incomplete or technically inaccurate.
* Pydantic validates response structure, not the factual correctness of recommendations.
* Output quality depends on the selected Ollama model.
* LLM inference speed depends on local hardware.
* The system does not automatically modify source code.
* The application does not currently review complete repositories or Git diffs.
* The current implementation does not integrate directly with GitHub pull requests or IDEs.
* Prompt-injection resistance is limited and should not be considered a complete security boundary.
* Files larger than the configured line limit are rejected rather than chunked.

## Future Work

* Support JavaScript, Java, C++, and other languages
* Add repository and directory-level reviews
* Review Git diffs instead of complete files
* Add GitHub pull-request integration
* Add a VS Code extension
* Add SARIF and HTML report formats
* Add confidence scoring and finding traceability
* Introduce safe automatic-fix previews
* Add rule-specific remediation guidance
* Add model selection through the CLI
* Support streaming model responses
* Add structured logging and observability
* Add prompt-version tracking
* Add human feedback collection
* Evaluate precision, recall, and false-positive rates on labeled datasets

## Design Principles

The project applies several software-engineering principles:

* Separation of concerns
* Dependency inversion
* Dependency injection
* Adapter pattern
* Single Responsibility Principle
* Open/Closed Principle
* Graceful degradation
* Canonical internal data models
* Configuration externalization
* Deterministic unit testing
* Explicit validation at external boundaries

## License

Add the selected open-source license to the repository and update this section.

Example:

```text
This project is licensed under the MIT License.
```

## Author

**Jayasankar K S**

## Submission Links

* GitHub Repository: `https://github.com/jayasankarks3378/code-review-assistant`
* Colab Notebook: `https://colab.research.google.com/github/jayasankarks3378/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb`
* Unlisted YouTube Demo: `# Code Review Assistant

An AI-powered Python code review assistant that combines deterministic static analysis with a locally hosted Large Language Model to generate clear, structured, and actionable review feedback.

The application uses Ruff and Bandit to identify code-quality and security findings, then supplies those findings as structured context to a local Ollama model. The generated response is validated with Pydantic before being presented as a Markdown or JSON report.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/<jayasankarks3378>/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb
)

## Features

* Reviews Python source files of up to 500 lines
* Detects common bugs and code-quality issues using Ruff
* Detects potential security vulnerabilities using Bandit
* Generates contextual explanations using a local LLM
* Keeps reviewed source code on the local machine
* Validates LLM output against a strict JSON contract
* Produces Markdown and JSON reports
* Provides a command-line interface
* Supports configurable Ollama models and timeouts
* Handles partial analyzer failures gracefully
* Includes unit, integration, CLI, and performance tests

## Project Architecture

The project follows a modular-monolith architecture with dependency injection and clearly separated responsibilities.

```text
Python Source File
        │
        ▼
   PythonParser
        │
        ▼
  AnalysisService
   ┌────┴─────┐
   ▼          ▼
RuffAnalyzer BanditAnalyzer
   │          │
   └────┬─────┘
        ▼
 AnalysisResult
        │
        ▼
ReviewPromptBuilder
        │
        ▼
     BaseLLM
   ┌────┴─────┐
   ▼          ▼
 MockLLM    OllamaLLM
        │
        ▼
ReviewResponseParser
        │
        ▼
  ReviewResponse
        │
        ▼
   ReportService
   ┌────┴─────┐
   ▼          ▼
 Markdown    JSON
```

### Main Components

| Component              | Responsibility                                                    |
| ---------------------- | ----------------------------------------------------------------- |
| `PythonParser`         | Validates Python syntax and source-file size                      |
| `RuffAnalyzer`         | Detects style, readability, performance, and bug-related findings |
| `BanditAnalyzer`       | Detects potential Python security vulnerabilities                 |
| `AnalysisService`      | Executes analyzers and combines normalized findings               |
| `ReviewPromptBuilder`  | Creates structured LLM prompts from source and findings           |
| `BaseLLM`              | Defines the common interface for LLM providers                    |
| `MockLLM`              | Provides deterministic responses for automated testing            |
| `OllamaLLM`            | Communicates with a locally running Ollama server                 |
| `ReviewResponseParser` | Validates raw LLM responses using Pydantic                        |
| `ReviewService`        | Coordinates prompt creation, model generation, and validation     |
| `ReportService`        | Generates and optionally saves Markdown or JSON reports           |
| `ApplicationContainer` | Creates and wires application dependencies                        |
| CLI                    | Accepts user input and invokes the complete review workflow       |

## Technology Stack

* Python 3.11 or later
* Ruff
* Bandit
* Ollama
* Qwen2.5-Coder
* Pydantic
* Pydantic Settings
* Typer
* Rich
* pytest
* Black
* requests

## Repository Structure

```text
code-review-assistant/
├── app/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── examples/
├── tests/
│   ├── analyzers/
│   ├── bootstrap/
│   ├── cli/
│   ├── config/
│   ├── integration/
│   ├── llm/
│   ├── models/
│   ├── parser/
│   ├── performance/
│   ├── prompts/
│   ├── reports/
│   ├── response/
│   └── services/
├── docs/
├── notebooks/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following before running the project:

* Python 3.11 or later
* Git
* Ollama

Confirm the installations:

```bash
python --version
git --version
ollama --version
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jayasankarks3378/code-review-assistant.git
cd code-review-assistant
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install an Ollama model

```bash
ollama pull qwen2.5-coder:3b
```

Confirm that the model is available:

```bash
ollama list
```

### 5. Configure the application

Copy the example environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

Default configuration:

```dotenv
CODE_REVIEW_OLLAMA_BASE_URL=http://localhost:11434
CODE_REVIEW_OLLAMA_MODEL=qwen2.5-coder:3b
CODE_REVIEW_OLLAMA_TIMEOUT_SECONDS=120
CODE_REVIEW_MAX_SOURCE_LINES=500
CODE_REVIEW_MAX_PROMPT_FINDINGS=50
CODE_REVIEW_ALLOW_EXTERNAL_API=false
CODE_REVIEW_LOG_LEVEL=INFO
```

The `.env` file is ignored by Git and should not be committed.

## Usage

Run all commands from the repository root.

### Review a Python file

```bash
python -m app.cli.main examples/vulnerable_example.py
```

The generated Markdown report is printed to the terminal.

### Save a Markdown report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format markdown `
  --output output/review.md
```

Linux or macOS:

```bash
python -m app.cli.main examples/vulnerable_example.py \
  --format markdown \
  --output output/review.md
```

### Save a JSON report

Windows PowerShell:

```powershell
python -m app.cli.main examples/vulnerable_example.py `
  --format json `
  --output output/review.json
```

### Replace an existing report

```bash
python -m app.cli.main examples/vulnerable_example.py --output output/review.md --overwrite
```

### Display CLI help

```bash
python -m app.cli.main --help
```

## Review Workflow

1. The CLI reads the requested Python file.
2. `PythonParser` validates the language, syntax, and line count.
3. `AnalysisService` executes Ruff and Bandit.
4. Analyzer outputs are normalized into shared `Finding` models.
5. `ReviewPromptBuilder` combines source code and findings.
6. `OllamaLLM` sends the prompt to the locally running model.
7. `ReviewResponseParser` validates the returned JSON.
8. `ReportService` produces Markdown or JSON output.
9. The CLI prints or saves the generated report.

## Privacy

The default implementation uses Ollama for local inference.

Reviewed source code is sent only to the locally configured Ollama endpoint:

```text
http://localhost:11434
```

The application does not require an external LLM API.

External-provider support should require explicit user permission before transmitting source code outside the local environment.

## Testing

### Run the complete test suite

```bash
pytest -v
```

### Run unit tests only

```bash
pytest -m "not integration and not performance" -v
```

### Run integration tests

```bash
pytest -m integration -v
```

### Run performance tests

```bash
pytest -m performance -v
```

### Run CLI tests

```bash
pytest tests/cli -v
```

### Run analyzer tests

```bash
pytest tests/analyzers -v
```

The automated test suite uses `MockLLM` wherever deterministic model output is required. Ruff and Bandit are exercised directly in integration tests.

## Code Quality Checks

Format the project:

```bash
black app tests
```

Verify formatting:

```bash
black --check app tests
```

Run Ruff:

```bash
ruff check app tests
```

Run all tests:

```bash
pytest -v
```

## Performance

The performance test validates Python parsing plus Ruff and Bandit analysis against a synthetic source file of approximately 500 lines.

Run:

```bash
pytest tests/performance -v -s
```

Measured result on the development machine:

```text
Parser + Ruff + Bandit: <replace with measured result> seconds
Environment: Windows, Python 3.13, <CPU/RAM details if available>
```

LLM inference latency is documented separately because it varies significantly based on model size, CPU, GPU, RAM, and Ollama configuration.

## Error Handling

The application handles expected failures such as:

* unsupported file extensions,
* invalid Python syntax,
* files exceeding the configured line limit,
* Ruff or Bandit execution failures,
* Ollama connection failures,
* Ollama request timeouts,
* missing Ollama models,
* malformed LLM JSON,
* invalid structured review responses,
* existing output files,
* UTF-8 decoding errors.

Independent analyzer failures use graceful degradation. Findings from successful analyzers are retained while failures are recorded in the report.

## Prompt Engineering Approach

The prompt instructs the model to:

* treat static-analysis findings as evidence rather than guaranteed defects,
* verify findings against the supplied source,
* avoid inventing unsupported issues,
* prioritize security and correctness,
* assign low priority to ordinary style findings,
* merge overlapping findings,
* suppress duplicate comments,
* avoid unrelated library recommendations,
* distinguish command-injection prevention from process error handling,
* return only JSON that follows the required schema.

The prompt also treats source code as untrusted data and instructs the model not to follow instructions embedded inside the reviewed source.

## Limitations

* Only Python is currently supported.
* Static analyzers may produce false positives or miss context-dependent defects.
* LLM recommendations can still be incomplete or technically inaccurate.
* Pydantic validates response structure, not the factual correctness of recommendations.
* Output quality depends on the selected Ollama model.
* LLM inference speed depends on local hardware.
* The system does not automatically modify source code.
* The application does not currently review complete repositories or Git diffs.
* The current implementation does not integrate directly with GitHub pull requests or IDEs.
* Prompt-injection resistance is limited and should not be considered a complete security boundary.
* Files larger than the configured line limit are rejected rather than chunked.

## Future Work

* Support JavaScript, Java, C++, and other languages
* Add repository and directory-level reviews
* Review Git diffs instead of complete files
* Add GitHub pull-request integration
* Add a VS Code extension
* Add SARIF and HTML report formats
* Add confidence scoring and finding traceability
* Introduce safe automatic-fix previews
* Add rule-specific remediation guidance
* Add model selection through the CLI
* Support streaming model responses
* Add structured logging and observability
* Add prompt-version tracking
* Add human feedback collection
* Evaluate precision, recall, and false-positive rates on labeled datasets

## Design Principles

The project applies several software-engineering principles:

* Separation of concerns
* Dependency inversion
* Dependency injection
* Adapter pattern
* Single Responsibility Principle
* Open/Closed Principle
* Graceful degradation
* Canonical internal data models
* Configuration externalization
* Deterministic unit testing
* Explicit validation at external boundaries

## License

Add the selected open-source license to the repository and update this section.

Example:

```text
This project is licensed under the MIT License.
```

## Author

**Jayasankar K S**

## Submission Links

* GitHub Repository: `https://github.com/jayasankarks3378/code-review-assistant`
* Colab Notebook: `https://colab.research.google.com/github/jayasankarks3378/code-review-assistant/blob/main/notebooks/Code_Review_Assistant_Demo.ipynb`
* Unlisted YouTube Demo: `https://youtu.be/SqL6mlnfbCo?si=0gbMe-VVttSsKaXQ`
`
