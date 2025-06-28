# Montréal Events Agent

An autonomous agent that curates and publishes interesting events in Montréal to a public Google Calendar.

**Important Note About Jazz Festival**: The Montreal International Jazz Festival runs from June 26 to July 5, 2025. Events from the festival will be automatically aggregated and added to the calendar as they become available. The agent will prioritize jazz events during this period due to their high cultural significance.

## Features

- Weekly scraping of multiple public sources for Montréal events
- Smart event ranking and filtering
- Automatic calendar updates
- Email notifications for job failures

## Data Sources

- Tourisme Montréal JSON API
- Eventbrite API
- Ticketmaster API
- RSS feeds (MTL Blog, Gazette)
- Reddit r/montreal

## Event Ranking

Events are ranked using a hybrid scoring system that considers:
- Event popularity (60% weight)
- Keyword relevance (40% weight)

### Tweaking Relevance

Edit `src/keywords.yaml` to bias the ranker. The GitHub Action will automatically load new weights on the next run.

Example:
```yaml
improv: 1.0    # Highest priority
free: 0.8      # High priority
workshop: 0.5   # Medium priority
```

## Constraints

- Maximum 5 events per day
- Maximum 3 overlapping events
- All-day blocks for festivals/multi-day events
- Curated sub-events for shows, concerts, and pop-ups

## Development

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Google Calendar service account credentials
4. Configure GitHub Actions secrets

### Testing

Run tests with pytest:
```bash
pytest tests/
```

## Deployment

**Google Cloud**
- Create a new project and enable the "Google Calendar API".
- Create a service account and generate a key JSON file.
- Share your blank calendar with the service account e-mail (give "make changes" permission).

**GitHub Secrets**
- `GOOGLE_SERVICE_ACCOUNT`: base64 of key JSON (`cat key.json | base64 -w0`)
- `GCAL_ID`: your calendar's ID
- `EVENTBRITE_TOKEN`, `TICKETMASTER_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `SMTP_USER`, `SMTP_PASS`: as required by your adapters and workflow

**Local Smoke Test**
```bash
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
export GOOGLE_CALENDAR_ID=...
python -m src.main   # events should appear
```
Push to GitHub and run the workflow manually once.

**Subscribe to the Calendar**
- Share the calendar's public URL (from Google Calendar settings) with users who want to subscribe.

## License

MIT License 