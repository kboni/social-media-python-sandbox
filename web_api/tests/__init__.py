import sys, os

# Inserting path to the main app's files
app_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_path + '/../../app/')