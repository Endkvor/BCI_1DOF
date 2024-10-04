"""Crear un programa que lea las entradas analogicas de una raspberry pi
con una frecuencia de muestreo de 160 Hz y una ventana de 1 segundo con incrementos de 10 puntos
y sobre esa ventana obtener las metricas como relacion entre alfa y beta o gama etc.
"""
import time
import tkinter as tk
from   gpiozero import MCP3008
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pywt
from datetime import datetime
#import anfis
import csv
import serial
from sklearn.model_selection import train_test_split
from skfuzzy import control as ctrl
from sklearn.metrics import mean_squared_error


#Inicializamos listas vacias
#Listas completas
F_C3=[]
F_CZ=[]
F_C4=[]
    #Listas para ventanas
v_C3 = []
v_CZ = []
v_C4 = []
    #Listas para corrimientos
v_C3_s=[]
v_CZ_s=[]
v_C4_s=[]
#Definicion de contador y parametros base
estado_actual='reposo' #estado inicial
cont=0 #Este es el contador para corrimiento una vez llena la ventana cuenta 10 y se reinicia 
i_GUI=1 # contador para la GUI comienza en 1 ya que el primer estado accedemos a el previo al while
num_muestra=0
num_muestra_list=[]
num_muestra_list.append(num_muestra)
GUI_counter=0
fs=160 #frecuencia de muestreo
t = np.linspace(0, 1, fs, False) # Vector de tiempo de ventana


#Parametros del filtro 1
l_inf_1   = 4.0
l_sup_1   = 17.0
order   = 8
nyquist = 0.5 * fs
#Parametros del filtro 2
l_inf_2 = 9.0
l_sup_2 = 30
##########
#frecuencias de corte Normalizadas
bajo_1 =l_inf_1/nyquist
alto_1= l_sup_1/nyquist
bajo_2 =l_inf_2/nyquist
alto_2= l_sup_2/nyquist

 #Filtro pasa banda butterworth coeficientes
b_1,a_1 =signal.butter(order,[bajo_1,alto_1],btype='band')
b_2,a_2 = signal.butter(order,[bajo_2,alto_2],btype='band')



#Definiciones para transformada Wavelet
wavelet_function ='db4' #seleccionamos daubechies 4
nivel_desc=3#nivel de descomposición
frec_muestreo_wt=fs 
#Generamos la wavelet
wavelet=pywt.Wavelet(wavelet_function)

#respuesta en frecuencia
frecuencias_wt=np.fft.fftfreq(len(wavelet.dec_lo),d=1/frec_muestreo_wt)
respuesta_wt= np.abs(np.fft.fft(wavelet.dec_lo, n=len(frecuencias_wt)))

#Inicializamos el Serial
ser=serial.Serial('COM6',9600)
ser.close()
ser.open()
#Funcion que lee las entradas analogicas
def read_analog_inputs_arduino():
    
    data_string=ser.readline()

   # print("00000000000000000"+data_string.decode()+"000000000000000000000")
    adc0,adc1,adc2= data_string.decode().split(",")
    #print(adc0)
    value_0=float(adc0)
    value_1=float(adc1)
    value_2=float(adc2)

    
#    GUI_counter=0    
    return value_0, value_1, value_2


    #Funcion que muestra en pantalla el color y el estado en la GUI segun un indice
def show_instruction(j):
    colors = ['blue', 'green', 'yellow', 'pink', 'purple']
    states = ['Reposo', 'Abrir Mano', 'Cerrar Mano', 'Imagina cerrar la mano', 'Imagina abrir la mano']
    global estado_actual
    estado_actual=states[j]
    root.configure(bg=colors[j])
    state_label.config(text=states[j])
    root.update()
#    print("Muestra en Pantalla la instrucción")
#Funcion que guarda en CSV las lecturas del estado actual


def save_to_csv(estado_actual, F_C3, F_CZ, F_C4, num_muestra_list):
    try:
        hora_actual = datetime.now().time()
        dia_actual = datetime.now().date()
        dia_string = dia_actual.strftime("%d%m%Y")
        # Convertimos la hora a un string en el formato deseado (HH:MM:SS)
        hora_string = hora_actual.strftime('%H%M%S')
        with open('C:/Users/LENOVO/Documents/Upiita/TrabajoTerminal/Codigos/Datos_Ejecuciones/analog_values_'+str(estado_actual)+'_'+dia_string+'_'+hora_string+'.csv', 'w', newline='') as csvfile:
            fieldnames = ['Estado', 'Valor_C3', 'Valor_CZ', 'Valor_C4', 'Muestra']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for i in range(len(F_C3)):
                
                writer.writerow({
                    'Estado': estado_actual,
                    'Valor_C3': v_C3[i],
                    'Valor_CZ': v_CZ[i],
                    'Valor_C4': v_C4[i],
                    'Muestra': num_muestra_list[i] if i < len(num_muestra_list) else ''  # Agregar el número de muestra
                })
               # print("Se escribió registro correctamente")
        
        print("Se guardó el archivo CSV correctamente.")
    except IOError as e:
        print(f"Error al escribir en el archivo CSV: {e}")

