from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
import os

@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read fhv data from web into pandas DataFrame"""
    df = pd.read_csv(dataset_url, compression='gzip')

    if color == "fhv":
        # df.rename({'dropoff_datetime':'dropOff_datetime'}, axis='columns', inplace=True)
        # df.rename({'PULocationID':'PUlocationID'}, axis='columns', inplace=True)
        # df.rename({'DOLocationID':'DOlocationID'}, axis='columns', inplace=True)
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
        df["dropOff_datetime"] = pd.to_datetime(df["dropOff_datetime"])
        df["PUlocationID"] = df["PUlocationID"].astype('Int64')
        df["DOlocationID"] = df["DOlocationID"].astype('Int64')
        df["SR_Flag"] = df["SR_Flag"].astype('Int64')
    else: 
        df["VendorID"] = df["VendorID"].astype('Int64')
        df["RatecodeID"] = df["RatecodeID"].astype('Int64')
        df["PULocationID"] = df["PULocationID"].astype('Int64')
        df["DOLocationID"] = df["DOLocationID"].astype('Int64')
        df["passenger_count"] = df["passenger_count"].astype('Int64')
        df["payment_type"] = df["payment_type"].astype('Int64')
        if color == "yellow":
            df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
            df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
        elif color == "green":
            df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
            df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
            df["trip_type"] = df["trip_type"].astype('Int64')


    return df

@task()
def write_local(color, df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    
    # create directory if not exist
    dir = f"data/{color}"
    if not os.path.isdir(dir):
        os.makedirs(dir)

    path = Path(f"{dir}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(path: Path):
    """Upload local parquet file to GCS"""
    gcp_block = GcsBucket.load("prefect-de-zoomcamp-gcs")
    gcp_block.upload_from_path(from_path=path, to_path=path, timeout=600)

@flow(log_prints=True)
def etl_web_to_gcs(color, year, month):
    """download"""
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    path = write_local(color, df, dataset_file)
    write_gcs(path)
    return path

@flow(log_prints=True)
def etl_parent_flow(color, months, year):
    for month in months:
        etl_web_to_gcs(color, year, month)

if __name__ == "__main__":
    # 1,2,3,
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    year = 2019
    color = 'fhv'
    etl_parent_flow(color, months, year)