""" Core ML functions"""

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

