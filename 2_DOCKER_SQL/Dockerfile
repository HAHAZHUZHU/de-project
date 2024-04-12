FROM python:3.9.1

RUN pip install pandas sqlalchemy psycopg2 pyarrow

WORKDIR /app
COPY data-loading-parquet.py data-loading-parquet.py

ENTRYPOINT ["python", "data-loading-parquet.py"]