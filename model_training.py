from SpamClassifier import NBC
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

model = NBC()
df = pd.read_csv('spam.csv')
encoder = LabelEncoder()
X = df.Message
y = encoder.fit_transform(df.Category)

model.load_options()
print(model.score(X, y))



