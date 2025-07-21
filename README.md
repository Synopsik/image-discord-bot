# AWS Discord Bot

A Discord bot application built with FastAPI and deployed on AWS using CDK infrastructure.

## 🏗️ Architecture

This project consists of three main components:

- **Discord Bot** - Python-based Discord bot with various cogs and functionality
- **FastAPI API** - REST API backend for bot operations and external integrations
- **AWS CDK Infrastructure** - TypeScript-based infrastructure as code for AWS deployment

## 📁 Project Structure
```

├── image/                   # Main application code
│   ├── api/                 # FastAPI REST API
│   │   ├── endpoints/       # API endpoints
│   │   └── main.py         # FastAPI application entry point
│   ├── bot/                 # Discord bot implementation
│   │   └── cogs/           # Discord bot command groups
│   ├── util/               # Shared utilities
│   ├── .env.sample         # Environment variables template
│   └── docker-compose.yml  # Local development setup
├── cdk-infra/              # AWS CDK infrastructure code
│   ├── bin/                # CDK app entry points
│   ├── lib/                # CDK stack definitions
│   └── test/               # Infrastructure tests
└── README.md               # This file
```
## 🚀 Getting Started

### Prerequisites

- Python 3.13.5
- Node.js with npm
- AWS CLI configured
- Discord Bot Token
- AWS Account

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aws-discord-bot
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up CDK dependencies**
   ```bash
   cd cdk-infra
   npm install
   cd ..
   ```

4. **Configure environment variables**
   ```bash
   cp image/.env.sample image/.env
   # Edit image/.env with your configuration
   ```

### Environment Variables

Copy `image/.env.sample` to `image/.env` and configure:

```env
BOT_TOKEN=your_discord_bot_token
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
GUILD_ID=your_discord_guild_id
API_URL=your_api_endpoint_url
OLLAMA_BASE_URL=your_ollama_instance_url
DB_URL=your_database_connection_string
```


## 🛠️ Development

### Local Development

1. **Run the API locally**
```shell script
cd image
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```


2. **Run the Discord bot**
```shell script
cd image
   python bot/main.py
```


3. **Use Docker Compose (alternative)**
```shell script
cd image
   docker-compose up
```


### Testing

Run tests for the infrastructure:
```shell script
cd cdk-infra
npm test
```


## 📦 Deployment

### AWS Infrastructure

1. **Bootstrap CDK (first time only)**
```shell script
cd cdk-infra
   npx cdk bootstrap
```


2. **Deploy infrastructure**
```shell script
cd cdk-infra
   npx cdk deploy
```


### Application Deployment

The application is containerized and deployed to AWS Lambda using the Mangum adapter for FastAPI.

## 🤖 Discord Bot Features

The bot includes several cogs with different functionalities:

- **Logging Cog** - Comprehensive server activity logging
    - Message tracking (create, edit, delete)
    - Member activity (join, leave, updates)
    - Command execution logging
    - Reaction tracking

- **General Commands** - Basic bot functionality
- **Agent Commands** - AI integration capabilities
- **Games** - Gaming-related features

## 🔧 API Endpoints

The FastAPI application provides:

- Health check endpoints
- Query processing with AI integration
- Reset functionality
- Bot management endpoints

## 📊 Monitoring & Logging

The application includes comprehensive logging capabilities:

- Discord activity logging
- Command execution tracking
- Error handling and reporting
- Timestamp formatting utilities

## 🧪 Testing

- Infrastructure tests using Jest
- API endpoint testing
- Bot functionality testing

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contributing guidelines here]

