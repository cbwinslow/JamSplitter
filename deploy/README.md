# JamSplitter Deployment Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 16+ (for frontend)
- Go 1.18+ (for optional Go components)
- Rust (for performance-critical components)

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d jam-splitter postgres redis

# View logs
docker-compose logs -f
```

### Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
   # For development
   pip install -r requirements-dev.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   # Start the API
   uvicorn app:app --reload
   
   # Or run the CLI
   python -m jamsplitter.cli --help
   ```

## Configuration

Configuration can be done through:

1. Environment variables (prefixed with `JAMSPLITTER_`)
2. `config.yaml` file
3. Command-line arguments

## Deployment Options

### Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f deploy/kubernetes/

# Monitor deployment
kubectl get pods -n jamsplitter
```

### AWS ECS

```bash
# Deploy using AWS CDK
cd deploy/aws
cdk deploy
```

### Google Cloud Run

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/jamsplitter

# Deploy to Cloud Run
gcloud run deploy jamsplitter --image gcr.io/PROJECT_ID/jamsplitter --platform managed
```

## Monitoring and Logging

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Jaeger**: `http://localhost:16686`

## Troubleshooting

Check logs:
```bash
docker-compose logs -f
```

Run tests:
```bash
pytest tests/
```

## License

MIT
