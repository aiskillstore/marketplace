import datetime

def get_current_date():
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    print(get_current_date())
