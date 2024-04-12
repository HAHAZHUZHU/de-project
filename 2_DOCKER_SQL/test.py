import argparse, os, sys
from time import time
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    tb = params.tb
    url = params.url

    # Get the name of the file from the URL
    file_name = url.split('/')[-1].strip()
    print(f'Downloading {file_name} ...')



    # Create SQL Alchemy engine
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    # test the connection
    # print(engine.connect())

    # Load the parquet file or CSV file
    if file_name.endswith('.parquet'):
        # Download the file fron the URL
        os.system(f'curl {url.strip()} -o {file_name}')

        file = pq.ParquetFile(file_name)
        df = next(file.iter_batches(batch_size=10)).to_pandas()
        df_iter = file.iter_batches(batch_size=100000)
    else:
        # Download the file fron the URL
        os.system(f'curl {url.strip()} -OL {file_name}')

        df = pd.read_csv(file_name, nrows=10)
        df_iter = pd.read_csv(file_name, chunksize=100000)
    
    # Create the table in the database
    df.head(0).to_sql(tb, engine, if_exists='replace')
    print(df.head(5))

    # Load the data to the database
    # start = time()
    # batch_num = 0
    # for batch in df_iter:
    #     batch_num += 1
    #     print(f'Loading batch {batch_num} ...')
    #     if file_name.endswith('.parquet'):
    #         batch_df = batch.to_pandas()
    #     else:
    #         batch_df = batch

    #     b_start = time()
    #     batch_df.to_sql(tb, engine, if_exists='append')
    #     b_end = time()

    #     print(f'inserted! time taken {b_end-b_start:10.3f} seconds.\n')
    
    # end = time()
    # print(f'All data loaded! Time taken: {end-start:10.3f} seconds. We have loaded {batch_num} batches.')





    


if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser(description='Load parquet file to a Postgres database')

    parser.add_argument('--user', type=str, help='User name to connect to the database')
    parser.add_argument('--password', type=str, help='Password to connect to the database')
    parser.add_argument('--host', type=str, help='Host of the database')
    parser.add_argument('--port', type=str, help='Port of the database')
    parser.add_argument('--db', type=str, help='Database name')
    parser.add_argument('--tb', type=str, help='Table name')
    parser.add_argument('--url', type=str, help='URL for the Parquet file to load')

    args = parser.parse_args()
    main(args)