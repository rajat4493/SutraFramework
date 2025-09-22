# sutra.py — SutraAI: Local-first agent workflows with flexible pipeline selection
import argparse, importlib.util, json, pathlib, sys, time, types, urllib.request

# ---------- Trace ----------
RUNS_DIR = pathlib.Path(".sutra") / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

class Trace:
    def __init__(self):
        ts = time.strftime("%Y%m%d-%H%M%S")
        self.d = RUNS_DIR / ts
        self.d.mkdir(parents=True, exist_ok=True)
        self.i = 0
    def dump(self, name, payload):
        self.i += 1
        (self.d / f"{self.i:02d}_{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

# ---------- Ollama ----------
class Ollama:
    def __init__(self, model="llama3.1:8b", host="http://localhost:11434"):
        self.model, self.host = model, host.rstrip("/")
    def generate(self, prompt, temperature=0.2, json_mode=False):
        url = f"{self.host}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "temperature": temperature, "stream": False}
        if json_mode: payload["format"] = "json"
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type":"application/json"}
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8")).get("response","")

# ---------- JSON Helpers ----------
def _extract_json(text: str):
    import re
    m = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if not m: return None
    try: return json.loads(m.group(1))
    except: return None

def _validate(obj, required):
    if not required: return True, ""
    if isinstance(obj, list):
        for i, it in enumerate(obj):
            if not isinstance(it, dict):
                return False, f"item {i} not dict"
            miss = [k for k in required if k not in it]
            if miss: return False, f"item {i} missing {miss}"
        return True, ""
    if isinstance(obj, dict):
        miss = [k for k in required if k not in obj]
        return (not miss, f"missing {miss}" if miss else "")
    return False, "not dict/list"

_WRAPPER_KEYS = ("items", "data", "result", "results", "topics", "list")

def _coerce_json_shape(obj, required):
    if obj is None: return None
    if isinstance(obj, dict):
        for k in _WRAPPER_KEYS:
            if k in obj and isinstance(obj[k], list):
                obj = obj[k]
                break
        else:
            if required and all(k in obj for k in required):
                obj = [obj]
    if isinstance(obj, list):
        out = []
        for it in obj:
            if not isinstance(it, dict): return obj
            it = it.copy()
            if "note" not in it and "notes" in it:
                it["note"] = it.pop("notes")
            if required:
                it = {k: it.get(k, "") for k in required}
            out.append(it)
        return out
    return obj

# ---------- CORE CLASSES ----------
class Agent:
    def __init__(self, name, objective, model, prompt,
                 expects_json=False, output_key="output", system_hint=None,
                 required_keys=None, retries=1, temperature=0.0):
        self.name=name; self.objective=objective; self.model=model; self.prompt=prompt
        self.expects_json=expects_json; self.output_key=output_key; self.system_hint=system_hint
        self.required_keys=required_keys or []; self.retries=retries; self.temperature=temperature

    def run(self, inputs: dict)->dict:
        try:
            p = self.prompt.format(**inputs, objective=self.objective)
        except KeyError as e:
            raise ValueError(f"[{self.name}] Missing var: {e}")
        if self.system_hint:
            p = f"{self.system_hint}\n\n---\n{p}"

        llm = Ollama(model=self.model)
        attempts = self.retries + 1
        last_raw = ""

        for a in range(attempts):
            raw = llm.generate(
                p if a==0 else p + "\n\nReturn ONLY valid JSON.",
                json_mode=self.expects_json,
                temperature=self.temperature
            )
            last_raw = raw

            if not self.expects_json:
                return {self.output_key: raw.strip()}

            obj = None
            try:
                obj = json.loads(raw)
            except:
                obj = _extract_json(raw)

            obj = _coerce_json_shape(obj, self.required_keys)
            ok, why = _validate(obj, self.required_keys)
            if ok:
                return {self.output_key: obj}

        return {self.output_key: {"error":"invalid_json", "raw": last_raw[:2000]}}

class Step:
    def __init__(self, agent: 'Agent', takes=None, on_error="continue"):
        self.agent=agent; self.takes=takes or []; self.on_error=on_error
    def __call__(self, state: dict)->dict:
        subset = {k: state.get(k) for k in self.takes} if self.takes else state
        try:
            out = self.agent.run(subset)
        except Exception as e:
            if self.on_error=="stop": raise
            out = { self.agent.output_key: {"error":"exception", "message": str(e)} }
        new = state.copy(); new.update(out); return new

class Pipeline:
    def __init__(self, steps):
        if not steps: raise ValueError("Pipeline needs steps")
        self.steps = steps
    def run(self, initial: dict)->dict:
        s = dict(initial or {}); tr = Trace()
        for st in self.steps:
            tr.dump(f"{st.agent.name}_in", s)
            s = st(s)
            tr.dump(f"{st.agent.name}_out", s)
        return s

# ---------- IMPROVED GENERATOR ----------
def create_analyzer_agent(project_name: str) -> str:
    """Generate analyzer.py file"""
    return f"""# {project_name}_analyzer.py
from sutra import Agent

analyzer = Agent(
    name='analyzer',
    objective='Analyze and understand the input content',
    model='llama3.1:8b',
    prompt='''Analyze the following content thoroughly.

Content: {{text}}

Break down and analyze this content. Return JSON with:
- "content_type": what type of content this is
- "key_themes": main themes or topics found
- "complexity": how complex the content is (simple/medium/complex)
- "analysis": detailed analysis of the content
- "notable_elements": any important elements worth highlighting

Return only valid JSON.''',
    expects_json=True,
    output_key='analyzer',
    required_keys=['content_type', 'key_themes', 'analysis'],
    retries=1,
    temperature=0.1
)"""

def create_classifier_agent(project_name: str) -> str:
    """Generate classifier.py file"""
    return f"""# {project_name}_classifier.py
from sutra import Agent

classifier = Agent(
    name='classifier',
    objective='Classify and categorize content appropriately',
    model='gemma2:2b',
    prompt='''Classify the following content into appropriate categories.

Content to classify: {{text}}
Analysis (if available): {{analyzer}}

Classify this content. Return JSON with:
- "primary_category": main category (e.g., business, technical, personal)
- "subcategory": more specific classification
- "priority_level": importance level (low/medium/high)
- "tags": list of relevant tags
- "confidence": confidence in classification (1-10)
- "reasoning": brief explanation of classification choice

Return only valid JSON.''',
    expects_json=True,
    output_key='classifier',
    required_keys=['primary_category', 'confidence', 'reasoning'],
    retries=1,
    temperature=0.1
)"""

def create_summarizer_agent(project_name: str) -> str:
    """Generate summarizer.py file"""
    return f"""# {project_name}_summarizer.py
from sutra import Agent

summarizer = Agent(
    name='summarizer',
    objective='Create clear summary and actionable output',
    model='mistral:7b',
    prompt='''Create a comprehensive summary and final output.

Original content: {{text}}
Analysis: {{analyzer}}
Classification: {{classifier}}

Create final summary. Return JSON with:
- "summary": clear 2-3 sentence summary
- "key_points": list of most important points
- "action_items": suggested next steps or actions
- "final_assessment": overall assessment of the content
- "recommendations": any recommendations based on the content

Return only valid JSON.''',
    expects_json=True,
    output_key='summarizer',
    required_keys=['summary', 'key_points', 'final_assessment'],
    retries=1,
    temperature=0.1
)"""

def generate_pipeline_file(project_name: str, description: str) -> str:
    """Generate simple pipeline file with agent name list"""
    lines = [
        f"# {project_name}_pipeline.py",
        f"# Pipeline: {description}",
        f"# Edit AGENT_ORDER list to choose which agents to use and in what order",
        "",
        "from sutra import Step, Pipeline",
        "import importlib",
        "",
        "# Configure your pipeline by listing agent file names in execution order",
        "# Examples:",
        f'# AGENT_ORDER = ["{project_name}_classifier"]  # Classification only',
        f'# AGENT_ORDER = ["{project_name}_summarizer"]  # Summary only',
        f'# AGENT_ORDER = ["{project_name}_analyzer", "{project_name}_classifier"]  # Analysis + Classification',
        f'AGENT_ORDER = ["{project_name}_analyzer", "{project_name}_classifier", "{project_name}_summarizer"]  # Full workflow',
        "",
        "def build():",
        "    steps = []",
        "    previous_outputs = ['text']  # Start with input text",
        "    ",
        "    for agent_file in AGENT_ORDER:",
        "        # Import the agent from its file",
        "        module = importlib.import_module(agent_file)",
        "        agent_name = agent_file.split('_')[-1]  # Get agent name from filename",
        "        agent = getattr(module, agent_name)",
        "        ",
        "        # Create step with outputs from all previous agents",
        "        steps.append(Step(agent, takes=previous_outputs.copy()))",
        "        ",
        "        # Add this agent's output for next agent",
        "        previous_outputs.append(agent_name)",
        "    ",
        "    return Pipeline(steps)",
        "",
        "DEFAULT_INPUT = {'text': 'Sample text to process - replace with your actual content'}"
    ]
    
    return "\n".join(lines)

# ---------- CLI ----------
def _import_module(path_str)->types.ModuleType:
    p = pathlib.Path(path_str)
    if not p.exists(): raise FileNotFoundError(p)
    spec = importlib.util.spec_from_file_location("user_pipeline", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def cmd_create(project_name, description):
    """Create a new project with 3 separate agent files and configurable pipeline"""
    # Sanitize project name
    project_name = project_name.replace('.py', '').replace('.', '_').replace('-', '_')
    
    print(f"Creating project: {project_name}")
    print(f"Description: {description}")
    print("Generating 3 separate agent files + 1 pipeline file")
    
    # Generate files
    analyzer_file = f"{project_name}_analyzer.py"
    classifier_file = f"{project_name}_classifier.py" 
    summarizer_file = f"{project_name}_summarizer.py"
    pipeline_file = f"{project_name}_pipeline.py"
    
    files_to_create = [analyzer_file, classifier_file, summarizer_file, pipeline_file]
    
    # Check if files exist
    existing = [f for f in files_to_create if pathlib.Path(f).exists()]
    if existing:
        print(f"Files exist: {existing}")
        overwrite = input("Overwrite existing files? [y/N]: ")
        if overwrite.lower() != 'y':
            print("Cancelled.")
            return
    
    # Write agent files
    pathlib.Path(analyzer_file).write_text(create_analyzer_agent(project_name), encoding="utf-8")
    pathlib.Path(classifier_file).write_text(create_classifier_agent(project_name), encoding="utf-8")
    pathlib.Path(summarizer_file).write_text(create_summarizer_agent(project_name), encoding="utf-8")
    print(f"Created: {analyzer_file}")
    print(f"Created: {classifier_file}")
    print(f"Created: {summarizer_file}")
    
    # Write pipeline file  
    pipeline_code = generate_pipeline_file(project_name, description)
    pathlib.Path(pipeline_file).write_text(pipeline_code, encoding="utf-8")
    print(f"Created: {pipeline_file}")
    
    print(f"\nProject '{project_name}' ready!")
    print(f"\nTo use different agent combinations, edit {pipeline_file}:")
    print(f"Change the AGENT_ORDER list to include only the agents you want.")
    print(f"\nExamples:")
    print(f'Classification only:  AGENT_ORDER = ["{project_name}_classifier"]')
    print(f'Summary only:         AGENT_ORDER = ["{project_name}_summarizer"]')
    print(f'Analysis + Summary:   AGENT_ORDER = ["{project_name}_analyzer", "{project_name}_summarizer"]')
    print(f"\nTest: python sutra.py test {pipeline_file}")

def cmd_run(filename, input_json=None):
    mod = _import_module(filename)
    pipe = mod.build()
    init = json.loads(input_json) if input_json else {}
    out = pipe.run(init)
    print(json.dumps(out, indent=2, ensure_ascii=False))

def cmd_test(filename):
    mod = _import_module(filename)
    pipe = mod.build()
    init = getattr(mod, "DEFAULT_INPUT", {})
    print(f"Testing with: {init}")
    out = pipe.run(init)
    print(json.dumps(out, indent=2, ensure_ascii=False))

def cmd_doctor():
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
        print("✓ Ollama reachable")
        r = Ollama().generate("Say OK.", json_mode=False)
        print("✓ Generation works:", (r[:60] + "…") if len(r)>60 else r)
    except Exception as e:
        print("✗ Ollama issue:", e)

def main():
    ap = argparse.ArgumentParser(prog="sutra", description="SutraAI: Local-first agent workflows")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Create new project with 3 flexible agents")
    c.add_argument("project_name", help="Project name (e.g., ticket_processor)")
    c.add_argument("description", help="What the workflow should do")

    r = sub.add_parser("run", help="Run a pipeline file")
    r.add_argument("pipeline_file", help="e.g., ticket_processor_pipeline.py")
    r.add_argument("--input", help="JSON input", default=None)

    t = sub.add_parser("test", help="Test pipeline with DEFAULT_INPUT")
    t.add_argument("pipeline_file")

    d = sub.add_parser("doctor", help="Check Ollama connectivity")

    args = ap.parse_args()
    if args.cmd == "create":
        cmd_create(args.project_name, args.description)
    elif args.cmd == "run":
        cmd_run(args.pipeline_file, args.input)
    elif args.cmd == "test":
        cmd_test(args.pipeline_file)
    elif args.cmd == "doctor":
        cmd_doctor()

if __name__ == "__main__":
    main()