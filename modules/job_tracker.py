# modules/job_tracker.py

"""
Simple job tracker module for Shaco Core.

Features:
- Job dataclass (id, role, company, status, updated_at)
- Atomic JSON persistence (safe save)
- CRUD functions (add, list, update, remove)
- Interactive CLI with flexible exit/skip words
- Small free-text -> command translator (keyword-based)
"""

from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
import os
import uuid
import difflib
import re
from typing import List, Optional, Dict, Union

# ---------- Config ----------
DEFAULT_STATUSES = [
    "applied",
    "interviewing",
    "offer",
    "accepted",
    "rejected",
    "withdrawn",
    "todo"
]

# Words that cancel the whole interactive operation
EXIT_WORDS = {"exit", "quit", "q", "cancel", "never mind", "nah", "nope", "forget it", "stop", "nvm"}
# Words that mean "leave this field blank or move on"
SKIP_WORDS = {"skip", "pass", "s", "no", "n"}

POSTCODE_RE = re.compile(r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b", re.I)

DATA_FILE = Path(__file__).parent.parent / "data" / "job_data.json"


# ---------- Data model ----------
@dataclass
class Job:
    id: str
    role: str
    company: str
    status: str = "applied"
    location: str = ""      # NEW
    job_type: str = ""                # full-time / part-time / contract etc.
    updated_at: str = ""
    skills: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.updated_at:
            self.touch()

    def touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "Job":
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            role=d.get("role", ""),
            company=d.get("company", ""),
            status=d.get("status", "applied"),
            updated_at=d.get("updated_at", datetime.now(timezone.utc).isoformat()),
            skills=d.get("skills", []),
        )


# ---------- Persistence ----------
def _ensure_data_path(path: Path = DATA_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)


def load_jobs(path: Path = DATA_FILE) -> List[Job]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Job.from_dict(item) for item in raw]


