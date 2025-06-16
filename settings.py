"""
Configuration settings for the Word Relatedness GUI application
"""

__all__ = [
    'GUI', 'VISUAL', 'EXPERIMENT', 'TEXT',
    'PATHS', 'ENTRY_WINDOW', 'ENTRY_WINDOW_VISUAL',
    'MESSAGES', 'TRIAL_MANAGER', 'DRAGGABLE_WORD',
    'CANVAS_INTERACTION', 'WORDSPACE'
]

#  ----------------- controls.py Settings
# GUI Settings
GUI = {
    'WINDOW_WIDTH': 1600,
    'WINDOW_HEIGHT': 900,
    'LEFT_PANEL_WIDTH': 200,
    'ARROW_PAN_DISTANCE': 30,
    'PADDING': 5,  # General padding value
}

# Visual Settings
VISUAL = {
    'COLORS': {
        'PANEL_BG': 'lightgrey',
        'HIGHLIGHT_ON': 'yellow',
        'HIGHLIGHT_OFF': 'lightgray',
    },
    'FONTS': {
        'PANEL_TITLE': ('Arial', 12, 'bold'),
    }
}

# Experimental Parameters
EXPERIMENT = {
    'TRAINING': {
        'TRIALS': 2,  # Number of training trials
        'WORDS_PER_TRIAL': 10  # Words per training trial
    },
    'MAIN': {
        'TRIALS': 9,  # Number of main trials
        'WORDS_PER_TRIAL': 17  # Words per main trial
    },
    'WORD_JITTER': {
        'RANGE_X': 60,
        'RANGE_Y': 60
    }
}

# Text Strings
TEXT = {
    'WINDOW_TITLE': 'Word Relatedness GUI',
    'PANEL_TITLE': 'Available Words',
    'BUTTONS': {
        'END_TRIAL': 'End Trial',
        'RECENTER': 'Recenter POV',
        'HIGHLIGHT': 'Highlight Mode: {}'
    },
    'MESSAGES': {
        'NO_MORE_WORDS': 'No more words to add.',
        'INSUFFICIENT_WORDS': 'You must use all the words before ending the trial.',
        'TRIAL_COMPLETED': 'Trial Completed',
        'EXPERIMENT_COMPLETED': 'Experiment Completed'
    }
}

# Path Settings
PATHS = {
    'DATA_DIRECTORY': 'data',
    'RESULT_FILE_SUFFIX': '_result.csv',
}
 
# Entry Window GUI Settings
ENTRY_WINDOW = {
    'WINDOW_WIDTH': 600,
    'WINDOW_HEIGHT': 500,
    'MAIN_FRAME_PADDING': 20,
    'ELEMENT_PADDING': 5,
    'SEPARATOR_PADDING': 15
}

# Entry Window Visual Settings
ENTRY_WINDOW_VISUAL = {
    'TITLE_FONT': ('Arial', 14, 'bold'),
    'SECTION_TITLE_FONT': ('Arial', 12, 'bold'),
    'VALIDATION_COLORS': {
        'SUCCESS': 'green',
        'WARNING': 'orange',
        'ERROR': 'red'
    }
}

# Validation Messages
MESSAGES = {
    'VALIDATION': {
        'INVALID_ID': 'Please enter a valid participant ID.',
        'EXISTING_ID': 'The ID {} already exists. Overwrite the data?',
        'MISSING_FILE': 'Please select a valid wordlist file.',
        'INVALID_CSV': 'The wordlist file is not a valid CSV.',
        'MISSING_EXPERIMENTER': 'Please enter the experimentr\'s name',
        'VALIDATION_SUCCESS': 'All data is valid. Ready to start the experiment.',
        'RECOVERY_SUCCESS': 'Recovery data valid. Ready to resume from trial {}.'
    },
    'ERRORS': {
        'LOAD_ERROR': 'Unable to load recovery file:\n{}',
        'START_ERROR': 'Unable to start experiment:\n{}'
    },
    'DIALOGS': {
        'EXIT_CONFIRM': 'Are you sure you want to exit?',
        'FILE_DIALOGS': {
            'WORDLIST_TITLE': 'Select wordlist CSV file',
            'RECOVERY_TITLE': 'Select JSON revorery file'
        }
    }
}

