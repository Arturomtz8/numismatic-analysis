import io
import os
import re

import pandas as pd
from google.cloud import storage


def read_csv_from_gcs(bucket_name, source_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    data = blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(data))

    return df


def parse_title(title):
    country = re.split(r"\sBillete\s", title)[0].strip()
    print(country)

    # value_match = re.search(
    #     r'(\d[\d.,]*)\s([A-Za-zÁ-Úá-ú]+)\s\d{4}',
    #     title.split(' Billete ')[1] if 'Billete' in title else title
    # )

    # if value_match:
    #     # Clean the number (remove thousand separators)
    #     amount = value_match.group(1).replace('.', '').replace(',', '')
    #     currency = value_match.group(2)
    #     value = f"{amount} {currency}"
    # else:
    #     amount, currency, value = None, None, None

    # year_match = re.search(r'(\d{4})', title)
    # year = year_match.group(1) if year_match else None

    # if year:
    #     series = title.split(year, 1)[1].strip(' ,-')
    # else:
    #     series = None

    # return pd.Series({
    #     'country': country,
    #     'amount': amount,
    #     'currency': currency,
    #     'value': value,
    #     'year': year,
    #     'series': series
    # })


if __name__ == "__main__":
    BUCKET_NAME = os.getenv("NUMISMATIC_BUCKET")
    SOURCE_BLOB_NAME = os.getenv("NUMISMATIC_RAW")
    df = read_csv_from_gcs(BUCKET_NAME, SOURCE_BLOB_NAME)
    df["title"].apply(parse_title)

    # df[['country', 'amount', 'currency', 'value', 'year', 'series']] =
    # print(df)
