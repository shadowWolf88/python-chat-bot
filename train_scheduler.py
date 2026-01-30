#!/usr/bin/env python3
"""
Training Scheduler - Runs background AI training periodically

This script should be run via cron job or scheduled task.
It trains the local AI model on new data without interrupting the live site.

Example cron job (train daily at 2 AM):
0 2 * * * /usr/bin/python3 /path/to/train_scheduler.py >> /path/to/train.log 2>&1

Example Windows Task Scheduler:
- Trigger: Daily at 2:00 AM
- Action: Start program
  - Program: python
  - Arguments: train_scheduler.py
    - Start in: C:\path\to\Healing Space UK
"""

import os
import sys
from datetime import datetime
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print(f"\n{'='*70}")
    print(f"🤖 Healing Space UK AI Training Scheduler")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    try:
        from ai_trainer import train_background_model, BackgroundAITrainer
        
        # Check if training data is available
        trainer = BackgroundAITrainer()
        status = trainer.get_training_status()
        
        print(f"📊 Current Status:")
        if status['trained']:
            print(f"   ✅ Previous training runs: {status['total_runs']}")
            print(f"   📅 Last run: {status['last_run']}")
            print(f"   📝 Last trained message ID: {status['last_trained_id']}")
        else:
            print(f"   ℹ️  {status['message']}")
        
        print(f"\n{'='*70}")
        print(f"🚀 Starting training...")
        print(f"{'='*70}\n")
        
        # Train with 3 epochs (adjust as needed)
        success = train_background_model(epochs=3)
        
        print(f"\n{'='*70}")
        if success:
            print(f"✅ Training completed successfully!")
            
            # Show updated status
            new_status = trainer.get_training_status()
            if new_status['trained'] and new_status['recent_runs']:
                latest = new_status['recent_runs'][-1]
                print(f"\n📈 Latest Run Statistics:")
                print(f"   📊 Samples trained: {latest.get('num_samples', 'N/A')}")
                print(f"   💬 Sessions processed: {latest.get('num_sessions', 'N/A')}")
                print(f"   ⏱️  Training time: {latest.get('training_time_seconds', 0):.1f}s")
                print(f"   📉 Final loss: {latest.get('train_loss', 'N/A')}")
        else:
            print(f"ℹ️  No new training data available")
            print(f"💡 Training will run next time there's new data")
        
        print(f"{'='*70}")
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        return 0 if success else 1
        
    except ImportError as e:
        print(f"\n❌ Error: Required libraries not installed")
        print(f"📦 Install with: pip install -r requirements-training.txt")
        print(f"   Details: {e}\n")
        return 2
    
    except Exception as e:
        print(f"\n❌ Training failed with error:")
        print(f"   {e}\n")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
