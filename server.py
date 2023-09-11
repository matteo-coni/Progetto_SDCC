import json
import time

import docker
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

results = {}

port_hanoi = ""
port_sort = ""
port_matrix = ""

def build_and_run_container_py(image_name, dockerfile_path, docker_absolute, ports_mapping):
    client = docker.from_env()

    if image_name == "docker-hanoi-py":
        cont_name = "cont-hanoi"
    elif image_name == "docker-sort":
        cont_name = "cont-sort"
    elif image_name == "docker-matrix":
        cont_name = "cont-matrix"

    try:
        # Costruisci l'immagine del container
        image, build_logs = client.images.build(path=dockerfile_path, dockerfile=docker_absolute, tag=image_name)
        print("problema non è build_logs")
        # Run del container a partire da un immagine costruita sopra
        container = client.containers.run(
            image=image_name,
            ports=ports_mapping,
            detach=True,
            name=cont_name
        )


        result = container.logs().decode("utf-8")  # Log

        global string

        string = container.attrs['NetworkSettings']['IPAddress']
        print("stringa è " + string)

        # container.wait() no wait altrimenti rimane bloccato

        return result

    except docker.errors.BuildError as e:
        print("Build failed:", e.build_log)
        print(build_logs)
    except docker.errors.ContainerError as e:
        print("Container failed:", e.stderr)
    except Exception as e:
        print("An error occurred:", e)

    return None

def start_application(name, input):
    # Inizializza il client Docker
    client = docker.from_env()

    # Cerca il container desiderato tra quelli attivi o in stato "exited"
    container = None
    for c in client.containers.list(all=True, filters={"name": name}):
        if c.status in ("running", "restarting", "exited"):
            container = c
            break

    if container:
        # Se il container è attivo o in stato "exited", riavvialo
        if container.status == "exited":
            container.restart()
    else:
        # Se il container non esiste, crea un nuovo container e avvialo
        print("entrato nell'else, creo il container")
        if name == "cont-hanoi":
            call_function_1("docker-hanoi-py")
            print("else name == cont-hanoi")

        elif name == "cont-sort":
            call_function_1("docker-sort")
            print("else name == cont-sort")

        elif name == "cont-matrix":
            call_function_1("docker-matrix")
            print("else name == cont-matrix")

    # devo rifarlo per evitare il problema dell'if else precedente
    if name == "cont-hanoi":
        server_url = 'http://localhost:' + port_hanoi +'/esegui-funzione'
        print(server_url)
        input_string = input
        print("ok input string hanoi: " + input_string )


    elif name == "cont-sort":
        server_url = 'http://localhost:' + port_sort +'/esegui-funzione'
        input_string = input #"1,2,3,4,5,3,4,5,6,7,8,9,23,4,5,5,6,7,5,4,5,6,7,5,3,5,6,4,3,3,5,7,4,3,2,2,2,2,3,3,10,3,3,3,33333,4,4,44,4,7,6,5,4,3,2,111,22,333,444,5555,6666,777,1,2"
        print(server_url)
        print("ok input string sort: " + input_string)

    elif name == "cont-matrix":
        server_url = 'http://localhost:' + port_matrix + '/esegui-funzione'
        print(server_url)
        input_string = input
        print("ok input string matrix: " + input_string)

    time.sleep(5)

    # Esegui una richiesta HTTP POST al server
    response = requests.post(server_url, json={'input': input_string})

    # Verifica la risposta
    if response.status_code == 200:
        risultato = response.json().get('risultato', 'Errore')
        print("Risultato:", risultato)

        return risultato
        #result_text.delete(1.0, tk.END)  # Cancella il testo precedente
        #result_text.insert(1.0, risultato)

    else:
        print("Errore nella richiesta HTTP:", response.status_code)


def call_function_1(image_name):  # prova con funzione scritta in python

    dockerfile_path = "/Users/matteo/SDCC_Project/SDCC_Faas"
    docker_absolute = ""

    if image_name == "docker-hanoi-py":
        # docker_absolute = "/Users/matteo/SDCC_Project/SDCC_Faas/Dockerfile_Hanoi"
        docker_absolute = "Dockerfile_Hanoi"
        ports_mapping = {
            '80/tcp': int(port_hanoi)
        }
    elif image_name == "docker-sort":
        docker_absolute = "Dockerfile_Sort"
        ports_mapping = {
            '8080/tcp': int(port_sort)
        }
    elif image_name == "docker-matrix":
        docker_absolute = "Dockerfile_Matrix"
        ports_mapping = {
            '8443/tcp': int(port_matrix)
        }

    container = build_and_run_container_py(image_name, dockerfile_path, docker_absolute, ports_mapping)
    print(container)

    if container:
        print("Container creato e in esecuzione:", container)
    else:
        print("Creazione del container fallita.")


@app.route('/start_application', methods=['POST'])
def start():
    data = request.get_json()
    # container_id = data.get('container_id')
    result = data.get('result')

    input_prova = data['input']
    name = data['nome']

    # ora fai start application
    risultato = start_application(name, input_prova)
    results[0] = result
    return jsonify({'risultato': risultato})


if __name__ == '__main__':
    with open('GUI/config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_server = config_data['port_server']
    port_hanoi = config_data['port_hanoi']
    port_sort = config_data['port_sort']
    port_matrix = config_data['port_matrix']

    app.run(host='0.0.0.0', port=port_server)
