# Garrett.ai

One autonomous system. Product name: **Garrett.ai**. Legal entity: Garcar Enterprise.
This repository is the runtime. The other 180 public repos are packaging under eleven organs. They are not eleven hundred products.

Storefront today: https://garrettc123.github.io/
Brand: Garrett.ai — do not claim the domain is live until DNS is yours.
Doctrine: [SYSTEM.md](SYSTEM.md) · Catalog: [CATALOG.md](CATALOG.md)

## Rule

Organs are families: Revenue, CRM, Proposal, Outreach, Billing, Fulfillment, Research, Governance, Content, Compliance, Enterprise Intelligence.
A GitHub repo is packaging. Pinning a repo does not attach an organ.

## Live cash (do not use card 4242)

- LLA-47 Lead Leak Audit — $47 — https://buy.stripe.com/3cI00j7YV0hQgDp8BR43S2v
- Stripe `acct_1SS3dpFKGbk21LK5` livemode
- SKU sheet: [SKUS.md](SKUS.md)

## Boot

```bash
cd ai-orchestrator
cp backend/.env.example backend/.env
python3 backend/serve.py
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/onesys
```

POST `/v1/onesys/act` with `{"hop":"intake"}` or `{"hop":"checkout"}`.
Money hops require CMC `commit`.

Secrets stay in `backend/.env` or the host vault.
