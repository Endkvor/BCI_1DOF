import time
import tkinter as tk
from gpiozero import MCP3008
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pywt
#import anfis
import csv
import serial
from sklearn.model_selection import train_test_split
from skfuzzy import control as ctrl
from sklearn.metrics import mean_squared_error


# Inicializamos listas vacias
# Listas completas
F_C3 = []
F_CZ = []
F_C4 = []
# Listas para ventanas
v_C3 = []
v_CZ = []
v_C4 = []
# Listas para corrimientos
v_C3_s = []
v_CZ_s = []
v_C4_s = []

# Definicion de contador y parametros base
estado_actual = 'reposo'
cont = 0
num_muestra = 0
num_muestra_list = []
GUI_counter = 0
fs = 160  # frecuencia de muestreo
t = np.linspace(0, 1, fs, False)  # Vector de tiempo de ventana

# Parametros del filtro 1
l_inf_1 = 4.0
l_sup_1 = 17.0
order = 8
nyquist = 0.5 * fs
# Parametros del filtro 2
l_inf_2 = 9.0
l_sup_2 = 30

# Frecuencias de corte Normalizadas
bajo_1 = l_inf_1 / nyquist
alto_1 = l_sup_1 / nyquist
bajo_2 = l_inf_2 / nyquist
alto_2 = l_sup_2 / nyquist

# Filtro pasa banda butterworth coeficientes
b_1, a_1 = signal.butter(order, [bajo_1, alto_1], btype='band')
b_2, a_2 = signal.butter(order, [bajo_2, alto_2], btype='band')

# Definiciones para transformada Wavelet
wavelet_function = 'db4'  # seleccionamos daubechies 4
nivel_desc = 3  # nivel de descomposición
frec_muestreo_wt = fs 
# Generamos la wavelet
wavelet = pywt.Wavelet(wavelet_function)
# Respuesta en frecuencia
frecuencias_wt = np.fft.fftfreq(len(wavelet.dec_lo), d=1 / frec_muestreo_wt)
respuesta_wt = np.abs(np.fft.fft(wavelet.dec_lo, n=len(frecuencias_wt)))

# Serial
ser = serial.Serial('COM6', 9600)
ser.close()
ser.open()

# Funcion que lee las entradas analogicas
def read_analog_inputs_arduino():
    data_string = ser.readline()
    adc0, adc1, adc2 = data_string.decode().split(",")
    value_0 = float(adc0)
    value_1 = float(adc1)
    value_2 = float(adc2)
    return value_0, value_1, value_2

# Funcion que muestra en pantalla el color y el estado en la GUI segun un indice
def show_instruction(j):
    colors = ['blue', 'green', 'blue', 'yellow', 'blue', 'pink', 'blue', 'purple']
    states = ['Reposo', 'Abrir Mano', 'Reposo', 'Cerrar Mano', 'Reposo', 'Imagina cerrar la mano', 'Reposo', 'Imagina abrir la mano']
    global estado_actual
    estado_actual = states[j]
    root.configure(bg=colors[j])
    state_label.config(text=states[j])
    root.update()

# Funcion que guarda en CSV las lecturas del estado actual
def save_to_csv():
    with open('./analog_values.csv', 'w', newline='') as csvfile:
        fieldnames = ['Estado', 'Valor_C3', 'Valor_CZ', 'Valor_C4', 'Muestra']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(F_C3)):
            writer.writerow({
                'Estado': estado_actual,
                'Valor_C3': F_C3[i],
                'Valor_CZ': F_CZ[i],
                'Valor_C4': F_C4[i],
                'Muestra': num_muestra_list[i]
            })
        num_muestra_list = []

# Declaracion de parametros del TK inter
root = tk.Tk()
root.title('Entrenador')
root.geometry("300x200")

state_label = tk.Label(root, text="", font=("Arial", 18))
state_label.pack(pady=20)

show_instruction(0)  # ejecucion del primer estado

start_time = time.time()

while True:
    elapsed_time = time.time() - start_time
    if elapsed_time >= 15:
        start_time = time.time()
        show_instruction(GUI_counter)
        GUI_counter = (GUI_counter + 1) % 8  # Reset GUI counter after 8 states

    # Adquisicion de datos en los puertos de entrada 
    a, b, c = read_analog_inputs_arduino()

    # Aqui almacenamos continuamente los datos
    F_C3.append(a)
    F_CZ.append(b)
    F_C4.append(c)

    if len(v_C3) < fs:
        v_C3.append(a)
        v_CZ.append(b)
        v_C4.append(c)
    else:
        # Aqui ya tenemos la primer ventana 
        # Aqui comienza a llenarse los valores de corrimiento
        cont += 1
        v_C3_s.append(a)
        v_CZ_s.append(b)
        v_C4_s.append(c)

        if cont == 10:
            ######################################################
            # Aqui va el procesamiento
            # Aplicamos el filtrado
            v_C3_filtered = signal.lfilter(b_1, a_1, v_C3)
            v_C4_filtered = signal.lfilter(b_1, a_1, v_C4)
            v_CZ_filtered = signal.lfilter(b_1, a_1, v_CZ)

            # Aplicamos Filtro CAR
            senal_prom = np.mean(np.array([v_C3_filtered, v_C4_filtered, v_CZ_filtered]), axis=0)
            v_C3_CAR = v_C3_filtered - senal_prom
            v_CZ_CAR = v_CZ_filtered - senal_prom
            v_C4_CAR = v_C4_filtered - senal_prom

            # Transformada Wavelet
            coefficients_3 = pywt.wavedec(v_C3_CAR, wavelet, level=nivel_desc)
            coefficients_z = pywt.wavedec(v_CZ_CAR, wavelet, level=nivel_desc)
            coefficients_4 = pywt.wavedec(v_C4_CAR, wavelet, level=nivel_desc)

            # Reinicia el corrimiento
            cont = 0
            for i in range(fs - 10):
                v_C3[i] = v_C3[i + 10]
                v_CZ[i] = v_CZ[i + 10]
                v_C4[i] = v_C4[i + 10]
            v_C3[fs - 10:] = v_C3_s
            v_CZ[fs - 10:] = v_CZ_s
            v_C4[fs - 10:] = v_C4_s

            v_C3_s.clear()
            v_CZ_s.clear()
            v_C4_s.clear()

    if len(F_C3) == fs * 15:
        save_to_csv()
        F_C3.clear()
        F_CZ.clear()
        F_C4.clear()
    
    num_muestra_list.append(num_muestra)
    num_muestra += 1

    root.update()
    time.sleep(1 / fs)  # Espera para alcanzar la frecuencia de muestreo
input("Presiona Enter para continuar...")