# ----------------- trialmanager.py Settings
TRIAL_MANAGER = {
    'MAX_TRIALS': 12,
    'WORDS_PER_TRIAL': 5,
    'TIMESTAMP_FORMAT': '%Y%m%d_%H%M%S',
    'PATHS': {
        'DATA_DIRECTORY': 'data',
        'RESULTS_FILENAME_TEMPLATE': 'experiment_results_{timestamp}.csv'
    },
    'CSV_FIELDS': ['trial_number', 'word', 'x_coord', 'y_coord', 'highlighted'],
    'MESSAGES': {
        'COMPLETED': 'All trials completed!',
        'TRIAL_PROGRESS': 'Trial {prev_trial} complete. Starting trial {next_trial}',
        'ERRORS': {
            'NO_PARTICIPANT': 'participant_id is required for saving results',
            'NO_WORDS': 'No words provided for saving',
            'TRIALS_EXCEEDED': 'Maximum number of trials reached',
            'WRONG_WORD_COUNT': 'Trial completed with {actual} words'
        }
    },
    'COORDINATES': {
        'INVERT_Y': True,  # Whether to invert Y coordinates in output (recommended)
        'CANVAS_ORIGIN': 'top-left',  # Canvas coordinate system origin
        'OUTPUT_ORIGIN': 'bottom-left'  # Desired output coordinate system origin
    }
}

# ----------------- draggable.py Settings
DRAGGABLE_WORD = {
    'SIZE': {
        'DEFAULT_WIDTH': 60,
        'DEFAULT_HEIGHT': 60
    },
    'COLORS': {
        'FILL': 'gray',
        'OUTLINE': 'black',
        'TEXT': 'white',
        'HIGHLIGHT': 'red'
    },
    'FONT': {
        'FAMILY': 'Arial',
        'SIZE': 10,
        'STYLE': ''  # Normal
    },
    'OUTLINE': {
        'DEFAULT_WIDTH': 2,
        'HIGHLIGHT_WIDTH': 4
    },
    'TAGS': {
        'DRAGGABLE': 'draggable'  # Tag for canvas elements
    }
}

# Canvas Interaction Settings
CANVAS_INTERACTION = {
    'BOUNDARY_MARGIN': 0,  # Margin from canvas edges
    'DRAG_ENABLED': True,  # Enable/disable dragging
    'HIGHLIGHT_ENABLED': True  # Enable/disable highlighting
}

# ----------------- wordspace.py Settings
WORDSPACE = {
    'CANVAS': {
        'DEFAULT_WIDTH': 1240,
        'DEFAULT_HEIGHT': 700,
        'BACKGROUND_COLOR': 'white',
        'MARGINS': {
            'SAFETY_MARGIN': 50,
            'PADDING_FACTOR': 1.2
        }
    },
    'ZOOM': {
        'MIN_SCALE': 1.0,
        'MAX_SCALE': 5.0,
        'ZOOM_FACTOR': 1.11111111119,
        'DISPLAY_FORMAT': 'Zoom: {}%',
        'MAX_ZOOM_PERCENTAGE': 500
    },
    'WORD_PLACEMENT': {
        'INITIAL_X_SPACING': 100,
        'INITIAL_Y_POSITION': 150,
        'INITIAL_X_OFFSET': 50
    },
    'INTERACTION': {
        'HIGHLIGHT_CURSOR': 'hand2',
        'DEFAULT_CURSOR': '',
    },
    'LABELS': {
        'ZOOM_LABEL': {
            'BACKGROUND': 'white',
            'FOREGROUND': 'black',
            'ANCHOR': 's',
            'RELATIVE_X': 0.5,
            'RELATIVE_Y': 1.0
        }
    }
}
