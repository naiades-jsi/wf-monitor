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

def extract_time(df,i):
    problem = df['Problem'][i]
    if 'Timestamp bigger' in problem:
        time = problem.split(':')[1].strip()
        time = float(time[:-1])
        return time
    return None

#def analyse_df(df):
#    '''1) adds a column (calculate time spent for a task)  and returns this dataframe
#    2) returns additional df with locations and error counts'''
#    time_spent = []
#    for index in range(len(df)):
#        time_1 = extract_time(df,index)
#        time = time_1
#        if index!=0 and time_1:
#            #find previous (warning/error) note from the same location
#            location = df['Location'][index]
#            j=index-1
#            current_location = df['Location'][j]
#            while j>0 and location!=current_location:
#                j-=1
#                current_location = df['Location'][j]
#
#            #calculate difference between the times
#            if current_location==location:
#                time_2 = extract_time(df,j)
#                if time_2:
#                    time = time_1-time_2
#            else:
#                time = time_1
#        time_spent.append(time)
#    df['Time_spent'] = time_spent
#
#    location = []
#    warning_count = []
#    error_count = []
#    for i in range(len(df)):
#        current_location = df['Location'][i]
#        current_type = df['Type'][i]
#        if current_location in location:
#            j = location.index(current_location)
#            if current_type == 'ERROR':
#                error_count[j]+=1
#            else: #current_type == 'WARNING':
#                warning_count[j]+=1
#        else:
#            location.append(current_location)
#            if current_type == 'ERROR':
#                error_count.append(1)
#                warning_count.append(0)
#            else: #current_type == 'WARNING':
#                error_count.append(0)
#                warning_count.append(1)
#    new_df = pd.DataFrame(data={'Location': location, 'Error_count': error_count, 'Warning_count': warning_count})
#
#    return df, new_df



def one_location(df,location):
    for i in range(len(df)):
        if location not in df['Location'][i]:
            df = df.drop([i])
    return df

def analyse_df(df):
    '''1) adds a column (calculate time spent for a task)  and returns this dataframe
    2) returns additional df with locations and error counts'''
    time_spent = []
    for index in range(len(df)):
        time_1 = extract_time(df,index)
        time = time_1

        #find out if there is previous problem and calculate the difference in times
        current_location = df['Location'][index]
        current_location_df = one_location(df,current_location)
        time_2 = time_1
        is_different = False
        for i in range(len(current_location_df)):
            current_time = extract_time(current_location_df,i)
            if current_time:
                if current_time < time_1 and current_time > time_2:
                    is_different = True
                    time_2 = current_time
        if is_different:
            time = time_1-time_2
        
        #if index!=0 and time_1:
        #    #find previous (warning/error) note from the same location
        #    location = df['Location'][index]
        #    j=index-1
        #    current_location = df['Location'][j]
        #    while j>0 and location!=current_location:
        #        j-=1
        #        current_location = df['Location'][j]
#
        #    #calculate difference between the times
        #    if current_location==location:
        #        time_2 = extract_time(df,j)
        #        if time_2:
        #            time = time_1-time_2
        #    else:
        #        time = time_1
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



#testing
example_file = os.path.join(os.getcwd(),'logs', "alicante-consumption.log")
df = to_df(example_file)
df = find_problems(df)
#df = analyse_df(df)[0]
#print(analyse_df(df)[0].head(42))
print(df.head(40))