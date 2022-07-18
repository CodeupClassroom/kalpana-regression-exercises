import pandas as pd
import os
from env import user, password, host

def get_db_url(database):
    return f'mysql+pymysql://{user}:{password}@{host}/{database}'

"""
USAGE: 
Use `from wrangle import wrangle_zillow` at the top of your notebook.
This 

"""
def get_zillow_data():
    """Seeks to read the cached zillow.csv first """
    filename = "zillow.csv"

    if os.path.isfile(filename):
        return pd.read_csv(filename)
    else:
        return get_new_zillow_data()

def get_new_zillow_data():
    """Returns a dataframe of all 2017 properties that are Single Family Residential"""

    sql = """
    select 
    bedroomcnt, bathroomcnt, calculatedfinishedsquarefeet, taxvaluedollarcnt, yearbuilt, taxamount, fips
    from properties_2017
    join propertylandusetype using (propertylandusetypeid)
    where propertylandusedesc = "Single Family Residential"
    """
    return pd.read_sql(sql, get_db_url("zillow"))


def handle_nulls(df):    
    # We keep 99.41% of the data after dropping nulls
    # round(df.dropna().shape[0] / df.shape[0], 4) returned .9941
    df = df.dropna()
    return df


def optimize_types(df):
    # Convert some columns to integers
    # fips, yearbuilt, and bedrooms can be integers
    df["fips"] = df["fips"].astype(int)
    df["yearbuilt"] = df["yearbuilt"].astype(int)
    df["bedroomcnt"] = df["bedroomcnt"].astype(int)    
    df["taxvaluedollarcnt"] = df["taxvaluedollarcnt"].astype(int)
    df["calculatedfinishedsquarefeet"] = df["calculatedfinishedsquarefeet"].astype(int)
    return df


def handle_outliers(df):
    """Manually handle outliers that do not represent properties likely for 99% of buyers and zillow visitors"""
    df = df[df.bathroomcnt <= 6]
    
    df = df[df.bedroomcnt <= 6]

    df = df[df.taxvaluedollarcnt < 2_000_000]

    return df


def wrangle_zillow():
    """
    Acquires Zillow data
    Handles nulls
    optimizes or fixes data types
    handles outliers w/ manual logic
    returns a clean dataframe
    """
    df = get_zillow_data()

    df = handle_nulls(df)

    df = optimize_types(df)

    df = handle_outliers(df)

    df.to_csv("zillow.csv", index=False)

    return df


## TODO Encode categorical variables (and FIPS is a category so Fips to string to one-hot-encoding
## TODO Scale numeric columns
## TODO Add train/validate/test split in here
## TODO How to handle 0 bedroom, 0 bathroom homes? Drop them? How many? They're probably clerical nulls