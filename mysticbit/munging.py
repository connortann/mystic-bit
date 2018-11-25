""" Code to load and prep data """

import pandas as pd
import numpy as np

def load_log_data():
    """ Return pandas dataframe of log data """
    df = (pd.read_csv('../data/HACKA_DS.csv', sep=';')
          .rename(columns=lambda x: x.strip())
          )
    return df


def create_ml_dataframe(df, feature_cols=['GR'], feature_lags=range(0, 50, 2),
                        label_cols=['GR'], label_lags=[2, 4, 6, 8, 10], dropna=True,
                        sample_step=0.2):
    """ Create dataframe with 'features' and 'labels', from the raw log dataframe """

    # Drop unused columns
    cols_to_keep = list(set(['TVDSS', 'HACKANAME', 'RES_ID'] + feature_cols + label_cols))
    df = df[cols_to_keep].copy()

    # Process each well in turn
    df = df.set_index('TVDSS')
    resampled_dfs = []

    for well in df['HACKANAME'].unique():
        # Resample
        df_well = df[df['HACKANAME'] == well].set_index('TVDSS')
        new_index = np.arange(int(df_well.index.min()), df_well.index.max(), sample_step)
        df_well = df_well.reindex(new_index, method='nearest', tolerance=sample_step)

        # Interpolate
        for col in feature_cols:
            df_well[col] = df_well[col].interpolate(method='index', limit=6, limit_area='inside')

        resampled_dfs.append(df_well)

    df_ml = pd.concat(resampled_dfs, axis=0).reset_index()
    print(df_ml.head())

    # Feature lagging (above the current bit depth)
    for col in feature_cols:
        for lag in feature_lags:
            kwargs = {col + '_lag_' + str(lag): lambda x: x[col].groupby('HACKANAME').shift(lag)}
            df_ml = df_ml.assign(**kwargs)

    # Label lagging (below the current bit depth)
    for col in label_cols:
        for lag in label_lags:
            kwargs = {col + '_futr_' + str(lag): lambda x: x[col].groupby('HACKANAME').shift(-lag)}
            df_ml = df_ml.assign(**kwargs)

    if dropna:
        df_ml = df_ml.dropna()


    return df_ml.reset_index()


def get_log_predictions(df_pred, well_name, bit_depth):
    """ Lookup predictions indexed by depth """

    prediction_col_names = [c for c in df_pred if 'pred' in c]

    pred_row = df_pred[(df_pred.HACKANAME == well_name) &
                       (df_pred.TVDSS == bit_depth)]

    assert len(pred_row) == 1, 'No predictions found for that well at that depth'

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
