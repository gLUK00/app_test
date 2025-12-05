# Configuration

The application is configured via a `configuration.json` file located in the root directory.

## Structure

```json
{
    "mongo": {
        "user": "root",
        "pass": "mypass",
        "host": "localhost",
        "port": "27017",
        "bdd": "testGyver",
        "prefix": "mgv_",
        "soft_delete": true
    },
    "jwt_secret": "your-secret-key",
    "app": {
        "debug": true,
        "port": 5000,
        "host": "0.0.0.0"
    },
    "pagination": {
        "page_size": 20,
        "max_page_size": 100
    },
    "security": {
        "token_expiration_minutes": 60,
        "password_min_length": 8
    },
    "workdir": "./workdir",
    "version": "1.0.0"
}
```

## Parameters Detail

### Mongo
*   **user**: MongoDB username.
*   **pass**: MongoDB password.
*   **host**: Database host address (e.g., `localhost` or `mongo` in Docker).
*   **port**: Database port (default: `27017`).
*   **bdd**: Name of the database to use.
*   **prefix**: Prefix for collection names (e.g., `mgv_` results in `mgv_users`).
*   **soft_delete**: If true, items are marked as deleted instead of being removed.

### Security
*   **jwt_secret**: A long, random string used to sign JWT tokens. **Change this in production!**
*   **token_expiration_minutes**: Session duration in minutes.
*   **password_min_length**: Minimum characters for user passwords.

### App
*   **debug**: Enable Flask debug mode (auto-reload). Set to `false` in production.
*   **port**: Port the application listens on.
*   **host**: Interface to bind to (`0.0.0.0` for all interfaces).

### Workdir
*   **workdir**: Path to the directory where campaign files and temporary data are stored.
