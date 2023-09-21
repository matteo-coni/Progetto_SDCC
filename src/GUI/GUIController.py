import json
import tkinter as tk
from tkinter import scrolledtext
import docker
import requests

string = None


def start_application(nome_cont, input):

    #File config.json
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

    # Recupera il valore della chiave riferita alla porta e sostituisce la porta nell'URL
    port_server = config_data['port_server']
    server_url = config_data['url_server'].replace('XXXX', port_server)

    response = requests.post(server_url, json={'input': input, 'nome': nome_cont})

    if response.status_code == 200:

        risultato = response.json().get('risultato', 'Errore')
        print("Risultato:", risultato)

        if nome_cont == "cont-hanoi":
            result_text1.delete(1.0, tk.END)  # Cancella il testo precedente
            result_text1.insert(1.0, risultato)

        elif nome_cont == "cont-sort":
            result_text2.delete(1.0, tk.END)  # Cancella il testo precedente
            result_text2.insert(1.0, risultato)

        elif nome_cont == "cont-matrix":
            result_text3.delete(1.0, tk.END)  # Cancella il testo precedente
            result_text3.insert(1.0, risultato)

    else:
        if nome_cont == "cont-hanoi":
            result_text1.delete(1.0, tk.END)  # Cancella il testo precedente
            result_text1.insert(1.0, "Errore nell'esecuzione: hai inserito un intero positivo?")

        elif nome_cont == "cont-sort":
            result_text3.delete(1.0, tk.END)  # Cancella il testo precedente
            result_text2.insert(1.0,
                                "Errore nell'esecuzione: hai inserito una sequenza di numeri intervallata da virgole? (es. 3,2,1)")

        elif nome_cont == "cont-matrix":
            result_text3.delete(1.0, tk.END)  # Cancella il testo precedente
            result_text3.insert(1.0, "Errore nell'esecuzione: hai inserito la matrice correttamente? (es. \n1,2,3\n4,5,6\n7,8,9\n ")


def stop_and_remove_all_containers():
    client = docker.from_env()

    # Ottieni la lista di tutti i container (anche quelli fermi o exited)
    containers = client.containers.list(all=True)

    # Rimuovi tutti i container
    for container in containers:
        container.remove(force=True)

    print("Tutti i container sono stati fermati e rimossi.")


def show_hanoi_window():
    hanoi_window.deiconify()
    main_window.withdraw()


def show_sort_window():
    sort_window.deiconify()
    main_window.withdraw()


def show_matrix_window():
    matrix_window.deiconify()
    main_window.withdraw()


def go_back():
    main_window.deiconify()
    hanoi_window.withdraw()
    sort_window.withdraw()
    matrix_window.withdraw()

def on_closing():
    stop_and_remove_all_containers()
    print("Chiusura")
    main_window.destroy()


# Main window
main_window = tk.Tk()
main_window.geometry("800x463")
main_window.title("FAAS Management")
main_window.resizable(False, False)

background_image = tk.PhotoImage(file="sfondo_main.png")

# Label per l'immagine di sfondo
background_label = tk.Label(main_window, image=background_image)
background_label.place(relwidth=1, relheight=1)

title_label = tk.Label(main_window, text="Benvenuto: seleziona la funzione che vuoi eseguire", font=("Helvetica", 28),
                       fg="blue")

# Finestre
hanoi_window = tk.Toplevel(main_window)
hanoi_window.geometry("800x463")
hanoi_window.resizable(False, False)
background_label = tk.Label(hanoi_window, image=background_image)
background_label.place(relwidth=1, relheight=1)

sort_window = tk.Toplevel(main_window)
sort_window.geometry("800x463")
sort_window.resizable(False, False)
background_label = tk.Label(sort_window, image=background_image)
background_label.place(relwidth=1, relheight=1)

