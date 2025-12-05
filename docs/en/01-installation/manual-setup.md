# Manual Installation

Follow these steps to install and run TestGyver directly on your machine.

## 1. Clone the Repository

```bash
git clone <repository-url>
cd app_test
```

## 2. Set Up Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configuration

1.  Copy the example configuration (if available) or create `configuration.json` in the root directory.
2.  See [Configuration Guide](configuration.md) for details on the settings.

## 5. Initialize Database (Optional)

You can pre-populate the database with initial data and indexes.

```bash
python init/init_database.py
```

To create an admin user:
```bash
python init/create_user.py
```

## 6. Run the Application

```bash
# Set environment variables
export FLASK_APP=app
export FLASK_ENV=development  # Use 'production' for deployment

# Run Flask
flask run --host=0.0.0.0 --port=5000
```

Access the application at `http://localhost:5000`.