def save_jobs(jobs: List[Job], path: Path = DATA_FILE):
    _ensure_data_path(path)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump([j.to_dict() for j in jobs], f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    # atomic replace
    os.replace(tmp, path)


# ---------- Utilities ----------
def _find_job(jobs: List[Job], identifier: Union[int, str]) -> Optional[int]:
    """
    Accepts integer (index) or job id (string).
    Returns index in list or None.
    """
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        idx = int(identifier)
        if 0 <= idx < len(jobs):
            return idx
        return None
    # treat identifier as id string
    for i, job in enumerate(jobs):
        if job.id == identifier:
            return i
    return None


def normalize_status(s: str) -> str:
    s = (s or "").strip().lower()
    mapping = {
        "int": "interviewing",
        "interview": "interviewing",
        "appl": "applied",
        "rej": "rejected",
        "acc": "accepted",
        "off": "offer",
        "todo": "todo",
    }
    if s in DEFAULT_STATUSES:
        return s
    if s in mapping:
        return mapping[s]
    # fuzzy match
    close = difflib.get_close_matches(s, DEFAULT_STATUSES, n=1, cutoff=0.6)
    if close:
        return close[0]
    # fallback
    return "applied"


# ---------- CRUD API ----------
def add_job(role: str, company: str, status: str = "applied", path: Path = DATA_FILE) -> Job:
    jobs = load_jobs(path)
    job = Job(id=str(uuid.uuid4()), role=role.strip(), company=company.strip(), status=normalize_status(status))
    job.touch()
    jobs.append(job)
    save_jobs(jobs, path)
    return job


def list_jobs(path: Path = DATA_FILE, *, status: Optional[str] = None) -> List[Job]:
    jobs = load_jobs(path)
    if status:
        status = normalize_status(status)
        jobs = [j for j in jobs if j.status == status]
    return jobs


def remove_job(identifier: Union[int, str], path: Path = DATA_FILE) -> Optional[Job]:
    jobs = load_jobs(path)
    idx = _find_job(jobs, identifier)
    if idx is None:
        return None
    removed = jobs.pop(idx)
    save_jobs(jobs, path)
    return removed


def update_job(identifier: Union[int, str], *, role: Optional[str] = None,
               company: Optional[str] = None, status: Optional[str] = None,
               path: Path = DATA_FILE) -> Optional[Job]:
    jobs = load_jobs(path)
    idx = _find_job(jobs, identifier)
    if idx is None:
        return None
    job = jobs[idx]
    if role is not None:
        job.role = role.strip()
    if company is not None:
        job.company = company.strip()
    if status is not None:
        job.status = normalize_status(status)
    job.touch()
    save_jobs(jobs, path)
    return job


# ---------- Interactive helpers ----------
class AbortInteractive(Exception):
    pass


def _prompt_field(prompt_text: str, required: bool = False, default: Optional[str] = None) -> Optional[str]:
    """
    Prompts user for a field. Respects EXIT_WORDS and SKIP_WORDS.
    - If user types an exit word -> raises AbortInteractive
    - If user types a skip word -> returns default (which may be None)
    - If required and blank -> re-prompt
    """
    while True:
        raw = input(f"{prompt_text}{' (required)' if required else ''}: ").strip()
        low = raw.lower()
        if low in EXIT_WORDS:
            raise AbortInteractive()
        if low in SKIP_WORDS:
            return default
        if raw == "":
            if required:
                print("Field is required. Type an exit word to cancel.")
                continue
            return default
        return raw

def add_job_interactive(path: Path = DATA_FILE):
    """
    Interactive flow for adding a job.
    - If at any prompt the user types an exit word -> the add is cancelled.
    - For optional fields the user can type 'skip' to leave them blank.
    """
    print("Adding a new job. Type one of the exit words to cancel at any time.")
    try:
        role = _prompt_field("Role", required=True)
        company = _prompt_field("Company", required=True)
        status = _prompt_field(f"Status (choices: {', '.join(DEFAULT_STATUSES)})", required=False, default="applied")
    except AbortInteractive:
        print("Add cancelled.")
        return None
    job = add_job(role=role, company=company, status=status or "applied", path=path)
    print(f"Added: {job.role} @ {job.company} (id={job.id})")
    return job

# ---------- Predefined skills ----------
COMMON_SKILLS = [
    "Python", "Java", "C++", "SQL", "Excel", "Leadership", "Communication",
    "Project Management", "AWS", "Docker", "Kubernetes", "Git", "Linux",
    "Machine Learning", "Data Analysis", "Testing", "Automation", "JavaScript"
]

# ---------- Paste / free-text helper ----------
def extract_skills_from_text(lines: List[str]) -> List[str]:
    """
    Scans the pasted job description for known skills.
    Returns a list of matched skills.
    """
    text = " ".join(lines).lower()
    found_skills = [skill for skill in COMMON_SKILLS if skill.lower() in text]
    return found_skills

def add_from_text():
    """
    Interactive paste: user pastes job description, 
    function guesses role, company, location, job type, and skills.
    """
    print("Paste the job description (end with a blank line):")
    lines = []
    while True:
        line = input()
        if not line.strip():  # blank line = stop
            break
        lines.append(line.strip())

    if not lines:
        print("No text entered.")
        return

    # --- Guess role ---
    role = lines[0].split("-")[0].strip().title()

    # --- Guess company ---
    company = ""
    for line in lines[1:5]:
        m = re.search(r"at\s+([A-Za-z &]+)", line, re.I)
        if m:
            company = m.group(1).title()
            break
    if not company:
        for line in lines[1:5]:
            if not any(k in line.lower() for k in ["full-time", "part-time", "contract", "salary", "location", "job", "profile", "skills"]):
                company = line.title()
                break

    # --- Guess location using regex for postcodes ---
    location = ""
    POSTCODE_RE = re.compile(r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b", re.I)
    for line in lines:
        m = POSTCODE_RE.search(line)
        if m:
            location = m.group(0)
            break

    # --- Guess job type (Full-time, Part-time, Contract) ---
    job_type = "Full-time"
    for t in ["full-time", "part-time", "contract", "temporary", "internship", "permanent"]:
        if any(t in line.lower() for line in lines):
            job_type = t.title()
            break

    # --- Extract skills ---
    skills = extract_skills_from_text(lines)

    # --- Prompt user to confirm or edit ---
    role = input(f"Role [{role}]: ") or role
    company = input(f"Company [{company}]: ") or company
    location = input(f"Location [{location}]: ") or location
    job_type = input(f"Job Type [{job_type}]: ") or job_type
    status = input("Status (applied/interviewing/offer/etc) [applied]: ") or "applied"

    # --- Save job ---
    job = Job(
        id="",
        role=role,
        company=company,
        status=status,
        location=location,
        job_type=job_type,
        skills=skills
    )

    jobs = load_jobs()
    jobs.append(job)
    save_jobs(jobs)

    # --- Notification ---
    print(f"✅ Job added: {job.role} @ {job.company} ({job.job_type}) [{job.status}]")
    if job.skills:
        print(f"🛠 Skills detected: {', '.join(job.skills)}")


def _print_jobs(jobs: List[Job]):
    if not jobs:
        print("(no jobs)")
        return
    print(f"{'idx':>3}  {'id':36}  {'role':30}  {'company':20}  {'status':12}  {'updated_at'}")
    print("-" * 120)
    for i, j in enumerate(jobs):
        print(f"{i:>3}  {j.id:36}  {j.role[:30]:30}  {j.company[:20]:20}  {j.status:12}  {j.updated_at}")


# ---------- Natural-language-ish translator (small, keyword-based) ----------
def translate_free_text_to_cmd(text: str) -> Optional[Dict]:
    """
    Very small translator that attempts to map free text to a command.
    Returns a dict like {"cmd":"add", "role": "...", "company": "..."} or {"cmd":"list"}
    This is intentionally simple: keyword presence + a tiny regex-like parse.
    """
    t = text.lower()
    if any(k in t for k in ("add", "create", "apply", "applied for", "i applied")):
        # naive extraction: look for "role at company" or "role @ company"
        parts = t.replace("@", " at ").split(" at ")
        if len(parts) >= 2:
            role = parts[0].replace("add", "").replace("create", "").strip(" :")
            company = parts[1].strip()
            return {"cmd": "add", "role": role or "UNKNOWN ROLE", "company": company or "UNKNOWN COMPANY"}
        return {"cmd": "add"}
    if any(k in t for k in ("list", "show", "ls")):
        return {"cmd": "list"}
    if any(k in t for k in ("remove", "delete", "forget")):
        # try to find an id-looking token
        tokens = t.split()
        for tok in tokens:
            if len(tok) >= 8 and "-" in tok:  # heuristic for uuid-ish
                return {"cmd": "remove", "id": tok}
        return {"cmd": "remove"}
    if any(k in t for k in ("update", "change")):
        return {"cmd": "update"}
    if any(k in t for k in ("exit", "quit", "bye")):
        return {"cmd": "exit"}
    return None


# ---------- High-level CLI / command dispatcher ----------
def handle_command(argv: List[str]):
    """
    Programmatic entrypoint for main.py / CLI.
    
    Commands supported:
      job add [role company [status]]   -> add a job (interactive if no args)
      job paste                         -> add a job by pasting multi-line description
      job list [status]                  -> list jobs, optionally filtered by status
      job remove <id|index>             -> remove a job
      job update <id|index> [...]       -> update role, company, status
      job help                          -> show help
      (if no argv given, opens interactive shell)
    """
    if not argv:
        interactive_mode()
        return

    cmd = argv[0].lower()

    # ---------- Add ----------
    if cmd in ("add", "a"):
        if len(argv) >= 3:
            # Non-interactive add: job add "role" "company" [status]
            role = argv[1]
            company = argv[2]
            status = argv[3] if len(argv) > 3 else "applied"
            job = add_job(role, company, status)
            print(f"Added: {job.id}")
        else:
            # Interactive add
            add_job_interactive()

    # ---------- Paste ----------
    elif cmd == "paste":
        # Add a job by pasting multi-line job description
        add_from_text()
        return

    # ---------- List ----------
    elif cmd in ("list", "ls"):
        # List jobs, optionally filtered by status
        status = argv[1] if len(argv) > 1 else None
        jobs = list_jobs(status=status)
        _print_jobs(jobs)

    # ---------- Remove ----------
    elif cmd in ("remove", "rm", "delete"):
        if len(argv) < 2:
            print("Usage: job remove <id|index>")
            return
        removed = remove_job(argv[1])
        if removed:
            print(f"Removed {removed.id}")
        else:
            print("No job found with that id/index.")

    # ---------- Update ----------
    elif cmd in ("update", "up"):
        if len(argv) < 2:
            print("Usage: job update <id|index> [--role newrole] [--company newcompany] [--status newstatus]")
            return
        identifier = argv[1]
        kwargs = {}
        it = iter(argv[2:])
        for token in it:
            if token in ("--role", "-r"):
                kwargs["role"] = next(it, "")
            elif token in ("--company", "-c"):
                kwargs["company"] = next(it, "")
            elif token in ("--status", "-s"):
                kwargs["status"] = next(it, "")
        updated = update_job(identifier, **kwargs)
        if updated:
            print(f"Updated {updated.id}")
        else:
            print("No job found to update.")

    # ---------- Help ----------
    elif cmd in ("help", "-h", "--help"):
        print_help()

    # ---------- Fallback: free-text translator ----------
    else:
        tl = translate_free_text_to_cmd(" ".join(argv))
        if tl:
            if tl["cmd"] == "add":
                role = tl.get("role")
                company = tl.get("company")
                if role and company:
                    job = add_job(role, company, tl.get("status", "applied"))
                    print(f"Added {job.id}")
                    return
            if tl["cmd"] == "list":
                _print_jobs(list_jobs())
                return

        print("Unknown command. Try 'job help'.")

def print_help():
    """
    Prints help text for the job tracker commands.
    Shows both interactive and non-interactive usage.
    """
    print("""Shaco Core — Job tracker commands:

Add a job:
  job add                -> interactive add
  job add "<role>" "<company>" [status]  -> quick add from main

Paste a job description:
  job paste              -> add a job by pasting multi-line description

List jobs:
  job list [status]      -> list jobs (optionally filter by status)

Remove a job:
  job remove <id|index>  -> remove a job

Update a job:
  job update <id|index> [--role r] [--company c] [--status s] -> update

Other:
  job help               -> show this help
  (when interacting: type 'cancel' or 'exit' to abort an operation)
""")



def interactive_mode():
    print("Shaco Core — Job tracker interactive shell. Type 'help' for commands.")
    while True:
        try:
            raw = input("job> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            break
        if not raw:
            continue
        if raw.lower() in EXIT_WORDS:
            print("bye")
            break
        tokens = raw.split()
        # dispatch to handle_command for convenience
        handle_command(tokens)
