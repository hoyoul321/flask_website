< PROJECT ROOT >
   |-- config/
   |    |-- config.yaml          # Configuration file (MUST be present)
   |    |-- config.yaml.example  # Sample configuration file
   |-- oam_intranet/             # Implements app logic
   |    |-- blueprints/          # Flask Blueprints
   |    |    |-- admin/               # Contains the website administrator's interface - Roles, permissions, etc.
   |    |    |-- api/                 # API Blueprint - handles API requests (no UI)
   |    |    |-- auth/                # Authorization Blueprint - Login, Logout, etc.
   |    |
   |   __init__.py               # Entry point for the module, contains the create_app factory method 
   |
   |-- app.py                    # Entry point for the whole app, calls create_app()
   |
   |-- Pipfile                   # Module requirements
   |-- Pipfile.lock              # Version locked module list
   |   |
   |-- ************************************************************************
