"""
Background AI Training System - Learns from all patient interactions

This trains a local model using data from training_data_manager.py
Currently uses Groq for live responses, but this trains a replacement model
that will eventually run independently without API limitations.

Features:
- Incremental training from new data
- Fine-tunes on therapy conversations
- Stores model checkpoints
- Quality metrics tracking
- Can replace Groq when ready
"""

import sqlite3
import json
import os
import time
from datetime import datetime
from training_data_manager import TrainingDataManager, TRAINING_DB_PATH
import numpy as np

# Check for ML libraries with graceful fallback
try:
    from transformers import (
        AutoModelForCausalLM, 
        AutoTokenizer, 
        TrainingArguments, 
        Trainer,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠️  Transformers not installed. Install with: pip install transformers torch datasets")

# Model configuration
MODEL_NAME = "microsoft/DialoGPT-small"  # Lightweight conversational model
MODEL_DIR = "trained_models"
CHECKPOINT_DIR = os.path.join(MODEL_DIR, "checkpoints")
METRICS_FILE = os.path.join(MODEL_DIR, "training_metrics.json")

class BackgroundAITrainer:
    """Trains local AI model from app data without interrupting live service"""
    
    def __init__(self):
        if not HAS_TRANSFORMERS:
            raise RuntimeError(
                "Transformers library required. Install with:\n"
                "pip install transformers torch datasets accelerate"
            )
        
        self.training_db = TRAINING_DB_PATH
        self.model = None
        self.tokenizer = None
        self.last_trained_id = self._get_last_trained_id()
        
        # Create model directory
        os.makedirs(MODEL_DIR, exist_ok=True)
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    
    def _get_last_trained_id(self):
        """Get ID of last message used in training"""
        if os.path.exists(METRICS_FILE):
            try:
                with open(METRICS_FILE, 'r') as f:
                    metrics = json.load(f)
                    return metrics.get('last_trained_id', 0)
            except:
                return 0
        return 0
    
    def _save_metrics(self, metrics):
        """Save training metrics"""
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, 'r') as f:
                existing = json.load(f)
        else:
            existing = {'training_runs': []}
        
        existing['training_runs'].append(metrics)
        existing['last_trained_id'] = metrics['last_trained_id']
        existing['last_run'] = metrics['timestamp']
        existing['total_runs'] = len(existing['training_runs'])
        
        with open(METRICS_FILE, 'w') as f:
            json.dump(existing, f, indent=2)
    
    def load_or_initialize_model(self):
        """Load existing checkpoint or initialize new model"""
        print("🤖 Loading AI model...")
        
        # Check for latest checkpoint
        checkpoints = [d for d in os.listdir(CHECKPOINT_DIR) if d.startswith('checkpoint-')]
        
        if checkpoints:
            # Load latest checkpoint
            latest = max(checkpoints, key=lambda x: int(x.split('-')[1]))
            checkpoint_path = os.path.join(CHECKPOINT_DIR, latest)
            print(f"📂 Loading checkpoint: {latest}")
            
            self.model = AutoModelForCausalLM.from_pretrained(checkpoint_path)
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
        else:
            # Initialize from base model
            print(f"🆕 Initializing from base model: {MODEL_NAME}")
            self.model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        
        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("✅ Model loaded successfully")
    
    def fetch_new_training_data(self, limit=1000):
        """Fetch new conversations since last training"""
        print(f"📊 Fetching training data (ID > {self.last_trained_id})...")
        
        conn = sqlite3.connect(self.training_db)
        cur = conn.cursor()
        
        # Get new conversations
        conversations = cur.execute(
            """SELECT id, session_hash, message_role, message_content, mood_context
               FROM training_chats
               WHERE id > ?
               ORDER BY id ASC
               LIMIT ?""",
            (self.last_trained_id, limit)
        ).fetchall()
        
        conn.close()
        
        if not conversations:
            print("ℹ️  No new training data available")
            return None
        
        # Group by session
        sessions = {}
        max_id = 0
        
        for conv_id, session_hash, role, content, mood in conversations:
            if session_hash not in sessions:
                sessions[session_hash] = []
            sessions[session_hash].append({
                'role': role,
                'content': content,
                'mood': mood
            })
            max_id = max(max_id, conv_id)
        
        print(f"✅ Fetched {len(conversations)} messages from {len(sessions)} sessions")
        return sessions, max_id
    
    def prepare_training_dataset(self, sessions):
        """Convert conversations to training format"""
        print("🔄 Preparing training dataset...")
        
        training_texts = []
        
        for session_hash, messages in sessions.items():
            # Build conversation context
            conversation = []
            
            for msg in messages:
                if msg['role'] == 'user':
                    conversation.append(f"Patient: {msg['content']}")
                elif msg['role'] == 'ai':
                    conversation.append(f"Therapist: {msg['content']}")
            
            # Create training samples (therapist responses in context)
            for i in range(1, len(conversation)):
                context = " ".join(conversation[:i])
                response = conversation[i]
                
                if response.startswith("Therapist:"):
                    # Format: [Context] <|endoftext|> [Response]
                    training_text = f"{context}{self.tokenizer.eos_token}{response}"
                    training_texts.append(training_text)
        
        print(f"✅ Created {len(training_texts)} training samples")
        
        # Tokenize
        tokenized = self.tokenizer(
            training_texts,
            truncation=True,
            max_length=512,
            padding='max_length',
            return_tensors='pt'
        )
        
        # Create dataset
        dataset = Dataset.from_dict({
            'input_ids': tokenized['input_ids'],
            'attention_mask': tokenized['attention_mask']
        })
        
        return dataset
    
    def train_incremental(self, num_epochs=3, batch_size=4):
        """Train model on new data"""
        print(f"\n🎓 Starting incremental training...")
        print(f"   Epochs: {num_epochs}, Batch size: {batch_size}")
        
        # Fetch new data
        result = self.fetch_new_training_data()
        if result is None:
            return False
        
        sessions, max_id = result
        
        # Load model if not loaded
        if self.model is None:
            self.load_or_initialize_model()
        
        # Prepare dataset
        dataset = self.prepare_training_dataset(sessions)
        
        if len(dataset) == 0:
            print("⚠️  No valid training samples")
            return False
        
        # Training configuration
        training_args = TrainingArguments(
            output_dir=CHECKPOINT_DIR,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=500,
            save_total_limit=3,
            logging_steps=50,
            learning_rate=5e-5,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=os.path.join(MODEL_DIR, 'logs'),
            report_to='none',  # Disable external reporting
            no_cuda=not torch.cuda.is_available()
        )
        
        # Data collator for language modeling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator
        )
        
        # Train
        print("🏋️  Training in progress...")
        start_time = time.time()
        
        train_result = trainer.train()
        
        training_time = time.time() - start_time
        
        # Save final model
        final_path = os.path.join(MODEL_DIR, f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        trainer.save_model(final_path)
        self.tokenizer.save_pretrained(final_path)
        
        print(f"✅ Training complete! ({training_time:.1f}s)")
        print(f"💾 Model saved to: {final_path}")
        
        # Save metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'last_trained_id': max_id,
            'num_samples': len(dataset),
            'num_sessions': len(sessions),
            'training_time_seconds': training_time,
            'train_loss': train_result.training_loss,
            'model_path': final_path
        }
        
        self._save_metrics(metrics)
        self.last_trained_id = max_id
        
        print(f"\n📈 Metrics:")
        print(f"   Loss: {train_result.training_loss:.4f}")
        print(f"   Samples: {len(dataset)}")
        print(f"   Sessions: {len(sessions)}")
        
        return True
    
    def generate_response(self, user_message, conversation_history=None, max_length=150):
        """Generate response using trained model"""
        if self.model is None:
            self.load_or_initialize_model()
        
        # Build context
        context_parts = []
        if conversation_history:
            for msg in conversation_history[-3:]:  # Last 3 exchanges
                sender, text = msg
                if sender == 'user':
                    context_parts.append(f"Patient: {text}")
                else:
                    context_parts.append(f"Therapist: {text}")
        
        context_parts.append(f"Patient: {user_message}")
        context_parts.append("Therapist:")
        
        context = " ".join(context_parts)
        
        # Generate
        inputs = self.tokenizer(context, return_tensors='pt')
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract therapist response
        if "Therapist:" in response:
            response = response.split("Therapist:")[-1].strip()
        
        return response
    
    def get_training_status(self):
        """Get current training status and metrics"""
        if not os.path.exists(METRICS_FILE):
            return {
                'trained': False,
                'message': 'No training runs yet'
            }
        
        with open(METRICS_FILE, 'r') as f:
            metrics = json.load(f)
        
        return {
            'trained': True,
            'total_runs': metrics.get('total_runs', 0),
            'last_run': metrics.get('last_run'),
            'last_trained_id': metrics.get('last_trained_id', 0),
            'recent_runs': metrics.get('training_runs', [])[-5:]  # Last 5 runs
        }


