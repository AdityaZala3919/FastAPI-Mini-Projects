import time
from celery_app import celery_app


@celery_app.task(bind=True)
def simulate_computation_task(self, duration: int = 60):
    """
    Background task that simulates a long-running computation.
    
    This task sleeps for the specified duration to simulate real work
    like data processing, API calls, or heavy computations.
    
    Args:
        duration: Time in seconds to simulate work (default: 60 seconds)
    
    Returns:
        dict: Status message with completion details
    """
    try:
        # Log task start
        print(f"Task {self.request.id} started. Simulating {duration} seconds of work...")
        
        # Update task state to PROGRESS
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": duration,
                "status": f"Running task for {duration} seconds..."
            }
        )
        
        # Simulate work with periodic updates
        for i in range(duration):
            time.sleep(1)
            # Update progress every 10 seconds
            if (i + 1) % 10 == 0:
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": duration,
                        "status": f"Progress: {i + 1}/{duration} seconds"
                    }
                )
                print(f"Task {self.request.id}: {i + 1}/{duration} seconds completed")
        
        # Return final result
        result = {
            "status": "completed",
            "duration": duration,
            "message": f"Task completed successfully after {duration} seconds",
            "task_id": self.request.id
        }
        
        print(f"Task {self.request.id} completed!")
        return result
        
    except Exception as e:
        # Log error and update state
        print(f"Task {self.request.id} failed with error: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "status": "Task failed"
            }
        )
        raise
