# Installation Options

Arbitra supports multiple installation methods to accommodate different environments.

## Quick Decision Guide

- **Can't use Docker/containers at all?** → Use Option 2 (Local Installation)
- **Want containerized but no Docker?** → Use Option 1 (Podman)
- **Just testing/development?** → Use Option 3 (No Infrastructure)

## Option 1: Podman (Recommended)

Podman is a Docker alternative that:
- ✅ Doesn't require a daemon
- ✅ Doesn't need root/sudo privileges
- ✅ Drop-in replacement for Docker
- ✅ More secure (rootless by default)

### Installation

#### macOS
```bash
brew install podman podman-compose

# Initialize podman machine
podman machine init --cpus 2 --memory 4096
podman machine start
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install podman

# Fedora/RHEL
sudo dnf install podman

# Install podman-compose
pip3 install podman-compose
```

### Usage
```bash
# Start all services
podman-compose up -d

# Check status
podman-compose ps

# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Start with monitoring (Prometheus + Grafana)
podman-compose --profile monitoring up -d
```

## Option 2: Local Installation (No Containers)

Install PostgreSQL and Redis directly on your system.

### macOS (Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Create database
createdb arbitra

# Verify
psql -d arbitra -c "SELECT version();"
redis-cli ping
```

### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt-get install postgresql-15 postgresql-client-15
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create database
sudo -u postgres createdb arbitra
sudo -u postgres createuser arbitra -P

# Verify
psql -U arbitra -d arbitra -c "SELECT version();"
redis-cli ping
```

### Linux (Fedora/RHEL)
```bash
# Install PostgreSQL
sudo dnf install postgresql15-server
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Install Redis
sudo dnf install redis
sudo systemctl start redis
sudo systemctl enable redis

# Create database
sudo -u postgres createdb arbitra
sudo -u postgres createuser arbitra -P
```

### Configuration
Update `config/config.yaml` with your local connection strings:

```yaml
database:
  postgres:
    host: localhost
    port: 5432
    database: arbitra
    user: arbitra
    password: your_password_here
  
  redis:
    host: localhost
    port: 6379
    db: 0
```

## Option 3: No Infrastructure (Testing Only)

For Phase 1 (Risk Module), you don't need any infrastructure!

```bash
# Just install Python dependencies
pip install -r requirements.txt

# Run tests (no database required)
pytest tests/risk/ -v
```

Unit tests use in-memory data and don't require PostgreSQL or Redis.

You'll need infrastructure for:
- Phase 2+: AI agent (needs vector DB)
- Phase 4+: Trade execution (needs persistent storage)
- Phase 7: Monitoring (needs Prometheus/Grafana)

## Troubleshooting

### Podman Issues

**"podman machine not running"**
```bash
podman machine start
```

**"port already in use"**
```bash
# Change ports in podman-compose.yml
# Example: "5433:5432" instead of "5432:5432"
```

**"permission denied"**
```bash
# Ensure podman is rootless
podman system info | grep rootless
```

### PostgreSQL Issues

**"connection refused"**
```bash
# Check if running
# macOS:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql
```

**"authentication failed"**
```bash
# Update pg_hba.conf to allow local connections
# macOS: /opt/homebrew/var/postgresql@15/pg_hba.conf
# Linux: /etc/postgresql/15/main/pg_hba.conf

# Add line:
# local   all   arbitra   md5
```

### Redis Issues

**"connection refused"**
```bash
# Check if running
# macOS:
brew services list | grep redis

# Linux:
sudo systemctl status redis
```

## Minimal Setup for Phase 1

If you just want to get started with the risk module:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run tests (no infrastructure needed)
pytest tests/risk/ -v --cov=src/risk

# 3. That's it! No database, no containers required.
```

You can add infrastructure later when you need it.

## Performance Comparison

| Method | Setup Time | Resource Usage | Isolation | Root Required |
|--------|-----------|----------------|-----------|---------------|
| Podman | ~5 min | Medium | Excellent | No |
| Local | ~10 min | Low | None | Maybe |
| None | ~1 min | Minimal | N/A | No |

## Recommendations by Use Case

- **Development/Testing**: Option 3 (No Infrastructure) for Phase 1
- **Production-like Testing**: Option 1 (Podman)
- **Minimal Resources**: Option 2 (Local)
- **CI/CD Pipeline**: Option 1 (Podman) or Option 3 (Tests only)
- **Personal Machine**: Option 2 (Local) if you already have PostgreSQL/Redis
