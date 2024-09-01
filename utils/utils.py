import datetime
import sqlite3
import configparser
from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()


def obtiene_db_path():
    config = configparser.ConfigParser()
    db_path = ""

    try:
        config.read("config.ini")
        db_path = config.get("database", "path")
    except configparser.NoSectionError as e:
        print("No se pudo leer el archivo de configuracion")
    except configparser.NoOptionError as e:
        print(
            "No se pudo leer el archivo de configuracion porque no existe la opcion Path"
        )
    except FileNotFoundError as e:
        print("No se pudo leer el archivo de configuracion porque no existe")
    except Exception as e:
        print("Error desconocido", e)

    finally:
        return db_path


def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def connect_servicetonic_demo_database():
    server = os.environ.get("SERVICETONIC_DEMO_SERVER")
    database = os.environ.get("SERVICETONIC_DEMO_DATABASE")
    username = os.environ.get("SERVICETONIC_DEMO_USERNAME")
    password = os.environ.get("SERVICETONIC_DEMO_PASSWORD")

    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    return cnxn
