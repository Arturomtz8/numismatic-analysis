import os
import re

import pandas as pd

from gc_utility.read_data import read_csv_from_gcs
from gc_utility.upload_data import upload_csv_to_gcs

BUCKET_NAME = os.getenv("NUMISMATIC_BUCKET")
SOURCE_BLOB_NAME = os.getenv("NUMISMATIC_RAW")

countries = [
    "Isla Bassas de India",
    "Isla Komplece",
    "Estados Unidos",
    "Irlanda Del Norte",
    "Sudan Del Sur",
    "Corea Del Norte",
    "Indochina Francesa",
    "Republica Dominicana",
    "Cabo Verde",
    "Republica Checa",
    "Gran Bretaña",
    "Territorios Ecuatoriales",
    "Territorios Articos",
    "Venezuela",
    "Transnistria",
    "Bolivia",
    "Argentina",
    "Paraguay",
    "Perú",
    "Cuba",
    "Francia",
    "Uruguay",
    "Inglaterra",
    "Chile",
    "Estonia",
    "Mexico",
    "Turquia",
    "Guatemala",
    "Vietnam",
    "Brasil",
    "Oman",
    "Rumania",
    "Nigeria",
    "España",
    "Afganistan",
    "Ghana",
    "Grecia",
    "Suiza",
    "Georgia",
    "Libia",
    "Portugal",
    "Colombia",
    "China",
    "Tajikistan",
    "Rusia",
    "Siria",
    "Congo",
    "Croacia",
    "Alemania",
    "Arabia Saudita",
    "Yemen",
    "Africa",
    "Europa",
]


def extract_country(title):
    normalized_title = title.lower()

    if "lote de argentina" in normalized_title:
        return "Argentina"
    if "billete replica de" in normalized_title:
        for country in countries:
            if re.search(r"\b" + re.escape(country.lower()) + r"\b", normalized_title):
                return country
        return "Unknown"
    if "bono exterior bonex" in normalized_title:
        return "Argentina"
    if "bono de emergencia" in normalized_title:
        return "Argentina"
    if "bono lecop" in normalized_title:
        return "Argentina"
    if "cheque de viajero" in normalized_title:
        return "Inglaterra"
    if normalized_title == "argentina":
        return "Argentina"

    match = re.search(r"^(.*?)\s+Billete", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^(.*?)\s+Billlete", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^(.*?)\s+Set", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^(.*?)\s+Lote", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^(.*?)\s+Emergency", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"^(.*?)\s+Emergencia", title, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    for country in countries:
        pattern = (
            r"^\s*"
            + re.escape(country.lower())
            + r"\s*(?:año|set|lote|coleccion|billete|billlete|bono|moneda|\d+|$)"
        )
        if re.search(pattern, normalized_title):
            return country

    for country in countries:
        if re.search(r"\b" + re.escape(country.lower()) + r"\b", normalized_title):
            return country

    return "Unknown"


def extract_value(title):
    match = re.search(r"(\d+[\.,]?\d*\s+[A-Za-z]+)", title)
    if match:
        return match.group(1).strip()
    return "Unknown"


def extract_year(title):
    match = re.search(r"\b(\d{4})\b", title)
    if match:
        return match.group(1)
    return "Unknown"


def extract_series(title):
    match = re.search(r"\(Serie\s+([A-Za-z])\)", title)
    if match:
        return "Serie " + match.group(1)
    return "Unknown"


if __name__ == "__main__":
    df = read_csv_from_gcs(BUCKET_NAME, SOURCE_BLOB_NAME)
    df["Country"] = df["title"].apply(extract_country)
    df["Value"] = df["title"].apply(extract_value)
    df["Year"] = df["title"].apply(extract_year)
    df["Series"] = df["title"].apply(extract_series)
    df.to_csv("billetes_extracted_improved.csv", index=False)

    # path_file = "billetes_extracted_improved.csv"
    # gcs_key = os.getenv("NUMISMATIC_CLEAN")
    # upload_csv_to_gcs(BUCKET_NAME, path_file, gcs_key)
