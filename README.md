# TestGyver

![Docker Pulls](https://img.shields.io/docker/pulls/gluk46546546/testgyver)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-gluk46546546/testgyver-blue?logo=docker)](https://hub.docker.com/r/gluk46546546/testgyver)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**TestGyver** is a multi-environment testing application designed to orchestrate and document functional or technical test campaigns. Inspired by the ingenious spirit of MacGyver, the platform combines flexibility, extensibility (action plugins), and visibility (detailed reports) within a web interface built with Flask and MongoDB.

## 📚 Documentation

The complete documentation is available in the `docs/` folder.

![Démo TestGyver](raw/main/docs/assets/testgyver-intro.gif)

### 🌍 Choose your language

*   [English (Source)](docs/en/index.md)
*   [Français](docs/fr/index.md)
*   [Español](docs/es/index.md)
*   [Deutsch](docs/de/index.md)
*   [Italiano](docs/it/index.md)
*   [Japanese](docs/ja/index.md)
*   [中文](docs/zh/index.md)

## 🚀 Quick Start

### Prerequisites

*   Python 3.11+
*   MongoDB 6.x
*   Docker (optional, for containerized deployment)

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd app_test
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # .venv\Scripts\activate   # Windows
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure the application:
    Copy `configuration.json.example` to `configuration.json` and adjust the settings (MongoDB connection, etc.).

5.  Run the application:
    ```bash
    flask run
    ```

## 🐳 Docker (official image)

Image: `gluk46546546/testgyver:0.0.2`

- Pull the image:
    ```bash
    docker pull gluk46546546/testgyver:0.0.2
    ```
- Run exposing port 5000:
    ```bash
    docker run --rm -p 5000:5000 gluk46546546/testgyver:0.0.2
    ```
- Configure MongoDB using environment variables (example):
    ```bash
    docker run --rm -p 5000:5000 \
        -e MONGO_HOST=host.docker.internal \
        -e MONGO_PORT=27017 \
        -e MONGO_DB=testgyver \
        gluk46546546/testgyver:0.0.2
    ```


## 🧩 Key Features

*   **Campaign Management**: Create, organize, and execute test campaigns.
*   **Plugin System**: Extend functionality with custom action plugins (HTTP, SSH, FTP, etc.).
*   **Real-time Reporting**: Monitor test execution via WebSockets.
*   **Multi-environment**: Manage variables across different environments.

## 🤝 Contributing

Contributions are welcome!
If you want to help, check out the issues tagged with **"good first issue"**:

[![Good First Issues](https://img.shields.io/github/issues/gLUK00/app_test/good%20first%20issue?color=green&label=Good%20First%20Issues)](https://github.com/gLUK00/app_test/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

Please see our [Developer Guide](docs/en/03-developer-guide/index.md) for more details.

## 📄 License

This project is licensed under the MIT License.

