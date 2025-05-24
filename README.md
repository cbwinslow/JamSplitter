# JamSplitter

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI Status](https://github.com/yourusername/jam-splitter/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/jam-splitter/actions)
[![codecov](https://codecov.io/gh/yourusername/jam-splitter/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/jam-splitter)

JamSplitter is a powerful tool for splitting music tracks into individual stems (vocals, drums, bass, etc.) and generating synchronized lyrics. It's designed for music producers, DJs, and audio enthusiasts who want to work with individual components of a song.

## ✨ Features

- **Audio Stem Separation**: Split music into separate stems (vocals, drums, bass, etc.)
- **Lyrics Generation**: Generate synchronized lyrics with timestamps using Whisper
- **GPU Acceleration**: Supports both NVIDIA CUDA and AMD ROCm for faster processing
- **Modern Python**: Built with Python 3.11+ and type hints for better maintainability
- **Containerized**: Easy deployment with Docker and Docker Compose
- **Rich CLI**: Beautiful command-line interface with progress bars and status updates
- **Caching**: Avoid re-processing the same audio files with built-in caching

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- FFmpeg
- (Optional) NVIDIA CUDA or AMD ROCm for GPU acceleration

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jam-splitter.git
   cd jam-splitter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Usage

#### Separate audio stems:
```bash
python -m jamsplitter separate input.mp3 --output-dir output/
```

#### Generate lyrics with timestamps:
```bash
python -m jamsplitter lyrics input.mp3 --output lyrics.json
```

## 🐳 Docker Support

### Build and run with Docker:

```bash
# Build the image
docker build -t jam-splitter .

# Run with GPU support (NVIDIA)
docker run --gpus all -v $(pwd)/input:/input -v $(pwd)/output:/output jam-splitter separate /input/song.mp3 --output-dir /output
```

### GPU-Accelerated Containers

- **NVIDIA CUDA**:
  ```bash
  docker build -f Dockerfile.cuda -t jam-splitter:cuda .
  ```

- **AMD ROCm**:
  ```bash
  docker build -f Dockerfile.rocm -t jam-splitter:rocm .
  ```

### Docker Compose

```bash
docker-compose up --build
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

## 🛠 Development

### Pre-commit Hooks

This project uses pre-commit to enforce code quality. Install the hooks with:

```bash
pre-commit install
```

### Code Style

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **Mypy** for static type checking

Run all code quality checks:
```bash
pre-commit run --all-files
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Demucs](https://github.com/facebookresearch/demucs) for audio source separation
- [Rich](https://github.com/willmcgugan/rich) for beautiful terminal output

## 📚 Documentation

For detailed documentation, please see the [docs](docs/) directory.

## 📬 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/jam-splitter](https://github.com/yourusername/jam-splitter)
