# Garcar AI Orchestrator

DFW trades revenue loop: intake → enrich → outreach → checkout → HubSpot → fulfill.

## Live cash (do not use card 4242)

- LLA-47 Lead Leak Audit — $47 — https://buy.stripe.com/3cI00j7YV0hQgDp8BR43S2v
- Stripe `acct_1SS3dpFKGbk21LK5` livemode
- Storefront: https://garrettc123.github.io/
- SKU sheet: [SKUS.md](SKUS.md)

## Boot

```bash
cd ai-orchestrator
cp backend/.env.example backend/.env
python3 backend/serve.py
curl http://127.0.0.1:8000/health
```

Docker (optional):

```bash
docker-compose -f templates/docker-compose-prod.yml up -d
```

Secrets stay in `backend/.env` or the host vault. Never paste live keys into chat.