matrix_window = tk.Toplevel(main_window)
matrix_window.geometry("800x463")
matrix_window.resizable(False, False)
background_label = tk.Label(matrix_window, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Nascondi le finestre delle schermate inizialmente
hanoi_window.withdraw()
sort_window.withdraw()
matrix_window.withdraw()

# schermata Hanoi
hanoi_label = tk.Label(hanoi_window, text="Hanoi Tower", height=2, width=20)
hanoi_label.pack()

# schermata Merge Sort
sort_label = tk.Label(sort_window, text="Merge Sort", height=2, width=20)
sort_label.pack()

# schermata Determinante Matrice
matrix_label = tk.Label(matrix_window, text="Determinante Matrice", height=2, width=20)
matrix_label.pack()

# Aggiungi pulsanti principali per navigare tra le schermate
hanoi_button_main = tk.Button(main_window, text="Hanoi", command=show_hanoi_window, height=4, width=50)
sort_button_main = tk.Button(main_window, text="Merge Sort", command=show_sort_window, height=4, width=50)
matrix_button_main = tk.Button(main_window, text="Determinante Matrice", command=show_matrix_window, height=4, width=50)

title_label.pack(pady=10)
hanoi_button_main.pack(pady=18)
sort_button_main.pack(pady=18)
matrix_button_main.pack(pady=18)

# HANOI
# Aggiungi pulsante per tornare alla schermata principale
back_button1 = tk.Button(hanoi_window, text="Torna alla schermata principale", command=go_back)
back_button1.pack(pady=5)

input_text_1 = tk.Text(hanoi_window, height=1, width=7, font=("Helvetica", 21))
input_text_1.pack(pady=18)

exec_button = tk.Button(hanoi_window,
                        text="Elenca tutti i passi necessari per i dischi inseriti",
                        command=lambda: start_application("cont-hanoi", input_text_1.get("1.0", "end-1c")), height=3,
                        width=40)
exec_button.pack(pady=18)

result_text1 = scrolledtext.ScrolledText(hanoi_window, wrap=tk.WORD, font=("Helvetica", 12))
result_text1.pack(pady=18)

# SORT
back_button2 = tk.Button(sort_window, text="Torna alla schermata principale", command=go_back)
back_button2.pack(pady=5)

input_text_2 = tk.Text(sort_window, height=1, width=7, font=("Helvetica", 21))
input_text_2.pack(pady=18)

exec_button2 = tk.Button(sort_window,
                         text="Ordina gli elementi inseriti (x,x,x,x)",
                         command=lambda: start_application("cont-sort", input_text_2.get("1.0", "end-1c")), height=3,
                         width=30)
exec_button2.pack(pady=18)

result_text2 = scrolledtext.ScrolledText(sort_window, wrap=tk.WORD, font=("Helvetica", 18), width=50)
result_text2.pack(pady=18)

# MATRIX
back_button3 = tk.Button(matrix_window, text="Torna alla schermata principale", command=go_back)
back_button3.pack(pady=5)

input_text_3 = tk.Text(matrix_window, height=5, width=30, font=("Helvetica", 21))
input_text_3.pack(pady=18)

exec_button3 = tk.Button(matrix_window,
                         text="Calcola il determinante ",
                         command=lambda: start_application("cont-matrix", input_text_3.get("1.0", "end-1c")), height=3,
                         width=30)
exec_button3.pack(pady=18)

result_text3 = scrolledtext.ScrolledText(matrix_window, wrap=tk.WORD, font=("Helvetica", 18), width=50)
result_text3.pack(pady=18)
##

main_window.protocol("WM_DELETE_WINDOW", on_closing) # Protocol: gestione chiusura finestra, chiamo on_closing
hanoi_window.protocol("WM_DELETE_WINDOW", on_closing) # Protocol: gestione chiusura finestra, chiamo on_closing
sort_window.protocol("WM_DELETE_WINDOW", on_closing) # Protocol: gestione chiusura finestra, chiamo on_closing
matrix_window.protocol("WM_DELETE_WINDOW", on_closing) # Protocol: gestione chiusura finestra, chiamo on_closing

# Avvia la GUI
main_window.mainloop()

