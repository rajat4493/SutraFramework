SutraAI 
Local-first agent workflow framework for hackable, reliable multi-agent pipelines.

Build, run, and debug AI agent pipelines entirely on your machine. No API keys, no cloud, no bloat.

SutraAI is a lightweight, open-source framework for orchestrating AI agent pipelines. Designed for developers who want control, hackability, and offline execution, SutraAI lets you sequence small-to-mid-sized language models (2B–7B) with a simple, Python-based workflow. Think of it as the anti-bloat alternative to heavy frameworks like LangChain or CrewAI—built for intermediates who value clarity and flexibility.

#######Features

Multi-Agent Pipelines – Define clear, sequential agent workflows using simple Python files, no complex graph abstractions.
Local-First Execution – Runs entirely offline using Ollama or similar local model servers. No cloud dependency, no API keys.
Hackable Core – Agents are just Python scripts with editable prompts, making customization a breeze.
CLI & Templates – Generate working pipelines in seconds with commands like sutra create study-helper.
Reliable Orchestration – Built-in retries, JSON schema validation, and error recovery for robust execution.


Quickstart
Get up and running in minutes:
# Clone the repository
git clone https://github.com/yourusername/sutra
cd sutra

# Install dependencies
pip install -r requirements.txt

# Run a sample pipeline (no Ollama required)
python3 sutra.py test examples/echo_pipeline.py

Or run with explicit input:
python3 sutra.py run examples/echo_pipeline.py --input '{"text":"Ticket #12847: App crashes on photo upload after update 2.3.1"}'

Example Output (from `examples/echo_pipeline.py`):
{
  "text": "Ticket #12847: App crashes on photo upload after update 2.3.1",
  "analyzer": [
    {
      "summary": "Ticket #12847: App crashes on photo upload after update 2.3.1",
      "category": "Bug Report",
      "root_cause": "Crash on photo upload"
    }
  ],
  "classifier": [
    {
      "priority": "High",
      "team": "mobile",
      "ticket_type": "bug"
    }
  ],
  "replier": {
    "reply": "Thanks for the report. We've identified the issue and our mobile team is on it.",
    "tone": "calm"
  }
}


Status

Status: Alpha | Experimental

Why SutraAI?
SutraAI is built for developers who want to avoid the complexity and overhead of bloated frameworks. Here’s how it stacks up:



Feature
SutraAI
LangChain
CrewAI



Local Execution
✅ Fully offline (Ollama)
❌ Cloud-heavy
❌ Cloud-heavy


Ease of Hacking
✅ Plain Python scripts
🟡 Complex abstractions
🟡 Rigid structure


Lightweight
✅ <100 KB core
❌ Heavy dependencies
❌ Heavy dependencies


Pipeline Clarity
✅ Sequential, explicit
🟡 Graph-based complexity
🟡 Black-box orchestration


Setup Time
✅ Seconds (CLI templates)
🟡 Minutes to hours
🟡 Minutes to hours


SutraAI is the framework for those who want to build fast, debug easily, and stay in control.

Roadmap

 CLI generator (sutra create <name> "<task>") for instant pipeline creation
 DAG executor for parallel branches and joins
 Observability with OpenTelemetry spans and JSONL logs
 Template library (e.g., resume-helper, ticket-triage, invoice-extract)
 Web UI for run history, input/output visualization, and replays


Project Structure
sutra/
├── sutra.py            # CLI entry point
├── examples/           # Ready-to-run pipelines
│   ├── catagent_pipeline.py
│   ├── study_helper.py
│   ├── ticket_triage.py
├── docs/               # Documentation
│   ├── concept.md
│   ├── comparisons.md
│   ├── examples.md
├── requirements.txt
└── README.md


Documentation

Concept – Core ideas behind SutraAI’s design
Comparisons – How SutraAI differs from other frameworks
Examples – Code snippets for common pipelines


Demo

Check out a short demo video on X or YouTube. - Upcoming

Contributing
We welcome contributions! Check out our Issues for bugs, features, or new pipeline ideas. Use our Discussions to share templates or ask questions.
To get started:

Fork the repo
Create a branch (git checkout -b feature/awesome-agent)
Commit changes (git commit -m "Add awesome agent")
Push and open a PR


License
MIT License – see LICENSE for details.

Try SutraAI Today!
SutraAI is the fastest way to build and debug local AI agent pipelines. Clone the repo, try the examples, and let us know what you think in Discussions!
