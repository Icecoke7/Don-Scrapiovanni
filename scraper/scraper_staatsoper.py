"""
Wiener Staatsoper ticket availability scraper
Checks daily at 09:30 AM Austria time for ticket availability for tomorrow's show
"""
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict
import pytz

import azure.functions as func
import requests
from bs4 import BeautifulSoup

bp = func.Blueprint()

# Track last execution to avoid duplicate notifications
_last_staatsoper_run = None

# Wiener Staatsoper base URL
STAATSOPER_BASE_URL = "https://tickets.wiener-staatsoper.at"
STAATSOPER_EVENTLIST_URL = f"{STAATSOPER_BASE_URL}/webshop/webticket/eventlist"

# Austria timezone (handles CET/CEST automatically)
AUSTRIA_TZ = pytz.timezone('Europe/Vienna')

def send_telegram_notification(message: str) -> bool:
    """
    Send a Telegram notification
    Returns True if successful, False otherwise
    """
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not telegram_token or not telegram_chat_id:
        logging.warning("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set, cannot send notification")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logging.info("Telegram notification sent successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to send Telegram notification: {e}")
        return False

def parse_date_time(date_str: str, time_str: str) -> Optional[datetime]:
    """
    Parse Austrian date format (e.g., "18.01.2026") and time (e.g., "19:00")
    Returns datetime in Austria timezone
    """
    try:
        # Parse date: "18.01.2026" -> datetime
        date_parts = date_str.strip().split('.')
        if len(date_parts) != 3:
            return None
        
        day = int(date_parts[0])
        month = int(date_parts[1])
        year = int(date_parts[2])
        
        # Parse time: "19:00" -> hour, minute
        time_parts = time_str.strip().split(':')
        if len(time_parts) != 2:
            return None
        
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        dt = datetime(year, month, day, hour, minute)
        # Localize to Austria timezone
        dt = AUSTRIA_TZ.localize(dt)
        
        return dt
    except Exception as e:
        logging.error(f"Error parsing date/time '{date_str} {time_str}': {e}")
        return None

def extract_show_info(event_element) -> Optional[Dict]:
    """
    Extract show information from an event element
    Returns dict with: title, author, date, time, event_id, is_available
    """
    try:
        show_info = {}
        
        # Extract event ID from button or link
        # Button has class "btn btn-primary full-width" and href like "/webshop/webticket/selectseat?eventId=11553&el=true"
        button = event_element.find('a', class_=lambda x: x and 'btn' in x if x else False)
        if button and button.get('href'):
            href = button.get('href')
            # Extract eventId from href like "/webshop/webticket/selectseat?eventId=11553&el=true"
            if 'eventId=' in href:
                event_id = href.split('eventId=')[1].split('&')[0]
                show_info['event_id'] = event_id
        
        # Check for ticket availability
        # Available: button with "Restkarten" text
        # Sold out: div with class "text-small" containing "Ausverkauft"
        is_available = None  # Unknown initially
        
        # First check for sold out indicator
        sold_out_div = event_element.find('div', class_='text-small')
        if sold_out_div:
            sold_out_text = sold_out_div.get_text(strip=True)
            if 'Ausverkauft' in sold_out_text:
                is_available = False
        
        # Check button text for availability
        if button:
            button_text = button.get_text(strip=True)
            if 'Restkarten' in button_text:
                is_available = True
            elif 'Ausverkauft' in button_text:
                is_available = False
        
        # Default to False if we can't determine
        show_info['is_available'] = is_available if is_available is not None else False
        
        show_info['is_available'] = is_available
        
        # Extract title - look for common patterns
        # Title might be in h2, h3, or strong tags
        title_elem = (
            event_element.find('h2') or 
            event_element.find('h3') or 
            event_element.find('strong') or
            event_element.find('div', class_=lambda x: x and 'title' in x.lower() if x else False)
        )
        
        if title_elem:
            show_info['title'] = title_elem.get_text(strip=True)
        else:
            # Fallback: try to find text that looks like a title
            all_text = event_element.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            if lines:
                show_info['title'] = lines[0]
        
        # Extract author/composer - usually near the title
        # Look for patterns like "by Mozart" or "Wolfgang Amadeus Mozart"
        author_elem = event_element.find('div', class_=lambda x: x and ('author' in x.lower() or 'composer' in x.lower() if x else False))
        if not author_elem:
            # Try to find text after title that might be author
            all_text = event_element.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            # Author is often on a separate line after title
            if len(lines) > 1:
                # Check if second line looks like an author name (contains common composer names or "von")
                potential_author = lines[1]
                if any(name in potential_author for name in ['Mozart', 'Beethoven', 'Verdi', 'Wagner', 'Puccini', 'Strauss', 'von', 'by']):
                    show_info['author'] = potential_author
        
        # Extract date and time
        # Look for date patterns like "18.01.2026" and time like "19:00"
        date_elem = event_element.find(string=lambda text: text and '.' in text and len(text.strip().split('.')) == 3)
        time_elem = event_element.find(string=lambda text: text and ':' in text and len(text.strip().split(':')) == 2)
        
        # Alternative: look in specific elements
        if not date_elem:
            # Try to find date in common patterns
            date_patterns = event_element.find_all(string=lambda text: text and re.match(r'\d{2}\.\d{2}\.\d{4}', text.strip()) if text else False)
            if date_patterns:
                date_elem = date_patterns[0]
        
        if not time_elem:
            # Try to find time in common patterns (HH:MM)
            time_patterns = event_element.find_all(string=lambda text: text and re.match(r'\d{2}:\d{2}', text.strip()) if text else False)
            if time_patterns:
                time_elem = time_patterns[0]
        
        if date_elem and time_elem:
            date_str = date_elem.strip()
            time_str = time_elem.strip()
            show_info['date'] = date_str
            show_info['time'] = time_str
            show_info['datetime'] = parse_date_time(date_str, time_str)
        
        return show_info if show_info else None
        
    except Exception as e:
        logging.error(f"Error extracting show info: {e}")
        return None

