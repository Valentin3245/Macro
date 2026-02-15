
import os
import time
import json
from jnius import autoclass

PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')

service = PythonService.mService

def run_service():
    while True:
        time.sleep(1)

if __name__ == '__main__':
    run_service()