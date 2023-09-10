from sklearn import preprocessing
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from uber_movement import data_extraction




data_madrid = data_extraction.extraction_pipeline()

df = pd.get_dummies(data_madrid, drop_first=True, columns=['hod', 'postcode_dest', 'postcode_source'], dtype=float)
df.head()

def feature_standarization(input_df: pd.DataFrame) -> pd.DataFrame:
    pass



X = df.drop(["mean_travel_time"], axis = 1).values
y = df[['mean_travel_time']].values


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()

scaling = scaler.fit(X_train)
X_scaled = scaler.transform(X_train)
