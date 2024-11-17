import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re


def extract_sheet_id(sheet_url):
    """Extract the sheet ID from a Google Sheets URL."""
    pattern = r'/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, sheet_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Google Sheets URL format")


def connect_google_sheets(sheet_url):
    """Connect to Google Sheets and return the data as a pandas DataFrame."""
    try:
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Load credentials from service account file
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'config/google_sheets_credentials.json',
            scope
        )

        # Authorize the client
        client = gspread.authorize(credentials)

        # Extract sheet ID from URL
        sheet_id = extract_sheet_id(sheet_url)

        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)

        # Get the first worksheet
        worksheet = spreadsheet.get_worksheet(0)

        # Get all values including header row
        data = worksheet.get_all_values()

        # Convert to pandas DataFrame
        if not data:
            raise ValueError("Sheet is empty")

        headers = data[0]
        values = data[1:]

        df = pd.DataFrame(values, columns=headers)

        return df

    except gspread.exceptions.APIError as e:
        raise Exception(f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error connecting to Google Sheets: {str(e)}")


def update_google_sheet(sheet_url, data):
    """Update a Google Sheet with new data."""
    try:
        # Setup authentication as above
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'config/google_sheets_credentials.json',
            scope
        )
        client = gspread.authorize(credentials)

        # Extract sheet ID and open spreadsheet
        sheet_id = extract_sheet_id(sheet_url)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.get_worksheet(0)

        # Convert DataFrame to list of lists
        values = [data.columns.values.tolist()] + data.values.tolist()

        # Clear existing content and update with new data
        worksheet.clear()
        worksheet.update(values)

    except Exception as e:
        raise Exception(f"Error updating Google Sheet: {str(e)}")