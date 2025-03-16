# Local Scripts
from typing import List
from fetch_emails import InvoiceData

# GMAIL
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Data analysis
import pandas as pd

# OS
import os
#from dotenv import load_dotenv

# Loading the environmental variables from the containing folder
#load_dotenv(dotenv_path=r'src\\keys\\.env')

def upload_tx_data(tx_data: List[InvoiceData]) -> None:
    """
    Upload the tx data to the google sheet

    Args:
        tx_data (List[InvoiceData]): The tx data to be uploaded to the google sheet
    """

    # scope for the google sheet
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # credentials for the google sheet
    creds = ServiceAccountCredentials.from_json_keyfile_name(filename='GSHEETS.json', scopes=scope)

    # authorize the clientsheet 
    client = gspread.authorize(creds)
    
    # the file path for the csv file
    budget_spreadsheet = client.open('BudgetSpreadsheet')
    
    # get the first sheet of the Spreadsheet
    budget_spreadsheet_instance = budget_spreadsheet.get_worksheet(0)
    
    # transaction data that is being passed off to the dataframe
    # Convert the list of InvoiceData objects to a DataFrame
    df = pd.DataFrame([tx.model_dump() for tx in tx_data])
    
    # Write the DataFrame to Google Sheets
    budget_spreadsheet_instance.append_rows(values=df.values.tolist(),      value_input_option='USER_ENTERED')

