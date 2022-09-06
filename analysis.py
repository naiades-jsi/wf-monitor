# Python module imports
import argparse
import json
import sys
import time
import logging
import os
import pandas as pd
import logging

# logging
LOGGER = logging.getLogger("wf-monitor")
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level=logging.INFO)

def to_df(infile):
    '''
    Parameters
    ----------
    infile : {string}  Absolute name of the log file.

    Returns
    -------
    df : pandas dataframe (keeping all the data from the infile)
    '''

    time = []               # array of ...
    file_loc = []
    type = []
    message = []

    with open(infile) as f:
        for line in f:
            # parsing log lines; only if length is bigger than 0
            if len(line) != 0:


                #2022-08-30 15:52:17,689 src.workflow INFO     Loading config: configs/alicante-consumption.json
                no_time = line.split(',', 1)
                time.append(no_time[0])
                no_time_str = no_time[1].strip()
                #689 src.workflow INFO     Loading config: configs/alicante-consumption.json

                no_index = no_time_str.split(' ',1)
                no_index_str = no_index[1].strip()
                #src.workflow INFO     Loading config: configs/alicante-consumption.json

                no_file_loc = no_index_str.split(' ',1)
                file_loc.append(no_file_loc[0])
                no_file_loc_str = no_file_loc[1].strip()
                #INFO     Loading config: configs/alicante-consumption.json

                no_type = no_file_loc_str.split(' ',1)
                type.append(no_type[0])
                no_type_str = no_type[1]
                #Loading config: configs/alicante-consumption.json

                message.append(no_type_str)

    df = pd.DataFrame(data={'Time':time, 'File_loc': file_loc, 'Type':type, 'Message': message})
    return df


def find_problems(df):
    '''
    Parameters
    ----------
    df : pandas dataframe

    Returns
    -------
    df : pandas dataframe
    Copy of the original df, but only the rows where 'ERROR' or 'WARNING' occurred
    "Message" column translated to "Column" column
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
                checking_index = index-2
                checking = df['Message'][checking_index].split(':',1)[1].strip()
                location.append(checking.split(' ')[0])
                action.append(checking.split(' ')[1])

            elif df['File_loc'][index] == 'src.influx':
                checking_index = index-3
                checking = df['Message'][checking_index].split(':',1)[1].strip()
                location.append(checking.split(' ')[1])
                action.append(checking.split(' ')[0] + ' ' + checking.split(' ')[2])

            else: #df['file_loc'][index] == 'src.kafka'
                checking_index = index-3
                checking = df['Message'][checking_index].split(':',1)[1].strip()
                location.append(checking.split(' ')[-1])
                action.append(checking.split(' ')[0])

    new_df = pd.DataFrame(data={'Time': time, 'Type': type, 'Action': action, 'Location': location, 'Problem': problem})
    return new_df

def extract_time(df,i):
    '''
    Parameters
    ----------
    df : pandas dataframe
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


def previous_time(df,i):
    '''
    Parameters
    ----------
    df : pandas dataframe \n
    i: index of the row

    Returns
    -------
    float: Time_spent value from the last row with the same location and action previous to the current one
    (API --> Influx --> Fusion --> Prediction)
    '''
    action = df['Action'][i]
    location = df['Location'][i]
    if action == 'Flow':
        return 0
    elif action == 'Influx Flow':
        index = i-1
        while index>0:
            if df['Action'][index] == 'Flow' and df['Location'][index] == location:
                return extract_time(df, index)
            index -= 1
    elif action == 'Fusion':
        index = i-1
        while index>0:
            if df['Action'][index] == 'Influx Flow' and df['Location'][index] == location:
                return extract_time(df, index)
            index -= 1
    else: # action == 'Prediction
        index = i-1
        while index>0:
            if df['Action'][index] == 'Fusion' and df['Location'][index] == location:
                return extract_time(df, index)
            index -= 1

    return 0 #error?

def analyse_df(df):
    '''
    Parameters
    ----------
    df : pandas dataframe

    Returns
    -------
    df : pandas datafram \n
    Copy of the original df but with an added column (calculated time spent for a task) \n
    new_df : pandas dataframe \n
    Presents error and warning counts for each location
    '''

    time_spent = []
    for index in range(len(df)):
        time_1 = extract_time(df,index)
        time_2 = previous_time(df,index)
        time = time_1-time_2

        time_spent.append(time)
    df['Time_spent'] = time_spent

    location = []
    warning_count = []
    error_count = []
    for i in range(len(df)):
        current_location = df['Location'][i]
        current_type = df['Type'][i]
        if current_location in location:
            j = location.index(current_location)
            if current_type == 'ERROR':
                error_count[j]+=1
            else: #current_type == 'WARNING':
                warning_count[j]+=1
        else:
            location.append(current_location)
            if current_type == 'ERROR':
                error_count.append(1)
                warning_count.append(0)
            else: #current_type == 'WARNING':
                error_count.append(0)
                warning_count.append(1)
    new_df = pd.DataFrame(data={'Location': location, 'Error_count': error_count, 'Warning_count': warning_count})

    return df, new_df

def correct_type(df):
    '''
    Parameters
    ----------
    df : pandas dataframe

    Returns
    -------
    df : pandas dataframe \n
    Same df with corrected "Type" column (if WARNING or ERROR don't look like a problem anymore)
    '''
    for i, row in df.iterrows():
        if df['Action'][i] != 'Flow':
            time = df['Time_spent'][i]
            if time < -1 or time > 1:
                df['Type'][i] = 'ERROR'
            else:
                df['Type'][i] = 'INFO'
    return df



example_file = os.path.join(os.getcwd(), 'logs', "alicante-consumption.log")
df = to_df(example_file)
df = find_problems(df)
df = analyse_df(df)[0]
df = correct_type(df)
print(df.head(50))
#testing
try:
    example_file = os.path.join(os.getcwd(), 'logs', "alicante-consumption.log")
    df = to_df(example_file)
    df = find_problems(df)
    df = analyse_df(df)[0]
except Exception as e:
    LOGGER.error("Exception while opening file %s: %s", example_file, str(e))