def train_background_model(epochs=3):
    """
    Main function to train model in background
    Call this from a scheduled task or cron job
    """
    if not HAS_TRANSFORMERS:
        print("⚠️  Cannot train: transformers library not installed")
        print("Install with: pip install transformers torch datasets accelerate")
        return False
    
    try:
        trainer = BackgroundAITrainer()
        success = trainer.train_incremental(num_epochs=epochs)
        return success
    except Exception as e:
        print(f"❌ Training error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Healing Space UK - Background AI Training System")
    print("=" * 60)
    
    if not HAS_TRANSFORMERS:
        print("\n❌ Required libraries not installed")
        print("\nInstall with:")
        print("pip install transformers torch datasets accelerate")
        exit(1)
    
    trainer = BackgroundAITrainer()
    
    # Show status
    status = trainer.get_training_status()
    print(f"\n📊 Training Status:")
    if status['trained']:
        print(f"   Total runs: {status['total_runs']}")
        print(f"   Last run: {status['last_run']}")
        print(f"   Last trained ID: {status['last_trained_id']}")
    else:
        print(f"   {status['message']}")
    
    # Run training
    print("\n" + "=" * 60)
    success = trainer.train_incremental(num_epochs=3, batch_size=4)
    
    if success:
        print("\n🎉 Training completed successfully!")
    else:
        print("\n⚠️  No new data to train on")
    
    print("=" * 60)
