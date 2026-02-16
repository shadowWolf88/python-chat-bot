# Background AI Training System Setup Guide

## Overview

The Healing Space app now has a **dual AI system**:
- **Production (Live)**: Uses Groq API for immediate responses
- **Background Training**: Trains a local model that learns from ALL app data

Eventually, the local model can replace Groq for unlimited, independent operation.

---

## How It Works

### 1. Data Collection (Already Active)
- ALL patient chats are collected (with GDPR consent)
- Data is anonymized and stored in `ai_training_data.db`
- Includes: messages, mood context, assessment scores

### 2. Background Training (New)
- Trains a local DialoGPT model on collected data
- Runs independently without interrupting live site
- Learns from ALL users' conversations
- Incrementally improves with each training run

### 3. Model Evolution
- **Current**: Groq API handles all responses
- **Future**: Local trained model takes over
- **Benefit**: No API limits, costs, or dependencies

---

## Installation

### 1. Install Training Dependencies

```bash
cd "/home/computer001/Documents/Healing Space UK"
pip install -r requirements-training.txt
```

**What this installs:**
- `transformers` - Hugging Face model library
- `torch` - PyTorch deep learning framework  
- `datasets` - Data processing for training
- `accelerate` - Training optimizations

**Size:** ~2-3 GB download

### 2. (Optional) GPU Acceleration

If you have NVIDIA GPU with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Training is **much faster** with GPU (minutes vs hours).

---

## Usage

### Manual Training

Train on new data anytime:

```bash
python ai_trainer.py
```

**Output:**
- Shows current training status
- Fetches new conversations since last run
- Trains for 3 epochs (~5-20 minutes depending on data)
- Saves model checkpoint
- Displays training metrics

### Automated Training (Recommended)

#### Linux/Mac (cron):

```bash
# Edit crontab
crontab -e

# Add this line (trains daily at 2 AM):
0 2 * * * cd /home/computer001/Documents/python\ chat\ bot && /usr/bin/python3 train_scheduler.py >> logs/training.log 2>&1
```

#### Windows (Task Scheduler):

1. Open Task Scheduler
2. Create Basic Task
3. **Trigger**: Daily at 2:00 AM
4. **Action**: Start a program
   - Program: `python`
   - Arguments: `train_scheduler.py`
  - Start in: `C:\path\to\Healing Space UK`

---

## Monitoring Training

### Check Status via API

```bash
curl http://localhost:5000/api/ai/training-status
```

**Returns:**
```json
{
  "trained": true,
  "total_runs": 5,
  "last_run": "2026-01-18T14:30:00",
  "last_trained_id": 1247,
  "recent_runs": [...]
}
```

### Manual Status Check

```python
from ai_trainer import BackgroundAITrainer

trainer = BackgroundAITrainer()
status = trainer.get_training_status()
print(status)
```

### View Training Metrics

File: `trained_models/training_metrics.json`

Contains:
- Number of training runs
- Samples per run
- Training loss
- Time taken
- Model paths

---

## Switching to Local Model

Once trained and tested, switch from Groq to local model:

### 1. Set Environment Variable

```bash
# .env or Railway environment variables
USE_LOCAL_AI=1
```

### 2. Restart App

```bash
# Local
python api.py

# Railway
git push  # Auto-deploys with new env var
```

### 3. Verify

Check logs for:
```
🤖 Using local AI model
```

Instead of:
```
🌐 Using Groq API
```

---

## Model Details

### Base Model
- **DialoGPT-small** (Microsoft)
- 117M parameters
- Conversational AI pre-trained on Reddit
- Fine-tuned on therapy conversations

### Training Process
1. Fetches new conversations from `ai_training_data.db`
2. Formats as Patient/Therapist dialogues
3. Fine-tunes DialoGPT on therapy-specific responses
4. Saves checkpoint in `trained_models/`
5. Updates metrics

### Storage
- **Model size**: ~500 MB per checkpoint
- **Keeps**: Last 3 checkpoints
- **Location**: `trained_models/checkpoints/`

---

## Performance Comparison

| Metric | Groq API | Local Trained Model |
|--------|----------|---------------------|
| Response Speed | ~2-5s | ~1-3s (CPU), <1s (GPU) |
| API Costs | $$ per request | Free after training |
| Rate Limits | Yes (API limits) | None |
| Offline Mode | ❌ No | ✅ Yes |
| Privacy | Data sent to API | 100% local |
| Customization | Limited | Fully customizable |
| Learning | No | Continuous |

---

## Troubleshooting

### "transformers library not installed"

```bash
pip install transformers torch datasets accelerate
```

### Out of Memory During Training

Reduce batch size in `ai_trainer.py`:
```python
trainer.train_incremental(num_epochs=3, batch_size=2)  # Was 4
```

### Training Takes Too Long

- Use GPU acceleration (see installation above)
- Reduce epochs: `train_background_model(epochs=1)`
- Train on smaller data batches

### Model Gives Poor Responses

- Need more training data (>500 conversations)
- Increase training epochs
- Check if base model loaded correctly

---

## API Endpoints

### Get Training Status
```
GET /api/ai/training-status
```

### Trigger Manual Training (Clinician only)
```
POST /api/ai/trigger-training
Body: {"username": "clinician_username"}
```

---

## File Structure

```
Healing Space UK/
├── ai_trainer.py              # Main training system
├── train_scheduler.py         # Automated training script
├── requirements-training.txt  # ML dependencies
├── trained_models/           # Model checkpoints
│   ├── checkpoints/         # Training snapshots
│   ├── model_YYYYMMDD/      # Saved models
│   └── training_metrics.json # Performance data
└── ai_training_data.db       # Anonymized training data
```

---

## Roadmap

### Phase 1: Data Collection ✅
- Collect conversations with consent
- Anonymize PII
- Store in training database

### Phase 2: Background Training ✅ (CURRENT)
- Train local model periodically
- Monitor performance
- Keep Groq as primary

### Phase 3: Hybrid Mode (Next)
- Use local model for routine chats
- Fall back to Groq for complex cases
- A/B test responses

### Phase 4: Full Independence
- Local model as primary
- Groq removed
- Fully self-sufficient AI

---

## Notes

- **Training does NOT affect live site** - runs separately
- **All data** from ALL users contributes to learning
- **GDPR compliant** - requires user consent
- **Clinicians see everything** - no data hidden
- **Backward compatible** - works without training libs

---

## Questions?

Check logs:
- Training: `logs/training.log`
- App: Railway dashboard or local console

The system is designed to work **passively** - collect data, train periodically, improve over time, eventually replace Groq.