# Ejemplo de llamada a la función (debes tener los datos adecuados en las variables)
# save_to_csv(estado_actual, v_C3, v_CZ, v_C4, num_muestra_list)

            
        

#Declaracion de parametros del TK inter
root = tk.Tk()
root.title('Entrenador')
root.geometry("300x200")

state_label = tk.Label(root, text="", font=("Arial", 18))
state_label.pack(pady=20)

show_instruction(0)# ejecucion del primer estado
while(1):
    #Hacemosun contador para la gui donde guarde el estado cada 15 segundos
    if((GUI_counter/fs)==15):
        GUI_counter=0
        show_instruction(i_GUI)
        i_GUI=i_GUI+1
        if i_GUI==5:# Numero de estados
            i_GUI=0


    GUI_counter=GUI_counter+1
    #Adquisicion de datos en los puertos de entrada 
    a,b,c=read_analog_inputs_arduino()
    #Aqui almacenamos continuamente los datos
    
    F_C3.append(a)
    F_CZ.append(b)
    F_C4.append(c)
    if(len(v_C3)<fs):
        v_C3.append(a)
        v_CZ.append(b)
        v_C4.append(c)
    else:
        #print(len(v_C3))
    #Aqui ya tenemos la primer ventana 
    #Aqui comienza a llenarse los valores de corrimiento
        cont+=1
        v_C3_s.append(a)
        v_CZ_s.append(b)
        v_C4_s.append(c)
        if cont==10:
            ######################################################
            #Aqui va el procesamiento
           
            #Aplicamos el filtrado
            v_C3_filtered= signal.lfilter(b_1, a_1, v_C3)
            v_C4_filtered= signal.lfilter(b_1, a_1, v_C4)
            v_CZ_filtered= signal.lfilter(b_1, a_1, v_CZ)
            #Aplicamos Filtro CAR
            senal_prom=np.mean(np.array([v_C3_filtered,v_C4_filtered,v_CZ_filtered]),axis=0)
            v_C3_CAR=v_C3_filtered -senal_prom
            v_CZ_CAR=v_CZ_filtered -senal_prom
            v_C4_CAR=v_C4_filtered -senal_prom
           

            #Obtenemos Relacion ALFA-DELTA BETA-THETA

             #Analisis de componentes independientes ICA

            #Correlacion coherencia medicion de similitud

            #Obtenemos la densidad de potencia Espectral

            #Obtenemos unespectrograma

            #Transformada Wavelet
            #Calculamos los coeficientes    
            coefficients_3 = pywt.wavedec(v_C3_CAR, wavelet, level=nivel_desc)
            coefficients_z = pywt.wavedec(v_CZ_CAR, wavelet, level=nivel_desc)
            coefficients_4 = pywt.wavedec(v_C4_CAR, wavelet, level=nivel_desc)
            #Aplicamos ANFIS Etapa 1

            #Aplicamos ANFIS Etapa 2

            #Aplicamos ANFIS Etapa 3

            #Aplicamos ANFIS Etapa 4

            #Aplicamos ANFIS Etapa 5


            #Salida al ARDUINO MEGA


            #####################################################
            #inicia el corrimiento 
            cont=0
            v_C3_c=v_C3
            v_CZ_c=v_CZ
            v_C4_c=v_C3

            for i in range(len(v_C3)):
                if(i<fs-10):
                    v_C3[i]=v_C3_c[i+10]#recorre 10 lugares los datos de la ventana dejando los ultimos 10 vacios
                    v_C4[i]=v_C4_c[i+10]
                    v_CZ[i]=v_CZ_c[i+10]
                else:
                    v_C3[i]=v_C3_s[i-(fs-10)]#Aqui carga los valores de corrimiento en los ultimos 10 valores vacios
                    v_C4[i]=v_C4_s[i-(fs-10)]
                    v_CZ[i]=v_CZ_s[i-(fs-10)]
            v_C3_s=[]# vacia las miniventanas de corrimiento
            v_CZ_s=[]
            v_C4_s=[]
    if(len(F_C3)==(fs*15)):
    #Guardamos externamente los estados en archivos csv nombrados por estados y numero de ejecución
        save_to_csv(estado_actual, F_C3, F_CZ, F_C4, num_muestra_list) 
#        print("csv")   
    #Reseteamos los valores totales para almacenarlos estados 
        F_C3=[]
        F_CZ=[]
        F_C4=[]    
    num_muestra_list.append(num_muestra)
    num_muestra+=1

    root.update()
    time.sleep(1 / fs)  # Espera para alcanzar la frecuencia de muestreo
   
input("Presiona Enter para continuar...")