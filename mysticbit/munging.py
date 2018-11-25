""" Code to load and prep data """

import pandas as pd
import numpy as np
import os

def load_log_data():
    """ Return pandas dataframe of log data """
    csv_path = os.path.join(os.path.dirname(__file__), '../data/HACKA_DS.csv')
    df = (pd.read_csv(csv_path, sep=';')
          .rename(columns=lambda x: x.strip())
          )
    return df


def resample_well(df_well, feature_cols, sample_step):
    """ Resamples and interpolates data in a single well. """

    # Resample
    df_well = df_well.copy()
    df_well = df_well.set_index('TVDSS')
    new_index = np.arange(int(df_well.index.min()), df_well.index.max(), sample_step)
    df_well = df_well.reindex(new_index, method='nearest', tolerance=sample_step)

    # Interpolate
    #for col in feature_cols:
    #    df_well[col] = df_well[col].interpolate(method='index', limit=5, limit_area='inside')

    df_well.interpolate(method='index', limit=5, limit_area='inside', inplace=True)

    # Fill in nans
    for col in ['HACKANAME', 'RES_ID']:
        df_well[col] = df_well[col].fillna(method='bfill').fillna(method='ffill')

    return df_well.reset_index()


def create_ml_dataframe(df, feature_cols=['GR'], feature_lags=range(0, 50, 2),
                        label_cols=['GR'], label_lags=[2, 4, 6, 8, 10], dropna=True,
                        sample_step=0.2):
    """ Create dataframe with 'features' and 'labels', from the raw log dataframe """

    # Drop unused columns
    cols_to_keep = list(set(['TVDSS', 'HACKANAME', 'RES_ID'] + feature_cols + label_cols))
    df_ml = df[cols_to_keep].copy()

    # Process each well in turn on TVDSS index
    df_ml = (df_ml.groupby('HACKANAME')
             .apply(resample_well, feature_cols, sample_step)
             .reset_index(drop=True))

    # Feature lagging (above the current bit depth)
    for col in feature_cols:
        for lag in feature_lags:
            kwargs = {col + '_lag_' + str(lag): lambda x: x.groupby('HACKANAME')[col].shift(lag)}
            df_ml = df_ml.assign(**kwargs)

    # Label lagging (below the current bit depth)
    for col in label_cols:
        for lag in label_lags:
            kwargs = {col + '_futr_' + str(lag): lambda x: x.groupby('HACKANAME')[col].shift(-lag)}
            df_ml = df_ml.assign(**kwargs)

    if dropna:
        df_ml = df_ml.dropna()

    return df_ml


def get_log_predictions(df_pred, well_name, bit_depth, tol=1):
    """ Lookup predictions indexed by depth """

    prediction_col_names = [c for c in df_pred if 'pred' in c]


    pred_row = df_pred[(df_pred.HACKANAME == well_name) &
                       (df_pred.TVDSS > bit_depth - tol) &
                       (df_pred.TVDSS < bit_depth + tol)
                       ]

    assert len(pred_row) > 0, 'No predictions found for that well near that depth'
    pred_row = pred_row.iloc[0:1, :]

    result = (pd.melt(pred_row,
                      id_vars=['HACKANAME', 'TVDSS'],
                      value_vars=prediction_col_names,
                      var_name='pred_col'
                      )
              .rename(columns={'TVDSS': 'TVDSS_bit_depth'})
              .assign(offset=lambda x: x['pred_col'].str.extract('(\d+)').astype('float'))
              .assign(log_name=lambda x: x['pred_col'].str.split('_').str[0])
              .assign(model_name=lambda x: x['pred_col'].str.split('_').str[-1])
              .assign(TVDSS=lambda x: x['TVDSS_bit_depth'] + x['offset'])
              )
    return result
