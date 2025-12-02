import os
import json
from datetime import datetime
from ml.ml_logger import get_ml_logger

logger = get_ml_logger('training_history')

class TrainingHistoryManager:
    """
    Manages training history and completion notifications.
    Logs training events and stores before/after metrics.
    """
    def __init__(self, history_dir='backend/models/training_history'):
        self.history_dir = history_dir
        os.makedirs(history_dir, exist_ok=True)
        self.history_file = os.path.join(history_dir, 'training_history.json')
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure the history file exists."""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def log_training_event(self, event_data):
        """
        Log a training event with before/after metrics.
        
        Args:
            event_data: dict containing:
                - trigger_type: 'scheduled' or 'manual'
                - started_at: ISO timestamp
                - completed_at: ISO timestamp (if successful)
                - duration_seconds: training duration
                - success: boolean
                - before_metrics: dict of metrics before training (optional)
                - after_metrics: dict of metrics after training
                - model_version: version of trained model
                - error: error message (if failed)
        
        Returns:
            dict: The logged event with ID
        """
        # Load existing history
        history = self._load_history()
        
        # Add event ID and timestamp
        event_data['event_id'] = len(history) + 1
        event_data['logged_at'] = datetime.now().isoformat()
        
        # Append to history
        history.append(event_data)
        
        # Save updated history
        self._save_history(history)
        
        # Log the event
        if event_data.get('success'):
            logger.info(f"Training event logged: {event_data['trigger_type']} - "
                       f"Version {event_data.get('model_version')} - "
                       f"Duration {event_data.get('duration_seconds', 0):.2f}s")
            
            # Log metrics comparison if available
            if 'before_metrics' in event_data and 'after_metrics' in event_data:
                self._log_metrics_comparison(event_data['before_metrics'], 
                                            event_data['after_metrics'])
        else:
            logger.error(f"Training event failed: {event_data.get('error', 'Unknown error')}")
        
        return event_data
    
    def _log_metrics_comparison(self, before_metrics, after_metrics):
        """Log comparison of before/after metrics."""
        if not before_metrics or not after_metrics:
            return
        
        logger.info("=== Training Metrics Comparison ===")
        
        for metric_name in after_metrics.keys():
            if metric_name in before_metrics:
                before_val = before_metrics[metric_name]
                after_val = after_metrics[metric_name]
                
                # Calculate improvement
                if metric_name == 'rmse':
                    # Lower is better for RMSE
                    improvement = before_val - after_val
                    improvement_pct = (improvement / before_val) * 100 if before_val > 0 else 0
                    direction = "↓" if improvement > 0 else "↑"
                else:
                    # Higher is better for precision, recall, coverage
                    improvement = after_val - before_val
                    improvement_pct = (improvement / before_val) * 100 if before_val > 0 else 0
                    direction = "↑" if improvement > 0 else "↓"
                
                logger.info(f"{metric_name}: {before_val:.4f} → {after_val:.4f} "
                          f"({direction} {abs(improvement_pct):.2f}%)")
    
    def get_training_history(self, limit=None):
        """
        Get training history.
        
        Args:
            limit: Maximum number of events to return (most recent first)
        
        Returns:
            list: Training events
        """
        history = self._load_history()
        
        # Sort by logged_at descending (most recent first)
        history.sort(key=lambda x: x.get('logged_at', ''), reverse=True)
        
        if limit:
            return history[:limit]
        
        return history
    
    def get_latest_training_event(self):
        """
        Get the most recent training event.
        
        Returns:
            dict: Latest training event or None
        """
        history = self.get_training_history(limit=1)
        return history[0] if history else None
    
    def get_training_statistics(self):
        """
        Get statistics about training history.
        
        Returns:
            dict: Training statistics
        """
        history = self._load_history()
        
        if not history:
            return {
                'total_trainings': 0,
                'successful_trainings': 0,
                'failed_trainings': 0,
                'avg_duration_seconds': 0,
                'last_training': None
            }
        
        successful = [e for e in history if e.get('success')]
        failed = [e for e in history if not e.get('success')]
        
        durations = [e.get('duration_seconds', 0) for e in successful]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Get latest event
        latest = max(history, key=lambda x: x.get('logged_at', ''))
        
        return {
            'total_trainings': len(history),
            'successful_trainings': len(successful),
            'failed_trainings': len(failed),
            'avg_duration_seconds': avg_duration,
            'last_training': latest
        }
    
    def _load_history(self):
        """Load training history from file."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading training history: {e}")
            return []
    
    def _save_history(self, history):
        """Save training history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving training history: {e}")
