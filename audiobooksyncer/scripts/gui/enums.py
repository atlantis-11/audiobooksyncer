from enum import Enum

ActionButtonState = Enum('ActionButtonState', ('Run', 'Next', 'Cancel'))
ProcessingState = Enum('ProcessingState', ('NotProcessing', 'Processing', 'Waiting'))
InputType = Enum('InputType', ('src', 'tgt', 'audio', 'output'))
Settings = Enum('Settings', ('aeneas_processes', 'aeneas_dtw_margin'))
