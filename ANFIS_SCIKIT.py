import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# Generar datos de ejemplo
np.random.seed(0)
X1 = np.random.rand(100) * 10
X2 = np.random.rand(100) * 10
Y = X1**2 + X2**3  

# Crear variables de entrada y salida difusas
x1 = ctrl.Antecedent(np.arange(0, 11, 1), 'X1')
x2 = ctrl.Antecedent(np.arange(0, 11, 1), 'X2')
y = ctrl.Consequent(np.arange(0, 1501, 1), 'Y')  # Expandir el rango de Y

# Definir funciones de membresía
x1['low'] = fuzz.trimf(x1.universe, [0, 3, 6])
x1['medium'] = fuzz.trimf(x1.universe, [3, 6, 9])
x1['high'] = fuzz.trimf(x1.universe, [6, 9, 10])

x2['low'] = fuzz.trimf(x2.universe, [0, 3, 6])
x2['medium'] = fuzz.trimf(x2.universe, [3, 6, 9])
x2['high'] = fuzz.trimf(x2.universe, [6, 9, 10])

y['low'] = fuzz.trimf(y.universe, [0, 500, 1000])
y['medium'] = fuzz.trimf(y.universe, [500, 1000, 1500])
y['high'] = fuzz.trimf(y.universe, [1000, 1500, 1500])

# Visualización de funciones de membresía
x1.view()
x2.view()
y.view()

# Pausar ejecución para visualizar gráficos
input("Presiona Enter para continuar...")

# Reglas difusas
rule1 = ctrl.Rule(x1['low'] & x2['low'], y['low'])
rule2 = ctrl.Rule(x1['medium'] & x2['medium'], y['medium'])
rule3 = ctrl.Rule(x1['high'] & x2['high'], y['high'])
# Agregar reglas adicionales
rule4 = ctrl.Rule(x1['low'] & x2['medium'], y['medium'])
rule5 = ctrl.Rule(x1['medium'] & x2['high'], y['high'])

# Crear sistema de control difuso
system = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
anfis_model = ctrl.ControlSystemSimulation(system)

# Depuración: Entrenar modelo ANFIS con datos de ejemplo
predicted_Y = []
for i in range(len(X1)):
    print(f"Entradas: X1 = {X1[i]}, X2 = {X2[i]}")
    anfis_model.input['X1'] = X1[i]
    anfis_model.input['X2'] = X2[i]
    try:
        anfis_model.compute()
        predicted_Y.append(anfis_model.output['Y'])
        print(f"Salida predicha: Y = {anfis_model.output['Y']}")
    except ValueError as e:
        print(f"Error de defuzzificación en el índice {i}: {e}")
        predicted_Y.append(np.nan)  # Añadir valor NaN para manejar el error

# Comparar los resultados con los datos reales
print("Datos reales:")
print(Y[:10])
print("Datos predichos:")
print(predicted_Y[:10])

# Visualización de resultados predichos vs reales
plt.figure()
plt.plot(Y, label="Datos reales")
plt.plot(predicted_Y, label="Datos predichos", linestyle="--")
plt.xlabel("Índice")
plt.ylabel("Valor de salida (Y)")
plt.legend()
plt.show()
