from bearer import Bearer
import pandas as pd
import os
path_script = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(path_script, 'data.csv'))
# data.set_index(pd.to_datetime(data['time']), inplace=True)
# data.drop(['time'], axis=1, inplace=True)
# data.index = data.index + pd.DateOffset(hours=3)
data['time'] = pd.to_datetime(data['time']) + pd.DateOffset(hours=3)
data['time'] = data['time'].dt.strftime('%d-%m-%Y %H:%M:%S')
# data_to_insert = data.values.tolist()
data_to_insert = data.tail(1).values.tolist()

gsheet = Bearer('FUFbE-aEBIbyWN5aVuX3wpWVp5pMOL8C') \
    .integration('google_sheets')

# 3. Define spreadsheet and values to append
spreadsheetId = '1HUxr6WrW4sCOenPwRmCo_e582sfGwIbFsqWOj9ZAd4Y'

# 4. Send data with a POST request
gsheet.auth('aa46f800-8e5a-11ea-b05a-8bedb8acf0eb') \
    .post(spreadsheetId + '/values/A1:append',
          body={'values': data_to_insert},
          query={'valueInputOption': 'RAW'})
