import threading
import time
from datetime import datetime, timedelta

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


class TrainingScheduler:
    """
    Scheduler for automated ML model training.
    Supports weekly full retraining and manual triggers.
    """
    def __init__(self, training_service, data_processor, model_manager, evaluation_service, logger=None):
        self.training_service = training_service
        self.data_processor = data_processor
        self.model_manager = model_manager
        self.evaluation_service = evaluation_service
        self.logger = logger
        self.scheduler = TaskScheduler()
        self.training_in_progress = False
        self.last_training_result = None
        
        # Import here to avoid circular dependency
        from ml.training_history import TrainingHistoryManager
        self.history_manager = TrainingHistoryManager()
        
    def schedule_weekly_training(self, day_of_week=6, hour=2, minute=0):
        """
        Schedule weekly full retraining.
        
        Args:
            day_of_week: 0=Monday, 6=Sunday (default: Sunday)
            hour: Hour of day (0-23, default: 2 AM)
            minute: Minute of hour (0-59, default: 0)
        """
        # Calculate seconds until next scheduled time
        interval_seconds = 7 * 24 * 60 * 60  # One week in seconds
        
        # Add task to scheduler
        self.scheduler.add_task(
            func=self._run_scheduled_training,
            interval_seconds=interval_seconds,
            name='weekly_model_training'
        )
        
        if self.logger:
            self.logger.info(f"Scheduled weekly training: Day {day_of_week}, {hour:02d}:{minute:02d}")
        else:
            print(f"Scheduled weekly training: Day {day_of_week}, {hour:02d}:{minute:02d}")
    
    def start(self):
        """Start the training scheduler."""
        self.scheduler.start()
        if self.logger:
            self.logger.info("Training scheduler started")
        else:
            print("Training scheduler started")
    
    def stop(self):
        """Stop the training scheduler."""
        self.scheduler.stop()
        if self.logger:
            self.logger.info("Training scheduler stopped")
        else:
            print("Training scheduler stopped")
    
    def trigger_manual_training(self):
        """
        Manually trigger a training session.
        Returns immediately and runs training in background.
        
        Returns:
            dict: Status message
        """
        if self.training_in_progress:
            return {
                'success': False,
                'message': 'Training already in progress'
            }
        
        # Run training in background thread
        thread = threading.Thread(target=self._run_manual_training, daemon=True)
        thread.start()
        
        return {
            'success': True,
            'message': 'Training started',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_training_status(self):
        """
        Get current training status.
        
        Returns:
            dict: Training status information
        """
        return {
            'training_in_progress': self.training_in_progress,
            'last_training_result': self.last_training_result,
            'scheduler_running': self.scheduler.running
        }
    
    def _run_scheduled_training(self):
        """Internal method for scheduled training execution."""
        if self.training_in_progress:
            if self.logger:
                self.logger.warning("Skipping scheduled training - training already in progress")
            return
        
        if self.logger:
            self.logger.info("Starting scheduled training session")
        
        self._execute_training(trigger_type='scheduled')
    
    def _run_manual_training(self):
        """Internal method for manual training execution."""
        if self.logger:
            self.logger.info("Starting manual training session")
        
        self._execute_training(trigger_type='manual')
    
    def _execute_training(self, trigger_type='scheduled'):
        """
        Execute the training process.
        
        Args:
            trigger_type: 'scheduled' or 'manual'
        """
        self.training_in_progress = True
        start_time = datetime.now()
        
        try:
            # Get current ratings data
            ratings_df = self.data_processor.ratings
            
            if len(ratings_df) < 100:
                error_msg = 'Insufficient data for training (minimum 100 ratings required)'
                if self.logger:
                    self.logger.error(error_msg)
                
                self.last_training_result = {
                    'success': False,
                    'error': error_msg,
                    'trigger_type': trigger_type,
                    'timestamp': start_time.isoformat()
                }
                
                # Log failed training event
                self.history_manager.log_training_event({
                    'trigger_type': trigger_type,
                    'started_at': start_time.isoformat(),
                    'success': False,
                    'error': error_msg
                })
                
                return
            
            # Get before metrics from current model
            before_metrics = self._get_current_model_metrics()
            
            # Retrain all models
            results = self.training_service.retrain_all_models(ratings_df)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract after metrics and model version
            after_metrics = None
            model_version = None
            
            if 'matrix_factorization' in results and 'metrics' in results['matrix_factorization']:
                after_metrics = results['matrix_factorization']['metrics']
                model_version = results['matrix_factorization'].get('version')
            
            self.last_training_result = {
                'success': True,
                'trigger_type': trigger_type,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'duration_seconds': duration,
                'results': results
            }
            
            # Log successful training event with before/after metrics
            event_data = {
                'trigger_type': trigger_type,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'duration_seconds': duration,
                'success': True,
                'model_version': model_version,
                'after_metrics': after_metrics
            }
            
            if before_metrics:
                event_data['before_metrics'] = before_metrics
            
            self.history_manager.log_training_event(event_data)
            
            if self.logger:
                self.logger.info(f"Training completed successfully in {duration:.2f}s")
                self.logger.info(f"Results: {results}")
            
        except Exception as e:
            error_msg = str(e)
            if self.logger:
                self.logger.error(f"Training failed: {error_msg}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.last_training_result = {
                'success': False,
                'error': error_msg,
                'trigger_type': trigger_type,
                'timestamp': start_time.isoformat()
            }
            
            # Log failed training event
            self.history_manager.log_training_event({
                'trigger_type': trigger_type,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'duration_seconds': duration,
                'success': False,
                'error': error_msg
            })
        
        finally:
            self.training_in_progress = False
    
    def _get_current_model_metrics(self):
        """
        Get metrics from the current model.
        
        Returns:
            dict: Current model metrics or None
        """
        try:
            versions = self.model_manager.list_versions('matrix_factorization')
            if versions:
                latest = versions[-1]
                return latest.get('metrics')
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not get current model metrics: {e}")
        
        return None
