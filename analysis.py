# Python module imports
import argparse
from cmath import nan
import json
import sys
import time
import logging
import os
import pandas as pd
import logging
import yagmail

# logging
LOGGER = logging.getLogger("wf-monitor")
logging.basicConfig(
    format = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level = logging.INFO)


def to_df(infile):
    '''
    Parameters
    ----------
    infile : {string}  Absolute name of the log file.

    Returns
    -------
    df : pandas dataframe (keeping all the data from the infile)
    '''

    time = []
    file_loc = []
    type = []
    message = []

    with open(infile) as f:
        for line in f:
            # parsing log lines; only if length is bigger than 0
            if len(line) != 0:

                # 2022-08-30 15:52:17,689 src.workflow INFO     Loading config: configs/alicante-consumption.json

                no_time = line.split(',', 1)
                time.append(no_time[0]) # 2022-08-30 15:52:17
                no_time_str = no_time[1].strip() # 689 src.workflow INFO     Loading config: configs/alicante-consumption.json

                no_index = no_time_str.split(' ', 1)
                no_index_str = no_index[1].strip() # src.workflow INFO     Loading config: configs/alicante-consumption.json

                no_file_loc = no_index_str.split(' ', 1)
                file_loc.append(no_file_loc[0]) # src.workflow
                no_file_loc_str = no_file_loc[1].strip() # INFO     Loading config: configs/alicante-consumption.json

                no_type = no_file_loc_str.split(' ', 1)
                type.append(no_type[0]) # INFO
                no_type_str = no_type[1] # Loading config: configs/alicante-consumption.json

                message.append(no_type_str) # Loading config: configs/alicante-consumption.json

    df = pd.DataFrame(data={'Time': time, 'File_loc': file_loc, 'Type':type, 'Message': message})
    return df


def find_problems(df):
    '''
    Parameters
    ----------
    df : pandas dataframe

    Returns
    -------
    df : pandas dataframe \n
    Copy of the original df, but only the rows where 'ERROR' or 'WARNING' occurred. \n
    The "Message" column translated to "Column". Added "Location" and "Action" columns.
    '''

    time = []
    type = []

    location = []
    action = []

    problem = []

    for index in range(len(df)):
        if df['Type'][index] == 'WARNING' or df['Type'][index] == 'ERROR':
            time.append(df['Time'][index])
            type.append(df['Type'][index])
            problem.append(df['Message'][index])

            if df['File_loc'][index] == 'src.historic':
                action.append('API')
            elif df['File_loc'][index] == 'src.influx':
                action.append('Influx')
            else: #df['file_loc'][index] == 'src.kafka'
                action.append('Kafka')

            i=index
            while df['File_loc'][i] != 'src.workflow':
                i -= 1
            checking = df['Message'][i].replace('Checking: ','')
            location.append(checking)

    new_df = pd.DataFrame(data={'Time': time, 'Type': type, 'Action': action, 'Location': location, 'Problem': problem})
    return new_df


def extract_time(df, i):
    '''
    Parameters
    ----------
    df : pandas dataframe \n
    i : index of the row

    Returns
    -------
    None; if cell not of the form: "Timestamp bigger than: ... " \n
    numerical value; else
    '''

    problem = df['Problem'][i]
    if 'Timestamp bigger' in problem:
        time = problem.split(':')[1].strip()
        time = float(time[:-1])
        return time
    return None


def previous_time(df, i):
    '''
    Parameters
    ----------
    df : pandas dataframe \n
    i: index of the row

    Returns
    -------
    float: Time_spent value from the last row with the same location and defined time in "Problem" column
    '''

    if df['Action'][i] == 'API':
        return 0

    location = df['Location'][i].split(' ')[-1]

    index = i
    while index!=0:
        index -= 1
        if location in df['Location'][index]:
            if df['Location'][i] == 'Kafka': #specifically for alicante-consumption.log because there are two fusion-prediction pairs
                if 'Prediction' in location:
                    if 'Prediction' not in df['Location'][index]:
                        if extract_time(df, index):
                            return extract_time(df, index)
                    return previous_time(df, index)
                elif 'Fusion' in location:
                    if df['Action'][index] != 'Kafka': #should be from 'Influx' (possibly 'API' ?)
                        if extract_time(df, index):
                            return extract_time(df, index)
                    return previous_time(df, index)

            if extract_time(df, index):
                return extract_time(df, index)
            return previous_time(df, index)
    return 0


def analyse_df(df):
    '''
    Parameters
    ----------
    df : pandas dataframe

    Returns
    -------
    df : pandas datafram \n
    Copy of the original df but with an added column (calculated time spent for a task)
    '''

    time_spent = []
    for index in range(len(df)):
        time_1 = extract_time(df, index)
        time_2 = previous_time(df, index)
        if time_2 and time_1:
            time = time_1 - time_2
        else:
            time = time_1
        time_spent.append(time)
    df['Time_spent'] = time_spent
    return df


