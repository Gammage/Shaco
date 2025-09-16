# modules/job_tracker.py
import json
import os

# Path to JSON file inside /data
# DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "job_data.json")

#incase i ever move the file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "jobs.json")

from datetime import datetime

def load_jobs():
    """Load jobs from JSON file, or return empty list if file missing."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_jobs(jobs):
    """Save jobs list to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(jobs, f, indent=4)

def add_job(company, role, status):
    """Add a new job application to the tracker."""
    jobs = load_jobs()
    timestamp = datetime.now().isoformat()  # current time as string
    jobs.append({
        "company": company, 
        "role": role, 
        "status": status,
         "updated_at": timestamp
        })
    save_jobs(jobs)
    print(f"✅ Job added: {role} at {company} (status: {status})")
    
def remove_job(index):
    jobs = load_jobs()
    if 0 <= index < len(jobs):
        removed = jobs.pop(index)
        save_jobs(jobs)
        print(f"❌ Removed: {removed['role']} at {removed['company']}")
    else:
        print("⚠️ Invalid job number.")

def list_jobs():
    """List all tracked jobs."""
    jobs = load_jobs()
    if not jobs:
        print("No jobs saved yet.")
        return
    print("\n📋 Your Job Applications:")
    for i, job in enumerate(jobs, start=1):
        print(f"{i}. {job['role']} at {job['company']} — {job['status']}")

def update_job(index, status):
    """Update the status of a job by its index number."""
    jobs = load_jobs()
    if 0 <= index < len(jobs):
        jobs[index]["status"] = status
        jobs[index]["updated_at"] = datetime.now().isoformat()
        save_jobs(jobs)
        print(f"🔄 Updated: {jobs[index]['role']} at {jobs[index]['company']} → {status}")
    else:
        print("⚠️ Invalid job number.")

            
def interactive_mode(command=None):
    """
    Run Job Tracker interactively. 
    If `command` is provided, execute that single command instead of prompting user.
    """
    while True:
        if command is None:
            cmd = input("(job)> ").strip().lower()
        else:
            cmd = command.strip().lower()

        if cmd == "help":
            print("Commands: add, list, remove, exit")
        
        elif cmd == "add":
            title = input("Job title: ")
            company = input("Company: ")
            status = input("Status (applied/interview/etc.): ")
            add_job(title, company, status)
        
        elif cmd == "list":
            list_jobs()
        
        elif cmd == "remove":
            list_jobs()
            index = int(input("Enter job number to remove: ")) - 1
            remove_job(index)
        
        elif cmd == "exit":
            print("Leaving Job Tracker.\n")
            break
        
        else:
            print("Unknown command. Type 'help'.")

        # If we were given a single command (from Shaco), exit after running it
        if command is not None:
            break
