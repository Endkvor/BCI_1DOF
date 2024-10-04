import csv
import time
import tkinter as tk
from   gpiozero import MCP3008

analog_values_by_state = {}

def read_analog_inputs():
    adc0 = MCP3008(channel=0)
    adc1 = MCP3008(channel=1)
    adc2 = MCP3008(channel=2)
    
    value0 = adc0.value
    value1 = adc1.value
    value2 = adc2.value
    
    return value0, value1, value2

def acquire_samples(state, samples_to_acquire):
    samples = []
    
    for _ in range(samples_to_acquire):
        analog_values = read_analog_inputs()
        samples.append(analog_values)
        time.sleep(1 / 160)  # Espera para alcanzar la frecuencia de muestreo
    
    analog_values_by_state[state] = samples

def change_state(i):
    colors = ['blue', 'green', 'blue', 'yellow', 'blue', 'pink', 'blue', 'purple']
    states = ['Reposo', 'Abrir Mano', 'Reposo', 'Cerrar Mano', 'Reposo', 'Imagina cerrar la mano', 'Reposo', 'Imagina abrir la mano']
    
    if i >= len(colors):
        save_to_csv()  # Llamar a la función para guardar los datos en CSV al finalizar
        return
    
    root.configure(bg=colors[i])
    state_label.config(text=states[i])
    
    acquire_samples(states[i], 160 * 15)  # Adquirir 160 muestras por segundo durante 15 segundos
    
    i += 1
    root.after(1, change_state, i)  # Esperar 1 milisegundo antes de cambiar al siguiente estado

def save_to_csv():
    with open('analog_values.csv', 'w', newline='') as csvfile:
        fieldnames = ['Estado', 'Valor_ADC0', 'Valor_ADC1', 'Valor_ADC2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for state, samples in analog_values_by_state.items():
            for idx, values in enumerate(samples):
                writer.writerow({
                    'Estado': state,
                    'Valor_ADC0': values[0],
                    'Valor_ADC1': values[1],
                    'Valor_ADC2': values[2],
                    'Muestra': idx + 1  # Agregar el número de muestra
                })

root = tk.Tk()
root.title('Entrenador')
root.geometry("300x200")

state_label = tk.Label(root, text="", font=("Arial", 18))
state_label.pack(pady=20)

change_state(0)

root.mainloop()

print("Valores guardados por estado:", analog_values_by_state)
