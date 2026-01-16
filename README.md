# Don-Scrapiovanni 🎭

Monitor Wiener Staatsoper website for ticket availability and get Telegram notifications. This scraper helps monitor the website and sends a notification via Telegram once a day at 09:30 AM, so members of the (Junger) Freundeskreis can buy tickets.

## Features

- 🎭 Monitors Wiener Staatsoper ticket availability
- ⏰ Runs automatically once daily at 09:30 AM Austria time (CET/CEST)
- 🔔 Sends Telegram notifications when tickets are available
- 🌍 Timezone-aware (handles CET/CEST transitions automatically)
- 🎯 Checks for tomorrow's show specifically

## How It Works

1. **Schedule**: The scraper runs every minute (timer trigger), but only executes at 09:30 AM Austria time
2. **Target**: Checks `https://tickets.wiener-staatsoper.at/webshop/webticket/eventlist`
3. **Logic**:
   - Fetches the event list page
   - Finds the show scheduled for tomorrow
   - Checks if tickets are available (looks for "Restkarten" button or "Ausverkauft" indicator)
   - Sends Telegram notification if tickets are available

## Prerequisites

- Docker and Docker Compose
- Telegram bot token and chat ID

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Icecoke7/Don-Scrapiovanni.git
cd Don-Scrapiovanni
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
# Required for Telegram notifications
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

#### Getting a Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the token you receive (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Getting Your Telegram Chat ID

1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":123456789}` in the response
4. Copy the ID number

### 3. Build and Run with Docker

```bash
# Build the scraper container
docker compose build

# Start the services
docker compose up -d

# Check logs
docker logs staatsoper-scraper -f | grep -i staatsoper
```

### 4. Verify It's Working

The scraper will automatically run at 09:30 AM Austria time. To verify:

```bash
# Check logs for Staatsoper scraper activity
docker logs staatsoper-scraper --tail 100 | grep -i staatsoper
```

You should see messages like:
```
Staatsoper scraper triggered at 2026-01-18 09:30:00 CET+01:00
Staatsoper: Fetching URL: https://tickets.wiener-staatsoper.at/webshop/webticket/eventlist
Staatsoper: Found tomorrow's show: Le Nozze di Figaro
```

## Notification Format

When tickets are available, you'll receive a Telegram message like:

```
🎭 Wiener Staatsoper - Tickets Available!

Le Nozze di Figaro
👤 Wolfgang Amadeus Mozart
📅 18.01.2026 19:00

🎫 Restkarten verfügbar!

View Events
```

## Configuration

### Schedule

The scraper runs at **09:30 AM Austria time** (Europe/Vienna timezone). This is hardcoded in the scraper to avoid overloading the website.

To change the schedule, edit `scraper/scraper_staatsoper.py`:

```python
# Line ~296: Change the hour and minute
if now_austria.hour != 9 or now_austria.minute != 30:
    return
```

### Timezone

The scraper uses `Europe/Vienna` timezone, which automatically handles:
- CET (Central European Time, UTC+1) in winter
- CEST (Central European Summer Time, UTC+2) in summer

## How Ticket Availability is Detected

The scraper detects ticket availability by parsing the HTML:

**Available Tickets:**
- Button with class `btn` containing text "Restkarten"
- Example: `<a href="/webshop/webticket/selectseat?eventId=11553" class="btn btn-primary full-width">Restkarten</a>`

**Sold Out:**
- Div with class `text-small` containing "Ausverkauft"
- Example: `<div class="text-small"><span>Ausverkauft</span></div>`

## Troubleshooting

### Scraper Not Running at 09:30

**Check timezone:**
```bash
docker exec staatsoper-scraper date
# Should show Austria time
```

**Check logs:**
```bash
docker logs staatsoper-scraper | grep -i staatsoper
```

**Verify timer trigger:**
The timer runs every minute but only executes at 09:30. You should see log entries every minute, but the scraper logic only runs at 09:30.

### No Notifications Received

1. **Check if tickets are actually available** - The scraper only notifies when tickets are available (not when sold out)

2. **Verify Telegram credentials:**
   ```bash
   # Check if environment variables are set
   docker exec staatsoper-scraper env | grep TELEGRAM
   ```

3. **Test Telegram bot manually:**
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
     -d "chat_id=<YOUR_CHAT_ID>" \
     -d "text=Test message"
   ```

4. **Check logs for errors:**
   ```bash
   docker logs staatsoper-scraper | grep -i "telegram\|staatsoper" | tail -20
   ```

### HTML Structure Changed

If the Wiener Staatsoper website changes its HTML structure, you may need to update the selectors in `scraper/scraper_staatsoper.py`:

- `extract_show_info()` - Extracts show details from HTML (lines ~90-194)
- `fetch_staatsoper_events()` - Finds event containers on the page (lines ~196-259)

**To update selectors:**

1. Visit `https://tickets.wiener-staatsoper.at/webshop/webticket/eventlist`
2. Open Developer Tools (F12)
3. Inspect the HTML structure
4. Update the selectors in the scraper code
5. Rebuild: `docker compose build && docker compose restart staatsoper-scraper`

### No Events Found

If you see "Staatsoper: No events found on the page":

1. **Check if the website is accessible:**
   ```bash
   curl -I https://tickets.wiener-staatsoper.at/webshop/webticket/eventlist
   ```

2. **Check for HTML structure changes** (see above)

3. **Check logs for parsing errors:**
   ```bash
   docker logs staatsoper-scraper | grep -i "staatsoper.*error"
   ```

## Development

### Running Locally (without Docker)

1. Install dependencies:
   ```bash
   cd scraper
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export TELEGRAM_TOKEN=your_token
   export TELEGRAM_CHAT_ID=your_chat_id
   ```

3. Run Azure Functions locally:
   ```bash
   func start
   ```

### Testing

To test the scraper manually, you can modify the schedule temporarily:

```python
# In scraper_staatsoper.py, temporarily change:
if now_austria.hour != 9 or now_austria.minute != 30:
    return

# To:
if False:  # Always run for testing
    return
```

Then rebuild and restart:
```bash
docker compose build
docker compose restart staatsoper-scraper
```

## File Structure

```
Don-Scrapiovanni/
├── scraper/
│   ├── scraper_staatsoper.py        # Main scraper implementation
│   ├── function_app.py              # Registers the scraper
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                    # Docker build configuration
│   └── host.json                     # Azure Functions configuration
├── docker-compose.yml                # Docker Compose configuration
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## Notes

- The scraper only checks for **tomorrow's** show, not all upcoming shows
- Notifications are only sent when tickets are **available** (not when sold out)
- The scraper runs once per day to avoid overloading the website
- Timezone handling is automatic (CET/CEST transitions)
- The scraper uses a global variable to prevent duplicate runs in the same minute

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `docker logs staatsoper-scraper | grep -i staatsoper`
3. Verify your environment variables are set correctly
4. Check if the website structure has changed

## Acknowledgments

- Built for monitoring Wiener Staatsoper ticket availability
- Uses BeautifulSoup for HTML parsing
- Uses pytz for timezone handling
