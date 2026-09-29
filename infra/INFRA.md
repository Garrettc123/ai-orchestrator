# Garrett.ai infrastructure

Own box. One process. One network. One ledger volume.

This is not Vercel. This is not 181 containers. Cognitive state and the audit ledger stay on disk you control.

## Layout

```
garrett-ai network
  └── core :8000 bound to 127.0.0.1
        └── volume garrett-ai-ledger → /data
```

Stripe, HubSpot, Gmail stay as host-side connectors. Secrets never enter the image.

## Bring up

```bash
cp -n backend/.env.example backend/.env
docker compose -f infra/docker-compose.yml up -d --build
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/v1/onesys
```

Bind is localhost. Put Caddy or Tailscale in front if the box must face the internet. Do not publish 8000 on 0.0.0.0 until a proxy owns TLS.

## What runs vs what does not

Runs: Garrett.ai core (RHNS gate + eleven organs + LLA-47 checkout pointer).
Does not run: Titan mainnet, Solana, 181 packaged repos.

## Detach

```bash
docker compose -f infra/docker-compose.yml down
docker volume inspect garrett-ai-ledger
```
