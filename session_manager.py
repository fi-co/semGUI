import os
import json
import datetime
import csv

def create_participant_folder(participant_id):
    """Create a folder for the participant if it doesn't exist"""
    folder_path = os.path.join("data", participant_id)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def validate_csv(filepath):
    """Verify if the provided file is a valid CSV"""
    try:
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # Read the first line to check if it is a valid format
            next(reader)
        return True
    except:
        return False

def create_session_log(participant_id, experimenter, wordlist_file, notes=""):
    """Create a log file fot the new session"""""
    session_data = {
        "participant_id": participant_id,
        "experimenter": experimenter,
        "wordlist_file": wordlist_file,
        "start_time": datetime.datetime.now().isoformat(),
        "interruption_time": None,
        "resume_time": None,
        "end_time": None,
        "interruption_type": None,
        "completed_trials":[],
        "current_trial": 1,
        "interrupted": False,
        "notes": notes
    }
    
    # Save the session
    log_path = os.path.join("data", participant_id, "log.json")
    with open(log_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    return session_data

def load_session(filepath):
    """LOad the session log data from the paritcipant JSON"""
    with open(filepath, 'r') as f:
        return json.load(f)

def update_session_log(session_data, completed_trial=None, interrupted=False):
    """Update the session log with the current state"""
    # If the trial was completed previously, add it up to the list
    if completed_trial is not None:
        if completed_trial not in session_data["completed_trials"]:
            session_data["completed_trials"].append(completed_trial)
            session_data["current_trial"] = completed_trial + 1 if completed_trial < 10 else 10 
    
    
    if interrupted:
        session_data["interruption_time"] = datetime.datetime.now().isoformat()
        session_data["interrupted"] = True
    
    
    if len(session_data["completed_trials"]) == 10:  # Assuming 10 trials NEED TO BE MODIFIED if you acted on settings.py/load_wordlist() 
        session_data["end_time"] = datetime.datetime.now().isoformat()
    
    # Save JSON for validation
    log_path = os.path.join("data", session_data["participant_id"], "log.json")
    with open(log_path, 'w') as f:
        json.dump(session_data, f, indent=2)