# shoptoli/util.py

from flask import current_app
import pytz

def format_datetime_local(dt):
    """Convert a UTC datetime object to the app's configured local timezone and format it."""
    if dt is None:
        return ""
    
    # Get the target timezone from the app's configuration
    local_tz_name = current_app.config.get('BABEL_DEFAULT_TIMEZONE', 'UTC')
    local_tz = pytz.timezone(local_tz_name)
    
    # Convert the naive UTC datetime from the database to an aware UTC datetime
    aware_utc_dt = pytz.utc.localize(dt)
    
    # Convert to the local timezone
    local_dt = aware_utc_dt.astimezone(local_tz)
    
    # Format it
    return local_dt.strftime('%B %d, %Y at %I:%M %p')