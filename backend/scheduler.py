import threading
import time
from datetime import datetime

class TaskScheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
    
    def add_task(self, func, interval_seconds, name=None):
        task = {
            'func': func,
            'interval': interval_seconds,
            'name': name or func.__name__,
            'last_run': None
        }
        self.tasks.append(task)
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print("Task scheduler started")
    
    def stop(self):
        self.running = False
        print("Task scheduler stopped")
    
    def _run(self):
        while self.running:
            current_time = time.time()
            
            for task in self.tasks:
                if task['last_run'] is None or (current_time - task['last_run']) >= task['interval']:
                    try:
                        print(f"Running task: {task['name']}")
                        task['func']()
                        task['last_run'] = current_time
                    except Exception as e:
                        print(f"Error in task {task['name']}: {e}")
            
            time.sleep(10)
