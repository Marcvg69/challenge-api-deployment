from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
import pandas as pd 
import numpy as np
import joblib

#def modelCAT(df, target, obs, results_df=None):

# Load the dataset
file = 'data/data_cleaned.csv'  
df = pd.read_csv(file)

# transform price to logarithm
df = df.assign(price=np.log1p(df['price']))

# Split into train/test
X = df.drop(columns=['price'])
y = df['price']

"""# Selecting features and target variables
x = df.iloc[:, 2:4]  
y = df.iloc[:, 4]    """

# Splitting the dataset into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=123)

# Training the model
clf =CatBoostRegressor(verbose=0, random_state=123)
clf.fit(x_train, y_train)

# Saving the trained model
joblib.dump(clf, "model/ego_catboost.joblib")