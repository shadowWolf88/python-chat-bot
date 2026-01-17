# Desktop Application Files (Not Needed for Railway)

This folder contains the **desktop version** of Healing Space, built with Python Tkinter.

## Files in This Folder

- **main.py** - Desktop GUI application (Tkinter/CustomTkinter)
- **pet_game.py** - Pet companion game (desktop UI)
- **clinician_appointments.py** - Appointment calendar system (desktop)

**Note**: `training_data_manager.py` is in the root folder because it's used by both desktop and web versions.

## Important Notes

### For Railway Deployment

**These files are NOT needed for Railway deployment!**

Railway runs the **web application** which uses:
- `api.py` - Flask REST API (web server)
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies

### For Desktop Users

To run the desktop application locally:

```bash
# Install desktop dependencies
pip install customtkinter reportlab cryptography bcrypt argon2-cffi

# Run desktop app
python3 legacy_desktop/main.py
```

### Why Separate?

The desktop files use **tkinter** which:
1. Is NOT available on Railway or most cloud platforms
2. Requires GUI display (X11/Wayland) 
3. Cannot run in web containers

Keeping them separate prevents:
- Import errors on Railway (`No module named '_tkinter'`)
- Confusion about which files are needed for web deployment
- Accidental deployment of desktop code to cloud

### Desktop Features

The desktop app includes:
- Full Tkinter GUI with tabbed interface
- Local SQLite database
- PDF generation for reports
- Appointment calendar
- Pet game with animations
- AI training data collection

All these features are **also available in the web version** via `api.py` and the web interface.

## Repository Structure

```
/
├── api.py                    # WEB: Flask API (needed for Railway)
├── templates/                # WEB: HTML interface (needed for Railway)
├── requirements.txt          # WEB: Dependencies (needed for Railway)
├── railway.toml              # WEB: Railway config (needed for Railway)
├── secrets_manager.py        # SHARED: Both desktop and web use this
├── audit.py                  # SHARED: Both desktop and web use this
├── fhir_export.py            # SHARED: Both desktop and web use this
├── secure_transfer.py        # SHARED: Both desktop and web use this
└── legacy_desktop/           # DESKTOP ONLY: Not needed for Railway
    ├── main.py               # Desktop GUI
    ├── pet_game.py           # Desktop game
    ├── clinician_appointments.py
    └── training_data_manager.py
```

## For Developers

When adding features:
- **Web features**: Edit `api.py` and `templates/index.html`
- **Desktop features**: Edit files in `legacy_desktop/`
- **Shared functionality**: Edit the shared modules (secrets_manager.py, audit.py, etc.)

The web and desktop apps share the same database schema, so features can be implemented in both versions.
