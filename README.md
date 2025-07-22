# Discord Bot Image

A Discord bot deployed using Docker, built using FastAPI and Discord.py 

## TODO
- Implement AWS functionality
- Implement Agent functionality
- Implement RAG functionality
- Implement attachments
- Finalize README documentation
- Finalize basic bot functionality
- ~~Implement basic AI query functionality~~ (7/20/25)
- ~~Local Testing~~ (7/20/25)

## Architecture

This project consists of three main components:

- **Discord Bot** - Python-based Discord bot with various cogs and functionality
- **FastAPI API** - REST API backend for bot operations and external integrations
- **AWS CDK Infrastructure** - TypeScript-based infrastructure as code for AWS deployment

## Getting Started

### Prerequisites
- Python 3.13
- Discord Bot Token
- Ollama server
- AWS Account
- AWS CLI configured
- Node.js with npm

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Synopsik/discord-bot-image.git
   cd aws-discord-bot
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   cd image/bot
   pip install -r requirements.txt
   cd ../..
   cd image/api
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


## Development

### Local Development

1. **Use Docker Compose**
```shell script
cd image
docker-compose up --build
```

2. **Run the API individually (alternative)**
```shell script
cd image/api
python main.py
```

3. **Run the Discord bot individually (alternative)**
```shell script
cd image/bot
python main.py
```

