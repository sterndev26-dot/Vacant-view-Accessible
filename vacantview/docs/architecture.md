vacantview-app/
│
├── .env                          # Environment configuration (should be listed in .gitignore)
├── .gitignore                    # Excludes .env, __pycache__/, *.pyc, *.db, etc.
├── README.md                     # Main documentation: setup, usage, and architecture
├── requirements.txt              # List of pip dependencies
├── setup.py                      # Optional: allows the app to be installed as a Python package
├── run.py                        # Explicit entry point to launch the application
│
├── vacantview/                   # Main application package
│   ├── __init__.py
│   ├── main.py                   # App initialization and startup logic
│
│   ├── config/                   # App configuration and environment variables
│   │   └── config.py
│
│   ├── ui/                       # All GUI logic and interface components
│   │   ├── __init__.py
│   │   ├── gui_app.py
│   │   ├── gui_elements.py
│   │   ├── image_loader.py
│   │   └── context_menu/
│   │       ├── __init__.py
│   │       ├── context_menu.py           # GUI menu construction
│   │       └── functions                 # Separated menu action logic
│
│   ├── platform/                 # Hardware interaction (e.g. GPIO, sensors, Raspberry Pi specifics)
│   │   ├── __init__.py
│   │   ├── gpio_control.py
│   │   └── sensor_read.py
│
│   ├── core/                     # Core logic, application state, and shared utilities
│   │   ├── __init__.py
│   │   ├── state.py              # Shared Tkinter state or context variables
│   │   ├── logger.py             # Centralized system logger
│   │   └── helpers.py            # General-purpose helper functions
│
│   ├── data/                     # Data access and database-related code
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── app_data.db           # SQLite database (should be gitignored)
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── auth_service.py
│   │   └── models/
│   │       ├── __init__.py
│   │       └── organization.py
│
│   ├── admin/                    # Admin tools and utilities
│   │   ├── __init__.py
│   │   ├── pin_entry.py
│   │   ├── admin_auth.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── user_editor.py
│   │       ├── data_service.py
│   │       └── usb_file_loader.py
│
├── assets/                       # Static resources used in the UI
│   └── images/
│       ├── BOTH.jpg
│       ├── MEN.jpg
│       └── WOMEN.jpg
│
├── tests/                        # Integration tests
│   ├── __init__.py
│   ├── test_ports.py
│   ├── check_gpio_status.py
│   └── test_auth.py
│
├── docs/                         # Developer and system documentation
│   ├── architecture.md
│   └── setup.md
