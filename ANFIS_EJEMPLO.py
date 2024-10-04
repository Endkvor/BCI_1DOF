
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from skfuzzy import control as ctrl
from sklearn.metrics import mean_squared_error
from anfis import ANFIS

# Generar datos de entrada y salida (señal senoidal)
X = np.linspace(0, 10, 1000).reshape(-1, 1)
y = np.sin(X).ravel()

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Definir el modelo ANFIS
anf = ANFIS(n_inputs=1, n_rules=10, learning_rate=0.01, epochs=100)

# Entrenar el modelo
anf.fit(X_train, y_train)

# Predecir con el modelo entrenado
y_pred_train = anf.predict(X_train)
y_pred_test = anf.predict(X_test)

# Calcular el error cuadrático medio
mse_train = mean_squared_error(y_train, y_pred_train)
mse_test = mean_squared_error(y_test, y_pred_test)

print("Error cuadrático medio en el conjunto de entrenamiento:", mse_train)
print("Error cuadrático medio en el conjunto de prueba:", mse_test)

# Visualización de resultados
plt.figure(figsize=(10, 6))
plt.scatter(X_test, y_test, color='blue', label='Datos reales')
plt.plot(X_test, y_pred_test, color='red', label='Predicciones')
plt.title('Predicción de una señal senoidal con ANFIS')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.show()

