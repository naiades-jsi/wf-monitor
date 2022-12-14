from influxdb_client import InfluxDBClient
import pandas as pd
from urllib3 import Retry
import logging

# logging
LOGGER = logging.getLogger(__name__)

class QueryFromDB():
    """Querying data for DataFusion"""
    # defined functions to crated useful queries
    # TODO: test if all queries work

    def __init__(self, token: str='', url: str='', organisation: str='', bucket: str=''):
        self.token = token
        self.url = url
        self.organisation = organisation
        self.bucket = bucket
        self.retries = Retry(total=10, connect=5, read=2, redirect=5)
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.organisation, retries=self.retries)

    def query(self, query: str = ''):
        #query = f'from(bucket: \\"{self.bucket}\\") |> range(start: -1h)'
        tables = self.client.query_api().query(query, org=self.organisation)
        return tables

    def query_df(self, query:str):
        # DataFrames
        #print(query) # TODO remove print

        #Error here - cannot query empty range
        df = self.client.query_api().query_data_frame(query)
        if isinstance(df, pd.DataFrame):
            pass
        else:
            # if list of DataFrames concatenate
            df = pd.concat(df)
            pass
        #df = df.sort_values(by='_time').reset_index(drop=True)
        return df

    def bucket_query(self, query: str = ''):
        query = query + f'from(bucket: "{self.bucket}")'
        return query

    def time_query(self, query: str = '', start_time = '-1h', stop_time = '-0h'):
        query = query + f'|> range(start:{start_time}, stop:{stop_time})'
        return query

    def group(self, query: str = ''):
        # TODO
        query = query + '|> group(columns:["_field"])'
        return query

    def filter_query(self, query: str = '', measurement: str = None, fields:list = None, tags:dict = {None:None}):

        # TODO may need some improvementst (check)

        filter_q = '|> filter(fn: (r) => '
        if measurement != None:
            filter_q = filter_q + f'r._measurement == "{measurement}"'

        if fields != None:
            if measurement != None:
                filter_q = filter_q + ' and ('
            iter = False
            for field in fields:
                if iter:
                    filter_q = filter_q + ' or '
                filter_q = filter_q + f'r._field == "{field}"'
                iter = True
            filter_q = filter_q + ')'

        iter = False
        for key, value in tags.items():
            if key != None:
                if (measurement != None or fields != None) & (iter == False):
                    filter_q = filter_q + ' and ('
                if iter:
                    filter_q = filter_q + ' and ('

                if isinstance(value, list):
                    iter2 = False
                    for val in value:
                        if iter2:
                            filter_q = filter_q + ' or '

                        filter_q = filter_q + f'r.{key} == "{val}"'
                        iter2 = True
                    filter_q = filter_q + ')'
                else:
                    filter_q = filter_q + f'r.{key} == "{value}"'
                iter = True
        filter_q = filter_q + ')'

        query = query + filter_q
        return query

    def filter_last(self, query: str = ''):
        query = query + '|> last()'
        return query

    def sort(self, query:str = ''):
        query = query + '|> sort(columns: ["_time"])'
        return query

    def yi(self, query: str = ''):
        query = query + '|> yield()'
        return query

    def window(self, query: str = '', every:str = '5m', period:str = '5m', offset = '0m', createEmpty:str= 'true'):
        query = query + f'|> window(every: {every}, period: {period}, offset: {offset}, createEmpty: {createEmpty})'
        return query

    def duplicate(self, query: str = '', column:str = "_stop", to:str = "_time"):
        query = query + f'|> duplicate(column: "{column}", as: "{to}")'
        return query

    def agregate(self, query: str = '', agr:str = 'mean', every:str = '5m', period:str = '5m', offset:str='0m', timeSrc:str="_stop", timeDst:str="_time", createEmpty:str= 'true' ):
        if (offset == '0m') and (every == period):
            query = query + f'|> aggregateWindow(every: {every}, fn: {agr}, timeSrc: "{timeSrc}", timeDst: "{timeDst}", createEmpty: {createEmpty} )'
        else:
            query = self.window(query, every, period, offset, createEmpty)
            query = query + f'|> {agr}()'
            query = self.duplicate(query, timeSrc, timeDst)

        return query

    def shift_time(self, query: str = '', shift = '0m'):
        query = query + f'|> timeShift(duration: {shift})'

        return query