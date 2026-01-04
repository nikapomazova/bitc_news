import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

data = {'size': [50, 60, 80, 100, 120, 150, 180],
        'price': [150, 180, 220, 260, 300, 360, 420]}
df = pd.DataFrame(data)

X = df[['size']] 
y = df['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

predictions = model.predict(X_test)
print("Predictions:", predictions)

plt.scatter(X, y, color='blue')
plt.plot(X, model.predict(X), color='red')
plt.xlabel('Size (m²)')
plt.ylabel('Price ($1000s)')
plt.title('House Price Prediction')
plt.show()