def correct_type(df):
    '''
    Parameters
    ----------
    df : pandas dataframe

    Returns
    -------
    df : pandas dataframe \n
    Same df with corrected "Type" column (if WARNING or ERROR don't look like a problem anymore).\n
    new_df : pandas dataframe \n
    Presents error and warning counts for each location, as well as description of the problem.
    '''
    # check if API time delays are in the limits (based on sensor and df)
    for i, row in df.iterrows():
        if df['Action'][i] != 'API':
            time = df['Time_spent'][i]
            if pd.isna(time) or time < -1 or time > 1:
                df.at[i, 'Type'] = 'ERROR'
            else:
                df.at[i, 'Type'] = 'INFO'

    actions = []
    locations = []
    warning_count = []
    error_count = []
    problems = [] # list of lists of problems for each location
    for i, row in df.iterrows():
        current_location = df['Location'][i]
        current_type = df['Type'][i]
        if current_location in locations:
            j = locations.index(current_location)
            if current_type == 'ERROR':
                error_count[j] += 1
                problems[j].append(df['Problem'][i])
            elif current_type == 'WARNING':
                warning_count[j] += 1
                problems[j].append(df['Problem'][i])
        else:
            if current_type == 'ERROR':
                actions.append(df['Action'][i])
                locations.append(current_location)
                error_count.append(1)
                warning_count.append(0)
                problems.append([df['Problem'][i]])
            elif current_type == 'WARNING':
                actions.append(df['Action'][i])
                locations.append(current_location)
                error_count.append(0)
                warning_count.append(1)
                problems.append([df['Problem'][i]])

    #convert list of problems to string
    problems_str = []
    for problem_list in problems:
        problem_str = ''
        for problem in problem_list:
            problem_str += '; ' + problem
        problems_str.append(problem_str[2:])
    new_df = pd.DataFrame(data = {'Action': actions, 'Location': locations, 'Error': error_count, 'Warning': warning_count, 'Problem': problems_str})

    return df, new_df


def count_errors(df, column_name):
    '''
    Parameters
    ----------
    df : pandas dataframe
    column_name : name of the column in df

    Returns
    -------
    int : Sum of the cells in 'column_name' column.
    '''

    sum = 0
    for i, row in df.iterrows():
        n = int(df[column_name][i])
        sum += n
    return sum

#testing
for file_name in ['alicante-salinity.log', 'alicante-consumption.log', 'braila-anomaly.log', 'braila-consumption.log', 'braila-leakage.log', 'braila-state-analysis.log', 'carouge.log']:
    example_file = os.path.join(os.getcwd(), 'logs', file_name)
    df = to_df(example_file)
    df = find_problems(df)
    df = analyse_df(df)
    print(df.head(50))
    df = correct_type(df)
    print(df[1].head(50))
try:
    for file_name in ['alicante-consumption.log', 'alicante-salinity.log', 'braila-anomaly.log', 'braila-consumption.log', 'braila-leakage.log', 'braila-state-analysis.log', 'carouge.log']:
        example_file = os.path.join(os.getcwd(), 'logs', file_name)
        df = to_df(example_file)
        df = find_problems(df)
        df = analyse_df(df)
        df = correct_type(df)
except Exception as e:
    LOGGER.error("Exception while opening file %s: %s", file_name, str(e))


#create and send a report via email

def create_msg_tables():
    '''
    Parameters
    ----------
    None

    Returns
    -------
    str: A message ready to be sent in an email written as html. Includes tables with reportes of errors and warnings for each .log file in 'logs' folder.
    '''

    msg = ''
    for filename in os.listdir('logs'):
        file = os.path.join('logs', filename)
        df = to_df(file)
        df = find_problems(df)
        df = analyse_df(df)
        df = correct_type(df)[1]

        file_name = filename.strip('.log').upper()
        table = df.to_html(index=False, justify='center')
        if len(df) == 0:
            partial_report = f'<p><b>{file_name}:</b> <br> No errors...</p>'
        else:
            partial_report = f'<p><b>{file_name}:</b> <br> {table}</p>'
        msg += partial_report

    html = '''\
    <html>
        <head></head>
        <body>
            <p>...Report...<br>
                {msg}
            </p>
        </body>
    </html>
    '''.format(msg = msg)
    return html


