import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import datetime
from settings import PATHS, ENTRY_WINDOW, ENTRY_WINDOW_VISUAL, MESSAGES
from validators import validate_participant_id
from session_manager import create_session_log, load_session, create_participant_folder, validate_csv
from controls import MainWindow
from settings import EXPERIMENT

class EntryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Experiment Setup")
        self.geometry(f"{ENTRY_WINDOW['WINDOW_WIDTH']}x{ENTRY_WINDOW['WINDOW_HEIGHT']}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Input variables
        self.participant_id = tk.StringVar()
        self.experimenter_name = tk.StringVar()
        self.notes = tk.StringVar()
        self.wordlist_path = tk.StringVar()
        self.recovery_path = tk.StringVar()
        
        # Flags for recovery mode and session data
        self.recovery_mode = False
        self.session_data = None
        
        # Add validation state tracking
        self.data_verified = False
        
        self.create_widgets()
        
        # Add trace to all input variables to handle changes
        self.participant_id.trace_add("write", self.on_input_change)
        self.experimenter_name.trace_add("write", self.on_input_change)
        self.notes.trace_add("write", self.on_input_change)
        self.wordlist_path.trace_add("write", self.on_input_change)
        self.recovery_path.trace_add("write", self.on_input_change)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding=ENTRY_WINDOW['MAIN_FRAME_PADDING'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # New session setup 
        ttk.Label(main_frame, text="Experiment Setup", 
                 font=ENTRY_WINDOW_VISUAL['TITLE_FONT']).grid(row=0, column=0, columnspan=3, pady=10)
        
        # ID
        ttk.Label(main_frame, text="Participant ID").grid(row=1, column=0, sticky=tk.W, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        id_entry = ttk.Entry(main_frame, textvariable=self.participant_id)
        id_entry.grid(row=1, column=1, sticky=tk.EW, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        self.id_validation_label = ttk.Label(main_frame, text="")
        self.id_validation_label.grid(row=1, column=2, padx=ENTRY_WINDOW['ELEMENT_PADDING'])
        
        # Check ID validity on-the-fly
        self.participant_id.trace_add("write", self.on_id_change)
        
        # Wordlist loader
        ttk.Label(main_frame, text="Wordlist File:").grid(row=2, column=0, sticky=tk.W, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        ttk.Entry(main_frame, textvariable=self.wordlist_path).grid(row=2, column=1, sticky=tk.EW, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        ttk.Button(main_frame, text="...", command=self.browse_wordlist).grid(row=2, column=2, padx=ENTRY_WINDOW['ELEMENT_PADDING'])
        
        # Experimenter
        ttk.Label(main_frame, text="Experimenter:").grid(row=3, column=0, sticky=tk.W, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        ttk.Entry(main_frame, textvariable=self.experimenter_name).grid(row=3, column=1, sticky=tk.EW, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        
        # Notes and misc 
        ttk.Label(main_frame, text="Notes:").grid(row=4, column=0, sticky=tk.W, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        ttk.Entry(main_frame, textvariable=self.notes).grid(row=4, column=1, sticky=tk.EW, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        
   
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=3, sticky=tk.EW, pady=ENTRY_WINDOW['SEPARATOR_PADDING'])
        
        # Receovery past session
        ttk.Label(main_frame, text="Recover Interrupted Session", 
                 font=ENTRY_WINDOW_VISUAL['SECTION_TITLE_FONT']).grid(row=6, column=0, columnspan=3, pady=10)
        
        # Recover data
        ttk.Label(main_frame, text="Recover data:").grid(row=7, column=0, sticky=tk.W, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        ttk.Entry(main_frame, textvariable=self.recovery_path).grid(row=7, column=1, sticky=tk.EW, pady=ENTRY_WINDOW['ELEMENT_PADDING'])
        ttk.Button(main_frame, text="...", command=self.browse_recovery).grid(row=7, column=2, padx=ENTRY_WINDOW['ELEMENT_PADDING'])
        
        
        self.recovery_info = ttk.Label(main_frame, text="")
        self.recovery_info.grid(row=8, column=0, columnspan=3, pady=10)
        
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        # Verification and start buttons
        ttk.Button(button_frame, text="Verify Data", command=self.verify_data).pack(side=tk.LEFT, padx=10)
        self.start_button = ttk.Button(button_frame, text="Start Experiment", 
                                      command=self.start_experiment, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # Configurazione del grid
        main_frame.columnconfigure(1, weight=1)
    
    def on_id_change(self, *args):
        """Real time validation of particapant id"""
        participant_id = self.participant_id.get().strip()
        if not participant_id:
            self.id_validation_label.config(text="")
            return
            
        if validate_participant_id(participant_id):
            # Check if participant ID already exists
            participant_dir = os.path.join(PATHS['DATA_DIRECTORY'], participant_id)
            if os.path.exists(participant_dir):
                self.id_validation_label.config(text="⚠️ ID esistente", foreground=ENTRY_WINDOW_VISUAL['VALIDATION_COLORS']['WARNING'])
            else:
                self.id_validation_label.config(text="✓", foreground=ENTRY_WINDOW_VISUAL['VALIDATION_COLORS']['SUCCESS'])
        else:
            self.id_validation_label.config(text="❌", foreground=ENTRY_WINDOW_VISUAL['VALIDATION_COLORS']['ERROR'])
    
    def browse_wordlist(self):
        """Apre il file dialog per selezionare il file CSV delle word list"""
        filepath = filedialog.askopenfilename(
            title=MESSAGES['DIALOGS']['FILE_DIALOGS']['WORDLIST_TITLE'],
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.wordlist_path.set(filepath)
            # Force verification after file selection
            self.data_verified = False
            self.start_button.config(state=tk.DISABLED)

    def browse_recovery(self):
        """Opens the dialog file to select the JSON recovery"""
        filepath = filedialog.askopenfilename(
            title=MESSAGES['DIALOGS']['FILE_DIALOGS']['RECOVERY_TITLE'],
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.recovery_path.set(filepath)
            self.try_load_recovery_data(filepath)
            # Force verification after recovery file selection
            self.data_verified = False
            self.start_button.config(state=tk.DISABLED)
    
    def try_load_recovery_data(self, filepath):
        """Attempts to lead recovery data from the selected JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Verify recovery data structure
            required_fields = ["participant_id", "experimenter", "wordlist_file", 
                              "completed_trials", "current_trial"]
            
            if all(field in data for field in required_fields):
                # Populate fields with recovery data
                self.participant_id.set(data["participant_id"])
                self.experimenter_name.set(data["experimenter"])

                # Find worlist file path
                wordlist_path = data["wordlist_file"]
                if not os.path.isabs(wordlist_path):
                    wordlist_path = os.path.join(os.path.dirname(filepath), "..", wordlist_path)
                    wordlist_path = os.path.normpath(wordlist_path)
                
                if os.path.exists(wordlist_path):
                    self.wordlist_path.set(wordlist_path)
                else:
                    messagebox.showwarning("File not found", 
                                          f"File '{data['wordlist_file']}' not found.")
                
                # Show recovery info
                completed = len(data["completed_trials"])
                current = data["current_trial"]
                
                self.recovery_info.config(
                    text=f"Experiment for {data['participant_id']} stopped after trial {completed}/10.\n"
                         f"Resume from trial {current}?",
                    foreground="blue"
                )
                
                # Switch to recovery mode
                self.recovery_mode = True
                self.session_data = data
            else:
                messagebox.showerror("Invalid JSON", 
                                    "The selected file does not contain valid recovery data.")
                self.recovery_mode = False
                self.session_data = None
                self.recovery_info.config(text="")
                
        except Exception as e:
            messagebox.showerror("Error Loading Recovery Data", 
                                 MESSAGES['ERRORS']['LOAD_ERROR'].format(e))
            self.recovery_mode = False
            self.session_data = None
    
    def on_input_change(self, *args):
        """Called whenever any input field changes"""
        # Disable start button if any change is made after verification
        if self.data_verified:
            self.data_verified = False
            self.start_button.config(state=tk.DISABLED)

    def verify_data(self):
        """Verify the input data before starting the experiment"""
        try:
            if self.recovery_mode and self.session_data:
                # While in recovery mode, we need to valiudate the recovery data 
                if not os.path.exists(self.wordlist_path.get()):
                    messagebox.showerror("Missing file", 
                                        MESSAGES['VALIDATION']['MISSING_FILE'])
                    return
                    
                # Verify participant ID exists
                participant_dir = os.path.join(PATHS['DATA_DIRECTORY'], self.participant_id.get())
                if not os.path.exists(participant_dir):
                    messagebox.showerror("Dati mancanti", 
                                        "La cartella del partecipante non è stata trovata.")
                    return
                    
                # Verify recovery JSON file
                result_file = os.path.join(participant_dir, f"{self.participant_id.get()}{PATHS['RESULT_FILE_SUFFIX']}")
                if not os.path.exists(result_file):
                    messagebox.showerror("File risultati mancante", 
                                        "Il file dei risultati non è stato trovato.")
                    return
                    
                # If we get here, validation passed
                self.data_verified = True
                self.start_button.config(state=tk.NORMAL)
                messagebox.showinfo("Verifica completata", 
                                  MESSAGES['VALIDATION']['RECOVERY_SUCCESS'].format(self.session_data['current_trial']))
                
            else:
                # Swirch to new session validation
                if not self.participant_id.get() or not validate_participant_id(self.participant_id.get()):
                    messagebox.showerror("ID non valido", 
                                        MESSAGES['VALIDATION']['INVALID_ID'])
                    return
                    
                
                participant_dir = os.path.join(PATHS['DATA_DIRECTORY'], self.participant_id.get())
                if os.path.exists(participant_dir):
                    response = messagebox.askyesno("ID Already Existing", 
                                                 MESSAGES['VALIDATION']['EXISTING_ID'].format(self.participant_id.get()))
                    if not response:
                        return
                
                
                if not self.wordlist_path.get() or not os.path.exists(self.wordlist_path.get()):
                    messagebox.showerror("Missing File", 
                                        MESSAGES['VALIDATION']['MISSING_FILE'])
                    return
                    
                
                if not validate_csv(self.wordlist_path.get()):
                    messagebox.showerror("File Not Valid", 
                                        MESSAGES['VALIDATION']['INVALID_CSV'])
                    return
                    
                
                if not self.experimenter_name.get():
                    messagebox.showerror("Missing Experimenter", 
                                        MESSAGES['VALIDATION']['MISSING_EXPERIMENTER'])
                    return
                
                # If we get here, validation passed
                self.data_verified = True
                self.start_button.config(state=tk.NORMAL)
                messagebox.showinfo("Verification Successful", 
                                  MESSAGES['VALIDATION']['VALIDATION_SUCCESS'])
                
        except Exception as e:
            self.data_verified = False
            self.start_button.config(state=tk.DISABLED)
            messagebox.showerror("Errore di validazione", str(e))

    def start_experiment(self):
        """Start the experiment"""
        try:
            # Load wordlist first (for both modes)
            words_list = load_wordlist(self.wordlist_path.get())
            if not words_list:
                raise ValueError("Failed to load wordlist")

            if self.recovery_mode and self.session_data:
                # Recovery mode setup
                self.session_data["resume_time"] = datetime.datetime.now().isoformat()
                
                # Save updated JSON
                with open(self.recovery_path.get(), 'w') as f:
                    json.dump(self.session_data, f, indent=2)
                
                # Get recovery trial number
                start_trial = self.session_data["current_trial"]
                
                # Create main window with recovery settings
                app = MainWindow(
                    participant_id=self.participant_id.get(),
                    experimenter=self.experimenter_name.get(),
                    words=words_list,
                    start_trial=start_trial,
                    recovery_mode=True,
                    session_data=self.session_data
                )
            else:
                # New experiment setup
                participant_id = self.participant_id.get()
                
                # Create participant folder
                create_participant_folder(participant_id)
                
                # Create session log
                session_data = create_session_log(
                    participant_id=participant_id,
                    experimenter=self.experimenter_name.get(),
                    wordlist_file=self.wordlist_path.get(),
                    notes=self.notes.get()
                )
                
                # Create main window with new experiment settings
                app = MainWindow(
                    participant_id=participant_id,
                    experimenter=self.experimenter_name.get(),
                    words=words_list,
                    start_trial=1,
                    recovery_mode=False,
                    session_data=session_data
                )

            
            self.withdraw()
            app.wait_window()
            self.quit()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Failed to Start Experiment", 
                MESSAGES['ERRORS']['START_ERROR'].format(e)
            )
    
    def on_closing(self):
        """Ask for confirmation before closing the window"""
        if messagebox.askokcancel("Uscita", MESSAGES['DIALOGS']['EXIT_CONFIRM']):
            self.master.destroy()  

# Support fuction to load wordlist from CSV
def load_wordlist(filepath):
    """Load words from CSV file."""
    import csv
    training_trials = []
    main_trials = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            # Change delimiter to semicolon
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Skip header row
            
            # Load all rows
            all_rows = list(reader)
            
            # Debug print
            print(f"Total rows read: {len(all_rows)}")
            print("First row content:", all_rows[0] if all_rows else "No rows")
            
            # Extract training trials (first 2 rows)
            for i in range(min(EXPERIMENT['TRAINING']['TRIALS'], len(all_rows))):
                # Get all columns except first (trial number)
                trial_words = [word.strip() for word in all_rows[i][1:] if word.strip()]
                print(f"Training trial {i+1} raw data: {all_rows[i]}")
                print(f"Training trial {i+1} words: {len(trial_words)} - {trial_words}")
                if trial_words:  # Only add if row contains words
                    training_trials.append(trial_words)
            
            # Extract main trials (remaining rows)
            for i, row in enumerate(all_rows[EXPERIMENT['TRAINING']['TRIALS']:]):
                trial_words = [word.strip() for word in row[1:] if word.strip()]
                if trial_words:  # Only add if row contains words
                    main_trials.append(trial_words)
                    print(f"Main trial {i+1}: {len(trial_words)} words loaded")
            
            # Debug print
            print(f"Training trials loaded: {len(training_trials)}")
            print(f"Main trials loaded: {len(main_trials)}")
            
            if not training_trials and not main_trials:
                raise ValueError("No valid words found in the CSV file. Please check the file format.")
            
            # Combine trials in correct order
            return training_trials + main_trials

    except Exception as e:
        messagebox.showerror("Error Loading Wordlist", 
                            f"Failed to load wordlist:\nError type: {type(e)}\nError: {str(e)}\n\n"
                            f"Expected format:\n"
                            f"trial;word1;word2;word3;...\n"
                            f"1;apple;banana;orange;...\n"
                            f"2;cat;dog;fish;...\n")
        return None
