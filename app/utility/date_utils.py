from datetime import datetime, timedelta

def format_date(date):
    """Format datetime object to YYYYMMDD."""
    return date.strftime("%Y%m%d")

def parse_custom_date(from_date_str, to_date_str):
    """Parse custom 'from' and 'to' dates in MM/DD/YYYY format."""
    from_date = datetime.strptime(from_date_str, "%m/%d/%Y")
    to_date = datetime.strptime(to_date_str, "%m/%d/%Y")
    print(from_date, to_date)
    return from_date, to_date

def get_date_range(time_range, from_date_str=None, to_date_str=None):
    print(time_range, from_date_str, to_date_str)
    """Calculate start and end dates for given time range."""
    if time_range == "Custom" and from_date_str and to_date_str:
        # Parse custom date range
        start_date, end_date = parse_custom_date(from_date_str, to_date_str)
    elif time_range == "Past 24 hours":
        end_date = datetime.now()  # Current date and time
        start_date = end_date - timedelta(days=1)
    elif time_range == "Past week":
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=1)
    elif time_range == "Past month":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Approximation
    elif time_range == "Past year":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # Approximation
    elif time_range == "Past hour":
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(hours=1)   
    else:
   # Default case: Sort from last week to today
        now = datetime.now()
        start_date = now - timedelta(weeks=1)
        end_date = now
        print("Default time range applied: Last week to today.")


    # Format dates to YYYYMMDD
    start_date_str = format_date(start_date)
    end_date_str = format_date(end_date)

    # Optionally, print the calculated start and end dates
    print(f"Start Date: {start_date_str} - End Date: {end_date_str}")

    return start_date_str, end_date_str
