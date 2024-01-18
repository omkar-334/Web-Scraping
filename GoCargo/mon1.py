import requests
import json
import pandas as pd


url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR8P8FWB28g0TMqz1TYyFirTokpbumL_AfEi4lVJNIf3M91HGfo9E2tmMIQMzNJ2Ad4sTqipiCLbkjD/pub?output=csv"
df = pd.read_csv(url)

apiKey='''eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjMwMDcxODM5NiwiYWFpIjoxMSwidWlkIjo1Mjc5MzQ0MCwiaWFkIjoiMjAyMy0xMi0wNVQxMjo0NjoxNy4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjAxNTA5MzEsInJnbiI6ImFwc2UyIn0.rbubLgxPJRuOMfNzodDi5sCZ2Ixub4rj8gbt0tww92U'''
board="1830621183"
group="new_group19939"

df['json'] = df.to_json(orient='records', lines=True).splitlines()

def create_item(board_id, group_id, item_name, column_values):
    query = f'''mutation
    {{
        create_item (
            board_id: {board_id},
            group_id: {group_id},
            item_name: {item_name},
            column_values: {json.dumps(json.dumps(column_values))},
        )}}'''
    return query

create_item(board,group,item,colvalues)