def create_table(filename):
    '''
    Parameters
    ----------
    str: name of .log file

    Returns
    -------
    str: HTML table presenting errors for given .log file
    '''

    file = os.path.join('logs', filename)
    df = to_df(file)
    df = find_problems(df)
    df = analyse_df(df)
    df = correct_type(df)[1]
    if len(df) == 0:
        return None

    problems = ''
    for i,row in df.iterrows():
        current_row = '''
        <tr>
            <td> {location} </td>
            <td> {error} </td>
            <td> {warning} </td>
            <td> {problem} </td>
        </tr>
        '''.format(location = row['Location'], error = row['Error'], warning = row['Warning'], problem = row['Problem'])
        problems += current_row
    
    table = '''
    <table>
        <tr>
            <th> Location </th>
            <th> Error </th>
            <th> Warning </th>
            <th> Problem </th>
        </tr>
        {problems}
    </table>
    '''.format(problems = problems)
    
    return table


def create_msg():
    '''
    Parameters
    ----------
    None

    Returns
    -------
    str: A message ready to be sent in an email written as html. Includes number of errors and warnings for each .log file in 'logs' folder.
    '''

    # get data from scheduler.json
    config_file = os.path.join(os.getcwd(), 'configs', 'scheduler.json')
    with open(config_file, "r") as json_file:
        data = json.load(json_file)

    msg = ''
    for filename in os.listdir('logs'):
        file = os.path.join('logs', filename)
        df = to_df(file)
        df = find_problems(df)
        df = analyse_df(df)
        df = correct_type(df)[1]

        file_name = filename.strip('.log').upper()
        num_errors = count_errors(df, 'Error')
        num_warnings = count_errors(df, 'Warning')

        # get time of last update, if not foun->update_time="???"
        update_time = "???"
        for section in data["tasks"]:
            if section["name"].upper() == file_name:
                update_time = section["last_update"]

        # all errors
        if len(df) == 0:
            partial_report = f'<p><b>{file_name} ({update_time}):</b> <br> No errors...</p>'

        else:
            if num_errors == 0:
                partial_report = f'<p><b>{file_name} ({update_time}):</b> <br> {num_warnings} warnings...</p>'
            if num_warnings == 0:
                partial_report = f'<p><b>{file_name} ({update_time}):</b> <br> {num_errors} errors...</p>'
            else:
                partial_report = f'<p><b>{file_name} ({update_time}):</b> <br> {num_errors} errors and {num_warnings} warnings...</p>'
            
            # new line
            partial_report += '<br> --> '

            # errors for which action type
            dict = {}
            for i,row in df.iterrows():
                if row["Action"] not in dict:
                    dict[row["Action"]] = row["Error"]+row["Warning"]
                else:
                    dict[row["Action"]] += (row["Error"]+row["Warning"])

            for key in dict.keys():
                partial_report += f'{key}: {dict[key]}, '

            partial_report = partial_report[:-2]

            # add html table
            table_part = '''
            <br>
            {table}
            '''.format(table = create_table(filename))
            partial_report += table_part

        msg += partial_report

    html = '''\
    <html>
        <head></head>
        <body>
            <p>...Report...<br>
                {msg}
            </p>
        </body>
    </html>
    '''.format(msg = msg)
    return html


def create_attachments():
    '''
    Parameters
    ----------
    None

    Returns
    -------
    list: For each file in 'logs' folder a new excel file is created and a list of filenames of all those excel files is returned.
    '''

    attachments = []
    for filename in os.listdir('logs'):
        file = os.path.join('logs', filename)
        df = to_df(file)
        df = find_problems(df)
        df = analyse_df(df)
        df = correct_type(df)[1]
        if len(df) != 0:
            file_name = filename.strip('.log') + '.xlsx'
            df.to_excel(file_name)
            attachments.append(file_name)
    return attachments


def main(sender_address, receiver_address, password):
    '''
    Parameters
    ----------
    sender_address: Email address from which the email report is sent \n
    receiver_address: Email address of the receiver \n
    password: Password of the sender_address. '2-Step Verification': Go to the Google account (https://myaccount.google.com/), click 'Security' and then enable '2-Step Verification'. After that go to back to 'App Passwords' and follow the instructions to create a new password (you will get a 16-character code). This is the required password.

    Returns
    -------
    None
    '''

    msg = create_msg()
    attachments = create_attachments()
    yag = yagmail.SMTP(sender_address, password)
    yag.send(
        to = receiver_address,
        subject = "Report",
        contents = msg,
        attachments = attachments,
    )
    for filename in attachments:
        os.remove(filename)


# run main()
# email info

with open(os.path.join(os.getcwd(), "configs", "config_mail.json"), "r") as infile:
    data = json.load(infile)
    sender_address = data["sender_address"]
    receiver_address = data["receiver_address"]
    password = data["password"]

main(sender_address, receiver_address, password)