# Amplify v2 - Fresh Setup Guide

## Pre-requisites
- Docker & Docker Compose
- 4GB+ RAM available
- 10GB+ disk space for models

## Quick Start

### 1. Create Docker Network
```bash
docker network create ai-coding-agent-network
```

### 2. Start All Services
```bash
cd /home/jimmy/Desktop/amplifyv2
docker compose up -d
```

### 3. Wait for Services
```bash
docker compose ps
```

Expected output:
- ✅ postgres - Healthy
- ✅ redis - Healthy  
- ✅ ollama - Healthy
- ✅ backend - Running

### 4. Verify System Health
```bash
curl http://localhost:8000/api/v1/models/health
```

### 5. Pull Models
```bash
docker exec amplifyv2-ollama-1 ollama pull deepseek-r1:8b
docker exec amplifyv2-ollama-1 ollama pull qwen3:8b
docker exec amplifyv2-ollama-1 ollama pull codellama:latest
```

### 6. Access the Application

**Chat Interface:** http://localhost:8000/chat
**API Docs:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

## Features Ready to Use

✅ **User Authentication**
- Sign up at `/signup` or via API
- Login with JWT tokens
- Secure session management

✅ **Chat Interface**
- Real-time messaging
- Model selection dropdown (30+ models)
- Multi-turn conversations
- Message history per session

✅ **30+ Available Models**
- deepseek-r1:8b (tool calling support)
- qwen3 variants
- codellama
- llama variants
- mistral, gemma, granite
- amplify-* custom models
- And more...

## Key Improvements from v1

### Fixed Issues
1. **Async/Sync Mismatch** - Backend now properly uses AsyncClient for Ollama calls
2. **Model Enumeration** - All 30+ available models now display in dropdown
3. **Docker Networking** - Ollama container properly integrated with backend
4. **Connection Reliability** - Docker DNS resolution instead of host.docker.internal

### Architecture Improvements
- Ollama runs in dedicated container with persistent volume
- Proper health checks for all services
- Correct async/await patterns in FastAPI
- Better error handling for model operations

## Development Workflow

### View Logs
```bash
docker compose logs -f backend
docker compose logs -f ollama
docker compose logs -f postgres
```

### Rebuild Backend
```bash
docker compose build backend
docker compose up -d backend
```

### Access PostgreSQL
```bash
docker exec -it amplifyv2-postgres-1 psql -U coding_agent -d coding_agent
```

### Stop All Services
```bash
docker compose down
```

### Full Cleanup (including volumes)
```bash
docker compose down -v
```

## Troubleshooting

### Ollama Health Check Failing
```bash
docker compose logs ollama | tail -50
docker exec amplifyv2-ollama-1 curl -s http://localhost:11434/api/tags
```

### Backend Can't Connect to Ollama
```bash
docker exec amplifyv2-backend-1 curl -s http://ollama:11434/api/tags
```

### Database Connection Issues
```bash
docker compose logs postgres
```

### Models Not Available
```bash
docker exec amplifyv2-ollama-1 ollama list
```

## Environment Configuration

All environment variables are in `docker-compose.yml`:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis cache
- `OLLAMA_BASE_URL` - Ollama service URL (internal Docker DNS)
- `DEFAULT_OLLAMA_MODEL` - Default model for chat
- `JWT_SECRET_KEY` - Change this in production!

## Next Development Priorities

1. Streaming response support for better UX
2. Model download UI
3. Repository indexing and analysis
4. Agent capabilities with tool calling
5. Code execution sandbox
6. Conversation export
7. Advanced model management
8. Rate limiting and quota management

---
Status: Clean rebuild ready for development
Date: November 14, 2025
