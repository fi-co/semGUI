import tkinter as tk
from tkinter import messagebox
from wordspace import WordSpace
from draggable import DraggableWord
from stackword import StackWord
from trial_manager import TrialManager
import random
from settings import GUI, VISUAL, EXPERIMENT, TEXT

class MainWindow(tk.Tk):
    # Class-level constants for configuration
    WINDOW_WIDTH = GUI['WINDOW_WIDTH']
    WINDOW_HEIGHT = GUI['WINDOW_HEIGHT']
    LEFT_PANEL_WIDTH = GUI['LEFT_PANEL_WIDTH']
    JITTER_RANGE_X = EXPERIMENT['WORD_JITTER']['RANGE_X']
    JITTER_RANGE_Y = EXPERIMENT['WORD_JITTER']['RANGE_Y']

    def __init__(self, participant_id=None, experimenter=None, words=None, 
             start_trial=1, recovery_mode=False, session_data=None):
        super().__init__()
    
        # Store session info
        self.participant_id = participant_id
        self.experimenter = experimenter
        self.start_trial = start_trial
        self.words_list = words
        self._words_list = []
        self.recovery_mode = recovery_mode
        self.session_data = session_data

        # Configuration methods
        self._configure_window()
        self._setup_trial_manager()
        self._create_layout()
        self._bind_keyboard_events()

    def _configure_window(self):
        """Set up window properties"""
        self.title(TEXT['WINDOW_TITLE'])
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

    def _setup_trial_manager(self):
        """Initialize trial management"""
        if not self.words_list or len(self.words_list) != EXPERIMENT['MAX_TRIALS']:
            raise ValueError(f"Word list must contain exactly {EXPERIMENT['MAX_TRIALS']} trials")
                            
        self.trial_manager = TrialManager(
            max_trials=EXPERIMENT['MAX_TRIALS'],
            participant_id=self.participant_id
        )
        self._words_list = list(self.words_list[self.start_trial - 1])

        self.update_title()

    def _create_layout(self):
        """Create GUI layout"""
        # Main container to hold all elements
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top frame for buttons
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=GUI['PADDING'])

        # Create button controls in top frame
        self.end_trial_btn = tk.Button(top_frame, text=TEXT['BUTTONS']['END_TRIAL'], command=self.end_trial)
        self.end_trial_btn.pack(side=tk.LEFT, padx=GUI['PADDING'])

        # Create button to reset zoom level
        self.reset_pov_btn = tk.Button(top_frame, text=TEXT['BUTTONS']['RECENTER'], command=self.reset_pov)
        self.reset_pov_btn.pack(side=tk.LEFT, padx=GUI['PADDING'])

         # Add highlight mode button
        self.highlight_btn = tk.Button(
            top_frame, 
            text=TEXT['BUTTONS']['HIGHLIGHT'].format("OFF"),
            command=self.toggle_highlight_mode,
            bg=VISUAL['COLORS']['HIGHLIGHT_OFF']
        )
        self.highlight_btn.pack(side=tk.LEFT, padx=GUI['PADDING'])

        # Content area container
        content_frame = tk.Frame(main_container)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left panel for word list
        self.left_panel = tk.Frame(content_frame, width=self.LEFT_PANEL_WIDTH, bg=VISUAL['COLORS']['PANEL_BG'])
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.left_panel.pack_propagate(False)  # Maintain width

        # Left panel title
        panel_title = tk.Label(self.left_panel, 
                              text=TEXT['PANEL_TITLE'], 
                              font=VISUAL['FONTS']['PANEL_TITLE'],
                              bg=VISUAL['COLORS']['PANEL_BG'])
        panel_title.pack(pady=GUI['PADDING']*2)

        # Create word stack frame inside left panel
        self.word_stack_frame = tk.Frame(self.left_panel, bg=VISUAL['COLORS']['PANEL_BG'])
        self.word_stack_frame.pack(fill=tk.BOTH, expand=True, padx=GUI['PADDING'], pady=GUI['PADDING'])

        # Canvas area container
        canvas_container = tk.Frame(content_frame)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create WordSpace
        self.word_space = WordSpace(canvas_container, words=[])
        self.word_space.pack(fill=tk.BOTH, expand=True)

        # Initialize word stack
        self.populate_word_stack()

    def _bind_keyboard_events(self):
        """Bind keyboard navigation events"""
        self.bind("<Left>", self.on_left_arrow)
        self.bind("<Right>", self.on_right_arrow)
        self.bind("<Up>", self.on_up_arrow)
        self.bind("<Down>", self.on_down_arrow)
        self.focus_set()

    def update_title(self):
        """Update window title with current trial number"""
        current_trial = min(self.trial_manager.get_trial_number(), self.trial_manager.max_trials)
        self.title(f"Word Relatedness GUI - Trial {current_trial} of {self.trial_manager.max_trials}")

    def reset_for_next_trial(self):
        """Reset everything for the next trial"""
        # Clear all draggable words
        for word in self.word_space.draggables:
            word.remove_from_canvas()
        self.word_space.draggables.clear()
        
        # Reset zoom and position
        self.word_space.reset_pov()
        
        # Get words for the current trial from words_list
        self._words_list = self.words_list[self.trial_manager.get_trial_number() - 1]
        
        # Clear and repopulate word stack
        for widget in self.word_stack_frame.winfo_children():
            widget.destroy()
        self.populate_word_stack()

    def create_word_at_center(self, word):
        """Compute center coordinates and create draggable word"""
        canvas_width = self.word_space.canvas.winfo_width()
        canvas_height = self.word_space.canvas.winfo_height()
        
        # Compute logical position at the center of the current viewport
        base_logical_x = (canvas_width / 2 - self.word_space.offset_x) / self.word_space.scale_factor
        base_logical_y = (canvas_height / 2 - self.word_space.offset_y) / self.word_space.scale_factor

        # Add jitter to the position
        jitter_x = random.uniform(-self.JITTER_RANGE_X/2, self.JITTER_RANGE_X/2)
        jitter_y = random.uniform(-self.JITTER_RANGE_Y/2, self.JITTER_RANGE_Y/2)

        # Apply jitter to logical coordinates
        logical_x = base_logical_x + jitter_x
        logical_y = base_logical_y + jitter_y

        # Create the draggable word
        new_word_obj = DraggableWord(self.word_space, logical_x, logical_y, word)
        self.word_space.draggables.append(new_word_obj)

        # Update everything
        self.word_space.update_all_positions()

    def on_left_arrow(self, event):
        # Move the offset rightwards (positive x) so the scene appears to shift left.
        self.word_space.pan_offset(dx=GUI['ARROW_PAN_DISTANCE'], dy=0)

    def on_right_arrow(self, event):
        self.word_space.pan_offset(dx=-GUI['ARROW_PAN_DISTANCE'], dy=0)

    def on_up_arrow(self, event):
        # Move the offset downwards (positive y) so the scene appears to shift up.
        self.word_space.pan_offset(dx=0, dy=GUI['ARROW_PAN_DISTANCE'])

    def on_down_arrow(self, event):
        self.word_space.pan_offset(dx=0, dy=-GUI['ARROW_PAN_DISTANCE'])

    def add_next_word(self):
        """Generate word lists at the left side"""
        if not self._words_list:
            messagebox.showinfo("Info", TEXT['MESSAGES']['NO_MORE_WORDS'])
            return

        new_word = self._words_list.pop(0)  # Get the next word from the queue

        self.create_word_at_center(new_word)

    def add_word_to_canvas(self, word):
        """Add a word from the stack to the canvas"""
        self.create_word_at_center(word)

    def populate_word_stack(self):
        """Add all words to the sidebar stack and clear the word list"""
        for word in self._words_list[:]:  # Create a copy to iterate
            StackWord(self.word_stack_frame, word, self.add_word_to_canvas)
        
        # Clear the words list after populating
        self._words_list.clear()

    def end_trial(self):
        """Compute word coordinates and end current trial"""
        words = self.word_space.get_draggable_words()
        
        # Check if all words from the stack are used
        if self.word_stack_frame.winfo_children():
            messagebox.showwarning("Insufficient Words", 
                                TEXT['MESSAGES']['INSUFFICIENT_WORDS'])
            return

        try:
            # Save trial data (also handles final save if last trial)
            self.trial_manager.save_trial_data(words)
            
            # Update session log if we have session data
            if self.session_data:
                from session_manager import update_session_log
                update_session_log(self.session_data, completed_trial=self.trial_manager.current_trial)
            
            # Advance to next trial
            continue_experiment, message = self.trial_manager.advance_trial()
            
            if continue_experiment:
                messagebox.showinfo(TEXT['MESSAGES']['TRIAL_COMPLETED'], message)
                self.update_title()
                self.reset_for_next_trial()
            else:
                messagebox.showinfo(TEXT['MESSAGES']['EXPERIMENT_COMPLETED'], message)
                self.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def reset_pov(self):
        """Reset zoom/POV level in the wordspace"""
        self.word_space.reset_pov()
    
    def toggle_highlight_mode(self):
        """Toggle highlight mode for word selection"""
        self.word_space.toggle_highlight_mode()
        is_active = self.word_space.highlight_mode
        self.highlight_btn.config(
            text=TEXT['BUTTONS']['HIGHLIGHT'].format('ON' if is_active else 'OFF'),
            bg=VISUAL['COLORS']['HIGHLIGHT_ON'] if is_active else VISUAL['COLORS']['HIGHLIGHT_OFF']
        )