def fetch_staatsoper_events() -> list:
    """
    Fetch events from Wiener Staatsoper eventlist page
    Returns list of event dictionaries
    """
    events = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Staatsoper: Fetching URL: {STAATSOPER_EVENTLIST_URL}")
        response = requests.get(STAATSOPER_EVENTLIST_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all event elements
        # Events are likely in containers like divs, articles, or list items
        # Look for elements that contain both date/time and ticket availability info
        event_containers = []
        
        # Try different patterns to find event containers
        patterns = [
            soup.find_all('div', class_=lambda x: x and ('event' in x.lower() or 'show' in x.lower() or 'performance' in x.lower() if x else False)),
            soup.find_all('article'),
            soup.find_all('div', class_=lambda x: x and 'card' in x.lower() if x else False),
            soup.find_all('li', class_=lambda x: x and ('event' in x.lower() or 'show' in x.lower() if x else False)),
        ]
        
        for pattern_results in patterns:
            if pattern_results and len(pattern_results) > 0:
                event_containers = pattern_results
                logging.info(f"Staatsoper: Found {len(event_containers)} event containers using pattern")
                break
        
        # If no specific containers found, try to find elements with both date and button
        if not event_containers:
            # Look for elements that contain both a date pattern and a button
            all_divs = soup.find_all(['div', 'article', 'li'])
            for div in all_divs:
                text = div.get_text()
                # Check if it has a date pattern and a button (indicating it's an event)
                if ('.' in text and ':' in text and 
                    (div.find('a', class_='btn') or div.find('div', class_='text-small'))):
                    event_containers.append(div)
        
        logging.info(f"Staatsoper: Processing {len(event_containers)} event containers")
        
        # Extract info from each event
        for event_elem in event_containers:
            show_info = extract_show_info(event_elem)
            if show_info:
                events.append(show_info)
        
        logging.info(f"Staatsoper: Extracted {len(events)} events")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Staatsoper: Error fetching events: {e}")
    except Exception as e:
        logging.error(f"Staatsoper: Unexpected error: {e}")
    
    return events

def find_tomorrows_show(events: list) -> Optional[Dict]:
    """
    Find the show that is scheduled for tomorrow
    Returns the event dict if found, None otherwise
    """
    # Get tomorrow's date in Austria timezone
    now_austria = datetime.now(AUSTRIA_TZ)
    tomorrow = now_austria + timedelta(days=1)
    tomorrow_date = tomorrow.date()
    
    logging.info(f"Staatsoper: Looking for show on {tomorrow_date}")
    
    for event in events:
        if 'datetime' in event and event['datetime']:
            event_date = event['datetime'].date()
            if event_date == tomorrow_date:
                logging.info(f"Staatsoper: Found tomorrow's show: {event.get('title', 'Unknown')}")
                return event
    
    logging.warning(f"Staatsoper: No show found for {tomorrow_date}")
    return None

@bp.timer_trigger(schedule="0 * * * * *", arg_name="timerObj", run_on_startup=False)
def staatsoper_scraper(timerObj: func.TimerRequest) -> None:
    """
    Wiener Staatsoper ticket availability checker
    Runs daily at 09:30 AM Austria time
    Timer runs every minute, but only executes at 09:30
    """
    global _last_staatsoper_run
    
    # Get current time in Austria timezone
    now_austria = datetime.now(AUSTRIA_TZ)
    
    # Only run at 09:30 AM Austria time
    if now_austria.hour != 9 or now_austria.minute != 30:
        return
    
    # Avoid duplicate runs in the same minute
    if _last_staatsoper_run is not None:
        time_since_last = (now_austria - _last_staatsoper_run).total_seconds()
        if time_since_last < 60:  # Less than 1 minute ago
            return
    
    _last_staatsoper_run = now_austria
    logging.info(f'Staatsoper scraper triggered at {now_austria.strftime("%Y-%m-%d %H:%M:%S %Z")}')
    
    try:
        # Fetch all events
        events = fetch_staatsoper_events()
        
        if not events:
            logging.warning("Staatsoper: No events found on the page")
            return
        
        # Find tomorrow's show
        tomorrow_show = find_tomorrows_show(events)
        
        if not tomorrow_show:
            logging.info("Staatsoper: No show scheduled for tomorrow")
            return
        
        # Check ticket availability
        if tomorrow_show.get('is_available', False):
            # Tickets are available - send notification
            title = tomorrow_show.get('title', 'Unknown Show')
            author = tomorrow_show.get('author', 'Unknown Author')
            date = tomorrow_show.get('date', 'Unknown Date')
            time = tomorrow_show.get('time', 'Unknown Time')
            
            message = (
                f"🎭 <b>Wiener Staatsoper - Tickets Available!</b>\n\n"
                f"<b>{title}</b>\n"
                f"👤 {author}\n"
                f"📅 {date} {time}\n\n"
                f"🎫 <b>Restkarten verfügbar!</b>\n\n"
                f"<a href=\"{STAATSOPER_EVENTLIST_URL}\">View Events</a>"
            )
            
            if send_telegram_notification(message):
                logging.info(f"Staatsoper: Sent notification for available tickets: {title}")
            else:
                logging.error("Staatsoper: Failed to send Telegram notification")
        else:
            logging.info(f"Staatsoper: Tomorrow's show '{tomorrow_show.get('title', 'Unknown')}' is sold out")
    
    except Exception as e:
        logging.error(f"Staatsoper: Error in scraper: {e}")
