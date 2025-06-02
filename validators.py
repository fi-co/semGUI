import re

def validate_participant_id(participant_id):
    """Verify particant ID format"""
    pattern = r'^P\d+$' # P followed by digists P001, P002 and so on
    return bool(re.match(pattern, participant_id))