import gspread
from google.oauth2.service_account import Credentials

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive']

json_file = '3BLD Leagues-ea0916299a75.json'
creds = Credentials.from_service_account_file(json_file, scopes=scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1K09SK9d_a5xZBNg__FcKqGXp5M5whLCTa8mD_kbi6KU')
