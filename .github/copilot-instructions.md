# GitHub Copilot Instructions for Project Argus

## Project Overview

Project Argus is an AI-driven Network Intrusion Detection/Prevention System (NIDS/NIPS) designed for Small Office/Home Office (SOHO) environments. It runs on lightweight hardware (Raspberry Pi 4/5) and uses behavioral anomaly detection to identify, rate, and prevent network threats.

## Technology Stack

- **Language**: Python 3.8+
- **AI/ML**: TensorFlow/Keras (Autoencoder neural networks), scikit-learn (Isolation Forest)
- **Packet Capture**: Scapy
- **Database**: InfluxDB (time-series data storage)
- **Backend API**: FastAPI with Uvicorn
- **Frontend Dashboard**: Plotly Dash with Bootstrap components
- **IPS/Firewall**: iptables integration
- **Security Scanning**: python-nmap
- **Testing**: pytest with pytest-asyncio and pytest-cov

## Code Organization

```
src/
├── api/           # FastAPI REST API endpoints
├── capture/       # Packet capture and network flow extraction
├── dashboard/     # Plotly Dash web interface
├── ips/           # Intrusion Prevention System (iptables management)
├── models/        # AI/ML models (Autoencoder, preprocessing)
├── scoring/       # Trust score calculation and vulnerability scanning
├── utils/         # Utility functions and helpers
└── config.py      # Configuration management

model_training/    # ML model training scripts and algorithms
tests/            # Unit and integration tests
scripts/          # Setup and deployment scripts
docs/             # Documentation
```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes (Google style)
- Keep functions focused and modular
- Prefer async/await for I/O operations in API endpoints

### Security Considerations

**CRITICAL**: This is a security tool that processes network traffic and controls firewall rules.

- Never log or expose sensitive network data (passwords, tokens, API keys)
- Validate all user inputs, especially IP addresses and network interface names
- Use environment variables (`.env`) for sensitive configuration
- Be extremely careful when modifying iptables/firewall rules
- Always validate network addresses and CIDR ranges before use
- Sanitize all data before executing system commands
- Use parameterized queries for database operations

### AI/ML Model Guidelines

- Models are trained on network flow features (packet counts, byte counts, protocols, ports)
- Autoencoder model detects anomalies by reconstruction error
- Features must be normalized/standardized before inference
- TFLite models are optimized for Raspberry Pi deployment
- Always validate model inputs are properly preprocessed
- Model files are stored in `data/models/` directory

### API Development

- Use FastAPI with Pydantic models for request/response validation
- All endpoints should handle errors gracefully
- Use async endpoints for database queries and ML inference
- Follow RESTful conventions for endpoint naming
- Document all endpoints with FastAPI's automatic OpenAPI generation
- Authentication/authorization should be considered for production deployments

### Database Operations

- InfluxDB is used for time-series network flow data
- Use the `InfluxDBManager` class for all database operations
- Tag data appropriately (device_ip, protocol, flow_type)
- Field names should be consistent across writes
- Handle connection failures and retries gracefully

### Testing Requirements

- Write unit tests for new features in `tests/` directory
- Use pytest fixtures for common test setup
- Mock external dependencies (InfluxDB, network interfaces, nmap)
- Test both normal and edge cases
- Aim for >80% code coverage on new code
- Run tests with: `pytest tests/`
- Use `pytest-asyncio` for testing async functions

### Network Capture

- Packet capture requires root/sudo privileges
- Always check interface exists before starting capture
- Handle packet parsing errors gracefully (malformed packets)
- Flow aggregation uses 60-second windows
- SimulatedTrafficGenerator is available for testing without real network access

### Trust Score System

- Device trust scores range from 0-100 (100 = fully trusted)
- Scores are calculated from: behavioral anomalies, vulnerability scans, reputation
- Critical threshold (default: 20) triggers automatic blocking
- Scores decay over time without new anomalies
- Whitelist bypasses all scoring and blocking

### IPS/IDS Modes

- **Passive Mode (IDS)**: Monitors and alerts only, no blocking
- **Inline Mode (IPS)**: Can actively block traffic via iptables
- Always test in passive mode before enabling inline mode
- Critical devices should be whitelisted to prevent accidental blocking

### Configuration

- Configuration is loaded from `.env` file (use `.env.example` as template)
- The `config.py` module provides centralized configuration access
- Validate configuration on startup
- Provide sensible defaults for optional settings

### Logging

- Use Python's `logging` module (not print statements)
- Log levels: DEBUG (verbose), INFO (normal operations), WARNING (issues), ERROR (failures)
- Logs are written to `data/logs/argus.log` and console
- Include context in log messages (device IP, flow ID, etc.)
- Avoid logging sensitive data

### Dashboard Development

- Dashboard is built with Plotly Dash
- Use Dash Bootstrap Components for UI consistency
- Real-time updates use Dash intervals (default: 5 seconds)
- Color-code trust scores: Green (>70), Yellow (40-70), Red (<40)
- Handle missing data gracefully

### Performance Considerations

- This runs on Raspberry Pi with limited resources
- Minimize memory usage in packet capture loop
- Use TFLite models instead of full TensorFlow for inference
- Batch database writes when possible
- Implement data retention policies (delete old flows)
- Monitor CPU/memory usage

### Dependencies

- Core dependencies are in `requirements.txt`
- Scapy requires libpcap development headers
- InfluxDB must be running before starting the system
- TensorFlow installation may require platform-specific builds for ARM

### Common Workflows

**Starting the system:**
```bash
python3 main.py full --mode passive
```

**Training a new model:**
```bash
python3 train_model.py --synthetic --num-flows 5000
```

**Running tests:**
```bash
pytest tests/ -v --cov=src
```

**Simulated traffic for testing:**
```bash
python3 main.py start --mode simulated
```

## File Naming Conventions

- Python modules: lowercase with underscores (e.g., `packet_capture.py`)
- Classes: PascalCase (e.g., `PacketCapture`, `TrustScoreManager`)
- Functions/variables: lowercase with underscores (e.g., `calculate_trust_score`)
- Constants: UPPERCASE with underscores (e.g., `DEFAULT_THRESHOLD`)

## Error Handling

- Catch specific exceptions rather than bare `except:`
- Provide informative error messages
- Log errors with stack traces
- Gracefully degrade when possible (e.g., continue without ML if model missing)
- Return appropriate HTTP status codes in API endpoints

## Documentation

- Update README.md for user-facing features
- Update ARCHITECTURE.md for system design changes
- Update API.md for new endpoints
- Use docstrings for inline code documentation
- Keep IMPLEMENTATION.md updated with development progress

## Deployment

- Target platform: Raspberry Pi 4/5 with Raspberry Pi OS (Debian-based)
- Setup script: `scripts/setup.sh`
- Systemd services for production deployment
- Environment variables must be configured in `.env`

## When Making Changes

1. Ensure changes don't break existing functionality
2. Add or update tests for new features
3. Update relevant documentation
4. Test on target platform if possible (Raspberry Pi)
5. Consider security implications
6. Validate configuration changes
7. Check resource usage impact
8. Test both passive and inline modes when applicable

## Resources

- Project README: `/README.md`
- Architecture: `/docs/ARCHITECTURE.md`
- API Documentation: `/docs/API.md`
- Installation Guide: `/docs/INSTALLATION.md`
- Quick Start: `/docs/QUICK_START_GUIDE.md`
