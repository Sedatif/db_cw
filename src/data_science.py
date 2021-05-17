import pandas as pd
import numpy as np
from scipy.stats import stats
from sklearn.linear_model import LinearRegression

def load_data_frame(db):
    smartphones = list(db.find())
    names = all_props('name', smartphones)
    unique = unique_name_indexes(names)
    cpus = all_props('cpu_frequency', smartphones)[unique]
    rams = all_props('ram', smartphones)[unique]
    memories = all_props('memory', smartphones)[unique]
    cameras = all_props('camera', smartphones)[unique]
    diagonals = all_props('diagonal', smartphones)[unique]
    batteries = all_props('battery', smartphones)[unique]
    prices = all_props('price', smartphones)[unique]
    df = pd.DataFrame({
        'name': names[unique], 'cpu_frequency': cpus, 'ram': rams, 'battery': batteries,
        'memory': memories, 'camera': cameras, 'diagonal': diagonals, 'price': prices
    })
    df = remove_odd_values(df, 'cpu_frequency')
    df = remove_odd_values(df, 'ram')
    df = remove_odd_values(df, 'memory')
    df = remove_odd_values(df, 'camera')
    df = remove_odd_values(df, 'diagonal')
    df = remove_odd_values(df, 'battery')
    df = remove_odd_values(df, 'price')
    return df

def remove_odd_values(df, prop_name):
    std_dev = 3
    z_scores = stats.zscore(df.loc[:, prop_name])
    return df[np.abs(z_scores) < std_dev]

def unique_name_indexes(names):
    short_names = [x.split(')')[0].split('(')[-1].strip() for x in names]
    _, indexes = np.unique(short_names, return_index=True)
    return indexes

def all_props(prop_name, smartphones):
    return np.array([x[prop_name] for x in smartphones])

def linear_model(x, y):
    model = LinearRegression()
    model.fit(x, y)
    return model