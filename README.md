# Amplify - AI Code Amplification Engine

An AI-powered code analysis and generation platform that runs entirely on local infrastructure using Docker and Ollama LLMs.

## Features

- **Web UI Chat Interface** - Full-featured chat UI with model selection and real-time responses
- **User Authentication** - Registration and login with JWT token security
- **Session Management** - Persistent chat history with automatic session tracking
- **Local LLM Integration** - Use 20+ models (codellama, llama3, deepseek-coder, granite, qwen, gemma, etc.)
- **Multi-turn Conversations** - Maintain context across multiple messages
- **Repository Analysis** - Index and search code repositories
- **Code Generation** - AI-powered code completion and generation
- **Message History** - Track all interactions and generated code
- **Full REST API** - Comprehensive endpoints for all operations

## Quick Start - One-Click Installation ⚡

### The Easiest Way (Recommended for non-technical users)

**Linux/macOS:**
```bash
./install.sh
```

**Windows:**
Double-click `install.bat` (run as Administrator)

This will automatically:
- ✅ Check for Docker
- ✅ Build and start all containers
- ✅ Wait for services to initialize
- ✅ Download a default LLM model
- ✅ Open the Web UI

See [QUICKSTART.md](QUICKSTART.md) for more details.

---

### Manual Installation

If you prefer to set up manually or the installer doesn't work:

#### Prerequisites

- Docker & Docker Compose
- 4GB+ RAM available for LLM models
- 10GB+ disk space for model storage

#### Steps

1. **Navigate to the project:**
```bash
cd amplify
```

2. **Start all services:**
```bash
docker compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Ollama (port 11436 external, 11434 internal)
- FastAPI Backend (port 8000)

3. **Verify the system is healthy:**
```bash
curl http://localhost:8000/api/v1/models/health
```

Expected response:
```json
{"status":"healthy","ollama_url":"http://ollama:11434","available_models":0,"models":[]}
```

4. **Pull an LLM model:**
```bash
docker exec selfclone-ollama-1 ollama pull codellama:latest
```

Available models: codellama, llama3, llama2, deepseek-coder, granite, qwen, gemma, and more

5. **Access the Web UI:**
- **Chat Interface**: http://localhost:8000/chat
- **Sign Up / Login**: Buttons in the top right corner
- Create an account or log in to start chatting

6. **Access the API:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000/api/v1

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Docker Compose (ai-coding-agent-network)      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  FastAPI     │  │PostgreSQL│  │  Redis Cache    │ │
│  │  Backend     │  │  Database│  │                 │ │
│  │ (port 8000)  │  │(port5432)│  │  (port 6379)    │ │
│  └──────────────┘  └──────────┘  └──────────────────┘ │
│         │                                              │
│         └──────────────────────────┬──────────────────┘ │
│                                    │                   │
│  ┌────────────────────────────────────────────────────┐│
│  │         Ollama LLM Service                        ││
│  │    (port 11436 external, 11434 internal)         ││
│  │  - codellama, llama3, deepseek-coder, etc.       ││
│  └────────────────────────────────────────────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Core Database Models

- **Repositories** - Code repositories with metadata
- **Sessions** - User sessions and conversation context
- **Messages** - Chat messages and interactions
- **CodeBlocks** - Generated or analyzed code snippets
- **Users** - User accounts and authentication
- **Agents** - AI agent configurations

## Environment Variables

```
DATABASE_URL=postgresql://coding_agent:coding_agent_password@postgres:5432/coding_agent
REDIS_URL=redis://redis:6379
JWT_SECRET_KEY=dev-secret-key-change-in-production
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_OLLAMA_MODEL=codellama:latest
DEBUG=true
LOG_LEVEL=INFO
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Login and receive JWT token

### Health & Status
- `GET /api/v1/models/health` - System health check

### Models
- `GET /api/v1/models/available` - List available LLM models
- `GET /api/v1/models/list` - List available LLM models
- `POST /api/v1/models/generate` - Generate code using AI

### Chat & Sessions
- `GET /api/v1/chat/sessions/` - Get user's chat sessions
- `POST /api/v1/chat/sessions/` - Create new chat session
- `POST /api/v1/chat/message` - Send message in session

### Repositories
- `POST /api/v1/repositories/search` - Search repositories
- `GET /api/v1/repositories/{id}` - Get repository details

### Sessions
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{id}` - Get session

### Messages
- `POST /api/v1/messages` - Send message in session
- `GET /api/v1/sessions/{id}/messages` - Get session messages

## Development

### File Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile          # Container image
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── routes/             # API endpoints
│   ├── utils/              # Helper utilities
│   └── services/           # Business logic
├── docker-compose.yml      # Container orchestration
└── README.md              # This file
```

### Running in Development

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f backend

# Stop services
docker compose down
```

### Hot Reload

The backend runs with `--reload` flag enabled, so code changes automatically restart the server.

## Troubleshooting

### Ollama Connection Refused

If you see "Ollama service is not available", check:
1. Ollama container is running: `docker compose ps`
2. Models are loaded: `curl http://localhost:11436/api/tags`
3. Docker network connectivity: `docker network inspect ai-coding-agent-network`

### Models Not Available

Pull models into Ollama:
```bash
docker exec selfclone-ollama-1 ollama pull codellama:latest
docker exec selfclone-ollama-1 ollama pull llama3:latest
```

### Database Issues

Reset the database:
```bash
docker compose down -v  # Remove volumes
docker compose up -d    # Recreate with fresh DB
```

## Performance Notes

- First model inference may be slow as Ollama loads the model
- Larger models (8B+) require significant RAM
- Redis caching significantly improves response times for repeated queries
- Consider model quantization (Q4_K_M) for faster inference on limited hardware

## Security Considerations

- Change `JWT_SECRET_KEY` in production
- Enable HTTPS/TLS for production deployments
- Restrict API access with firewall rules
- Use strong database credentials
- Keep Ollama models and dependencies updated

## License

[Specify your license here]

## Support

For issues and questions, check the logs:
```bash
docker compose logs backend
docker compose logs ollama
docker compose logs postgres
```
