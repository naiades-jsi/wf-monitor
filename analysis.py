# Python module imports
import argparse
import json
import sys
import time
import logging
import os
import pandas as pd

def to_df(infile):
    '''converts log file to pandas dataframe'''
    time = []
    file_loc = []
    type = []
    message = []
    
    with open(infile) as f:
        for line in f:
            if len(line)!=0:
                #2022-08-30 15:52:17,689 src.workflow INFO     Loading config: configs/alicante-consumption.json

                no_time = line.split(',',1)
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
    '''returns new dataframe presenting errors and warnings'''
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
                action.append(checking.split(' ')[2])

            else: #df['file_loc'][index] == 'src.kafka'
                checking_index = index-3
                checking = df['Message'][checking_index].split(':',1)[1].strip()
                location.append(checking.split(' ')[-1])
                action.append(checking.split(' ')[0])
            
    new_df = pd.DataFrame(data={'Time': time, 'Type': type, 'Action': action, 'Location': location, 'Problem': problem})
    return new_df

example_file = os.path.join(os.getcwd(),'logs', "alicante-consumption.log")
df = to_df(example_file)
print(find_problems(df).head(50))