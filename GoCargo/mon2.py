import pandas as pd
from monday import MondayClient
import requests

class FetchGoogleSheet:
    def _init_(self, url, monday_api_token, board_id):
        self.df = pd.read_csv(url)
        self.monday = MondayClient(monday_api_token)
        self.board_id = board_id

    def mileage(self):
        mileage_condition = self.df["Mileage"] < 130000
        self.df = self.df[mileage_condition]

    def vauto(self):
        vauto_condition = self.df["95"] >= self.df["Reserve Price"]
        self.df = self.df[vauto_condition]

    def carfax_amt(self):
        carfax_amt_condition = self.df["Carfax Amt"] < 6000
        self.df = self.df[carfax_amt_condition]

    def tags(self):
        tags_condition_1 = self.df["Tags"] == "engine needs repair"
        tags_condition_2 = self.df["Tags"] == "tow"
        tags_condition_3 = self.df["Tags"] == "transmission"
        # Fill NaN values with False
        tags_condition_1 = tags_condition_1.fillna(False)
        tags_condition_2 = tags_condition_2.fillna(False)
        tags_condition_3 = tags_condition_3.fillna(False)
        # Apply conditions
        self.df = self.df[~(tags_condition_1 | tags_condition_2 | tags_condition_3)]

    def add_to_crm(self):
        # Assuming the columns are already created on the board
        apiUrl = "https://api.monday.com/v2"
        apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMwMDM3MjUxMiwiYWFpIjoxMSwidWlkIjo1MjY2MDE0MywiaWFkIjoiMjAyMy0xMi0wNFQxMDoxNjo0Ni4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAxMDIzMDAsInJnbiI6ImFwc2UyIn0.38lZ-aalLIs9o79_2xGRiiCcR4yIOHwSNqcybto3FN4"
        headers = {"Authorization": apiKey}

        # Iterate through filtered rows and add to CRM
        for index, row in self.df.iterrows():
            # Extract the name of the vehicle from the row
            Task1 = row["Task1"]

            # Assuming you have an "item_id" column in your DataFrame
            Link = row["link"]

            # Define the column values to be appended
            new_column_values = {}

            # Iterate through the columns you want to append
            for column_name in [
                 'Date', 'Auction Date', 'Tags'
            ]:
                # Append the value from the row to the corresponding column
                new_column_values[column_name] = {"append": row[column_name]}

            # Assuming "YOUR_BOARD_ID" is the actual board ID
            query = f'''
                mutation {{
                    change_column_values (
                        board_id: {self.board_id},
                        Link: {link},
                        column_values: {json.dumps(new_column_values)}
                    ) {{
                        id
                    }}
                }}
            '''

            data = {'query': query}
            r = requests.post(url=apiUrl, json=data, headers=headers)

            print(f"API Response for {item_name}: {r.text}")
            print(f"Status Code: {r.status_code}")

if __name__ == "_main_":
    sheet_path = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8P8FWB28g0TMqz1TYyFirTokpbumL_AfEi4lVJNIf3M91HGfo9E2tmMIQMzNJ2Ad4sTqipiCLbkjD/pub?output=csv"
    monday_api_token = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMwMDcxODM5NiwiYWFpIjoxMSwidWlkIjo1Mjc5MzQ0MCwiaWFkIjoiMjAyMy0xMi0wNVQxMjo0NjoxNy4xODRaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAxNTA5MzEsInJnbiI6ImFwc2UyIn0.oNDOHIYFqKXqacUZAwUsxM4U0c6syNIrUz-rsevzpCc"
    board_id = "1830621183"

    obj = FetchGoogleSheet(sheet_path, monday_api_token, board_id)
    obj.mileage()
    obj.vauto()
    obj.carfax_amt()
    obj.tags()
    obj.add_to_crm()