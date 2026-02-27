import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class GoogleSheets:
    def __init__(self, credentials_json, spreadsheet_id):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds_dict = json.loads(credentials_json)
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(self.creds_dict, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(spreadsheet_id)

    def get_sheet_data(self, sheet_name):
        worksheet = self.sheet.worksheet(sheet_name)
        return worksheet.get_all_records()

    def append_row(self, sheet_name, row):
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.append_row(row)

    def append_rows(self, sheet_name, rows):
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.append_rows(rows)

    def update_cell(self, sheet_name, row, col, val):
        worksheet = self.sheet.worksheet(sheet_name)
        worksheet.update_cell(row, col, val)

    def get_config(self):
        records = self.get_sheet_data("config")
        config = {}
        for row in records:
            config[row["key"]] = row["value"]
        return config
