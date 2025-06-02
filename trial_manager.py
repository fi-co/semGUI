import csv
from typing import List
from datetime import datetime
import os
from settings import TRIAL_MANAGER

class TrialManager:
    def __init__(self, max_trials=None, participant_id=None):
        self.current_trial = 1
        self.max_trials = max_trials if max_trials is not None else TRIAL_MANAGER['MAX_TRIALS']
        self.all_trial_results = []
        self.participant_id = participant_id 

    def get_trial_number(self):
        return self.current_trial
        
    def is_experiment_complete(self):
        return self.current_trial > self.max_trials
        
    def advance_trial(self) -> tuple[bool, str]:
        if self.current_trial >= self.max_trials:
            return False, TRIAL_MANAGER['MESSAGES']['COMPLETED']
        prev_trial = self.current_trial
        self.current_trial += 1
        return True, TRIAL_MANAGER['MESSAGES']['TRIAL_PROGRESS'].format(prev_trial=prev_trial, next_trial=self.current_trial)


    def _convert_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """Convert coordinates from canvas to output coordinate system.
        
        Canvas uses top-left origin with Y increasing downward.
        Output uses bottom-left origin with Y increasing upward.
        """
        if TRIAL_MANAGER['COORDINATES']['INVERT_Y']:
            return x, -y
        return x, y

    def save_trial_data(self, words) -> None:
        """Store trial data and save to CSV if experiment is complete.
        
        Args:
            words: List[DraggableWord]: Words with their positions and states
                
        Raises:
            ValueError: If number of words is unexpected or missing
        """
        # Use stored participant_id
        if not self.participant_id:
            raise ValueError(TRIAL_MANAGER['MESSAGES']['ERRORS']['NO_PARTICIPANT'])
    
        # Validate words count
        if not words or len(words) == 0:
            raise ValueError(TRIAL_MANAGER['MESSAGES']['ERRORS']['NO_WORDS'])
        
        # Check if we've already saved all trials
        if len(self.all_trial_results) >= self.max_trials * TRIAL_MANAGER['WORDS_PER_TRIAL']:
            raise ValueError(TRIAL_MANAGER['MESSAGES']['ERRORS']['TRIALS_EXCEEDED'])
        
        # Store current trial data
        coordinates = []
        for word in words:
            x_coord, y_coord = self._convert_coordinates(word.logical_x, word.logical_y)
            word_data = {
                'trial_number': self.current_trial,
                'word': word.word,
                'x_coord': x_coord,
                'y_coord': y_coord,  # Y is now handled by _convert_coordinates
                'highlighted': word.is_highlighted
            }
            coordinates.append(word_data)
        
        self.all_trial_results.extend(coordinates)
        
        # If this was the last trial, save everything to CSV
        if self.current_trial == self.max_trials:
            expected_words = TRIAL_MANAGER['WORDS_PER_TRIAL'] * self.max_trials
            if len(self.all_trial_results) != expected_words:
                raise ValueError(
                    TRIAL_MANAGER['MESSAGES']['ERRORS']['WRONG_WORD_COUNT'].format(
                        expected=expected_words, actual=len(self.all_trial_results)
                    )
                )
            
            participant_dir = os.path.join(TRIAL_MANAGER['PATHS']['DATA_DIRECTORY'], str(self.participant_id))
            os.makedirs(participant_dir, exist_ok=True)

            # Save to CSV with participant ID in filename
            timestamp = datetime.now().strftime(TRIAL_MANAGER['TIMESTAMP_FORMAT'])
            filename = os.path.join(
                participant_dir, 
                TRIAL_MANAGER['PATHS']['RESULTS_FILENAME_TEMPLATE'].format(timestamp=timestamp)
            )
            
            fieldnames = TRIAL_MANAGER['CSV_FIELDS']
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                writer.writerows(self.all_trial_results)
            
            return filename