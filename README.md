# TidalHiFiDiscordRPC

This project provides a Discord Rich Presence integration for Tidal HiFi via the internal API.

## Environment Setup

Create a `.env` file in the root directory of the project by copying the example file:

```bash
cp .env.example .env
```

Edit the `.env` file to set the required environment variables. At a minimum, you'll need to set:

- `DISCORD_CLIENT_ID`: Your Discord application client ID
- `TIDAL_API_URL`: Tidal HiFi internal API
- `TIDAL_API_PORT`: Tidal HiFi internal API port

## Manual Installation and Running

Install the required Python packages:

```bash
uv pip install -r requirements.txt
```

3. Run the application:

```bash
python3 main.py
```

## Docker Installation and Running

Using docker compose

```bash
docker compose up -d --build
```

or using pure docker

```bash
docker build -t tidal-discord-rpc .
docker run -d --name tidal-discord-rpc --network host \
  --restart unless-stopped \
  -e TZ=Europe/Paris \
  -v /run/user/1000/discord-ipc-0:/tmp/discord-ipc-0:ro \
  tidal-discord-rpc
```
