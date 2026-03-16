import sys
import os

sys.path.insert(0, os.path.abspath('src'))

try:
    import emova.api.main
    print("Application emova.api.main imported successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
