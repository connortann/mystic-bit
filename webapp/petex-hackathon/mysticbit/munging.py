""" Code to load and prep data """

import pandas as pd


def load_log_data():
    """ Return pandas dataframe of log data """
    df = (pd.read_csv('../data/HACKA_DS.csv', sep=';')
          .rename(columns=lambda x: x.strip())
          )
    return df


def create_ml_dataframe(df, feature_cols=['GR'], feature_lags=range(0, 50, 2),
                        label_cols=['GR'], label_lags=[2, 4, 6, 8, 10], dropna=True):
    """ Create dataframe with 'features' and 'labels', from the raw log dataframe """

    cols_to_keep = list(set(['TVDSS', 'HACKANAME', 'RES_ID'] + feature_cols + label_cols))

    # Resample at 1m
    # TODO: resampling that handles RESID
    df_ml = df.copy()
    df_ml = (df_ml[cols_to_keep]
             .astype({"TVDSS": int})
             .groupby(['HACKANAME', 'TVDSS'])
             .mean())

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
              .assign(TVDSS=lambda x: x['TVDSS_bit_depth'] + x['offset'])
              )
    return result
