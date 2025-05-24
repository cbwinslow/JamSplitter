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
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package in development mode with all dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

### Usage

#### Separate audio stems

```bash
python -m jamsplitter separate input.mp3 --output-dir output/
```

#### Generate lyrics with timestamps

```bash
python -m jamsplitter lyrics input.mp3 --output lyrics.json
```

## 🚀 Deployment

### Deployment Prerequisites

- Docker and Docker Compose
- Python 3.11+
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate permissions (for AWS deployment)
- [Terraform](https://www.terraform.io/) (for AWS deployment)

### Local Deployment with Docker Compose

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/jam-splitter.git
   cd jam-splitter
   ```

2. Copy the example environment file and update with your configuration:

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. Start the services:

   #### CPU-only mode

   ```bash
   docker-compose up -d
   ```

   #### NVIDIA GPU support

   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
   ```

   #### AMD GPU support

   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.rocm.yml up -d
   ```

4. Access the application:
   - Web UI: <http://localhost:8080>
   - API Docs: <http://localhost:8000/docs>

### AWS Deployment with Terraform

1. Ensure you have AWS CLI configured with appropriate permissions

2. Navigate to the deployment directory:

   ```bash
   cd deploy/aws
   ```

3. Initialize Terraform:

   ```bash
   terraform init
   ```

4. Review the planned changes:

   ```bash
   terraform plan
   ```

5. Apply the configuration:

   ```bash
   terraform apply
   ```

6. After deployment, you'll receive the load balancer URL and other outputs

### Environment Variables

Create a `.env` file with the following variables (or set them in your deployment environment)

```bash
# OpenAI API Key (required for lyrics generation)
OPENAI_API_KEY=your_openai_api_key_here

# Spotify API Configuration (required for Spotify integration)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://your-domain.com/callback

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=jamsplitter
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Application Settings
OUTPUT_DIR=/output_stems
LOG_LEVEL=INFO
GPU_DEVICE=cpu  # or 'cuda' for NVIDIA, 'rocm' for AMD
```

## 🐳 Docker Containers

### Available Services

- `jam-splitter`: Main application service
- `postgres`: PostgreSQL database
- `redis`: Redis cache and task queue
- `traefik`: Reverse proxy with automatic HTTPS (in production setup)

### Building Custom Images

```bash
# CPU version
DOCKER_BUILDKIT=1 docker build -t jam-splitter:latest .
```

```bash
# NVIDIA GPU version
DOCKER_BUILDKIT=1 docker build -f Dockerfile.cuda -t jam-splitter:cuda .
```

```bash
# AMD GPU version
DOCKER_BUILDKIT=1 docker build -f Dockerfile.rocm -t jam-splitter:rocm .
```

## 📊 Monitoring

- **Prometheus Metrics**: Available at `/metrics` endpoint
- **Grafana Dashboards**: Pre-configured dashboards in `deploy/grafana`
- **Logs**: Centralized logging with Loki and Promtail in production setup

## 🔄 Upgrading

1. Pull the latest changes:

   ```bash
   git pull origin main
   ```

2. Rebuild and restart containers:

   ```bash
   docker-compose down
   docker-compose pull
   docker-compose up -d --build
   ```

3. Run database migrations (if any):

   ```bash
   docker-compose exec jam-splitter alembic upgrade head
   ```

## 🛠 Troubleshooting

### Common Issues

1. **GPU not detected in Docker**
   - Ensure NVIDIA Container Toolkit is installed
   - Run `nvidia-smi` to verify GPU detection
   - Use `--gpus all` flag when running containers

2. **Port conflicts**
   - Check for other services using ports 8000, 8080, 5432, or 6379
   - Update `docker-compose.yml` to use different ports if needed

3. **Missing environment variables**
   - Ensure all required variables are set in `.env`
   - Restart containers after making changes

### Getting Help

- Check the logs: `docker-compose logs -f`
- Open an issue on GitHub
- Join our Discord community (link in project description)

## 🐳 Docker Support

### Build and run with Docker

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
# Run tests
pytest tests/

# Run with coverage
pytest --cov=jamsplitter tests/
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

Project Link: [GitHub Repository](https://github.com/yourusername/jam-splitter)
