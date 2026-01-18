"""
Railway-specific training configuration
This runs on the Railway server where ALL users' data is collected
"""

import os

# Training configuration for Railway deployment
RAILWAY_CONFIG = {
    # Train automatically after N new conversations
    'auto_train_threshold': 100,  # Train after 100 new messages
    
    # Training schedule (if using Railway cron)
    'training_schedule': 'daily',  # or 'weekly', 'manual'
    
    # Model storage
    'model_storage': '/app/trained_models',  # Railway persistent storage
    
    # Training resources
    'batch_size': 2,  # Small for Railway's CPU limits
    'epochs': 2,      # Quick training runs
    'max_length': 256, # Shorter for faster training
    
    # Enable background training
    'enable_auto_training': True
}

# Check if we're on Railway
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None

def get_training_config():
    """Get appropriate config based on environment"""
    if IS_RAILWAY:
        return RAILWAY_CONFIG
    else:
        # Local development - smaller settings
        return {
            'auto_train_threshold': 50,
            'training_schedule': 'manual',
            'model_storage': 'trained_models',
            'batch_size': 4,
            'epochs': 3,
            'max_length': 512,
            'enable_auto_training': False
        }
