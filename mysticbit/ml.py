""" Core ML functions"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import LeavePGroupsOut


def train_test_split(df_ml):
    """ Split log data into train and test by well ID """

    test_wells = set(['B03', 'B05', 'B06'])
    train_wells = set(df_ml.HACKANAME.unique()) - test_wells
    print('Train well: ', train_wells)
    print('Test wells: ', test_wells)

    mask_train = df_ml.HACKANAME.isin(train_wells)
    df_ml_train = df_ml[mask_train]
    df_ml_test = df_ml[~mask_train]

    return df_ml_train, df_ml_test


def make_model(X_train, y_train):
    """ Returns a trained model"""
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    return model


def make_predictions(model, df_ml, y_col='GR_futr_5', X_cols = ['GR', 'GR_lag_1']):
    """ Use trained model to make predictions, add on to df_ml as new column"""
    X = df_ml[X_cols]
    y_pred = model.predict(X)
    df_ml[y_col+'_pred'] = y_pred
    return df_ml
