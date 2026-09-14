# Sponsor Watch

Hourly Python watcher for three mortgage watchlists. It checks official company feeds/pages first when you define them in `companies.yaml`, falls back to Google News RSS when needed, dedupes locally with SQLite, and posts short markdown alerts into separate Roam channels.

Alerts are limited to articles published in the last seven days by default. Undated items are skipped so a cache miss or first run cannot flood a channel with old results. Configure `max_article_age_days` and `allow_undated_articles` in `config.yaml` if needed.

## Files

- `sponsor_watch.py`: single CLI entrypoint
- `companies.yaml`: vendor/lender/AIME watchlists and optional official sources
- `config.example.yaml`: runtime config template
- `.github/workflows/hourly.yml`: hourly GitHub Actions job

## Setup

1. Create a virtualenv and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the example config and fill in your Roam token/channel values.

```bash
cp config.example.yaml config.yaml
```

3. Add official feeds/pages to `companies.yaml` for the companies you care about most. Each company can define:

```yaml
- name: Rapidio
  official_domains:
    - rapidio.ai
  official_sources:
    - url: https://rapidio.ai/feed
      kind: rss
    - url: https://rapidio.ai/blog
      kind: html
```

If no official sources are configured for a company, the script goes straight to Google News RSS fallback.

## Commands

```bash
python sponsor_watch.py run
python sponsor_watch.py test-vendors
python sponsor_watch.py test-lenders
python sponsor_watch.py test-aime
```

- `run` scans all watchlists, posts any new alerts to Roam, and records dedupe state.
- `test-vendors`, `test-lenders`, and `test-aime` print candidate alerts without posting.

## Roam Notes

This project is wired around Roam’s Chat API endpoints:

- `POST /chat.post` for message delivery
- `GET /chat.list` to resolve a configured channel name to a chat ID
- `GET /token.info` for token validation if you want to extend the script

The docs describe chat posting as markdown-formatted text, which is what the alert formatter emits. I used the official docs here:

- [Roam HQ API](https://developer.ro.am/docs/roam-api/roam-hq-api)
- [Chat API (Alpha)](https://developer.ro.am/docs/category/chat-api-alpha)
- [Post to a chat](https://developer.ro.am/docs/chat-api/chat-post)
- [Access token info](https://developer.ro.am/docs/chat-api/token-info)

## Alert Format

```md
**[Vendor Alert] Rapidio — New Product Update**
Short summary in 1-2 lines.

Source: official company blog
Published: **2026-03-05**
Link: https://example.com/post
```

## Data Model

`companies.yaml` supports these fields per company:

- `name`: display name
- `aliases`: optional aliases used in fallback matching
- `strict_google_match`: stronger fallback filter for ambiguous names like `Roam`, `MMI`, `EPM`, `PRMG`, and `RETR`
- `official_domains`: optional allowlist used when scraping HTML pages
- `official_sources`: optional list of `rss`, `atom`, or `html` URLs

The default file now includes an `aime_mentions` watchlist for:

- `Association of Independent Mortgage Experts`
  Aliases: `AIME`
  Matching intent: the full organization name or `AIME` in mortgage context

`config.yaml` / `config.example.yaml` supports:

- `max_article_age_days`: rolling publication-age limit (seven days by default)
- `allow_undated_articles`: whether articles with no usable publication date may be sent (off by default)
- `roam_post_delay_seconds`: small pause between Roam posts to reduce rate-limit errors

## GitHub Actions

The included workflow runs hourly and also supports manual dispatch. Add these repository secrets before enabling it:

- `ROAM_API_TOKEN`
- `ROAM_VENDOR_CHANNEL`
- `ROAM_LENDER_CHANNEL`
- `ROAM_AIME_CHANNEL`

The workflow writes `config.yaml` from secrets at runtime and persists the SQLite dedupe database using the GitHub Actions cache. That is lightweight and workable for V1, but if you need stronger durability later, move state to S3/R2/Postgres.
