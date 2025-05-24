from datetime import datetime

month_translation = {
    'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April',
    'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August',
    'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
}

def convert_date(date_string):
    if isinstance(date_string, datetime):
        return date_string.date()

    # Try RFI format: '20/05/2025'
    try:
        return datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError:
        pass

    # Try Actu format: '20 mai 2025'
    try:
        day, month, year = date_string.split()
        english_month = month_translation.get(month.lower(), month)
        date_string_english = f"{day} {english_month} {year}"
        return datetime.strptime(date_string_english, "%d %B %Y").date()
    except Exception:
        return None  # return None if both formats fail
