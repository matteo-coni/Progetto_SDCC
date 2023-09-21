import json
import threading
import time
from datetime import timedelta, datetime
import pytz

import docker
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

results = {}

port_hanoi = ""
port_sort = ""
port_matrix = ""
dockerfile_path = ""



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

        # no wait altrimenti rimane bloccato

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

    client = docker.from_env()

    # qui viene cercato il container desiderato tra quelli attivi o in stato exited
    container = None
    for c in client.containers.list(all=True, filters={"name": name}):
        if c.status in ("running", "restarting", "exited"):
            container = c
            break

    if container:
        # se il container è attivo o in stato "exited", viene riavviato
        if container.status == "exited":
            container.restart()
    else:
        # se il container non esiste, ne viene creato e avviato uno nuovo
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

    # devo rifarlo per evitare il problema dell'if else precedente -- imposto la porta del container da contattare
    if name == "cont-hanoi":
        server_url = 'http://localhost:' + port_hanoi +'/esegui-funzione'
        input_string = input

    elif name == "cont-sort":
        server_url = 'http://localhost:' + port_sort +'/esegui-funzione'
        input_string = input

    elif name == "cont-matrix":
        server_url = 'http://localhost:' + port_matrix + '/esegui-funzione'
        input_string = input

    time.sleep(5)  # per evitare che il container non abbia ancora concluso la creazione

    # richiesta HTTP POST al server per ottenere il risultato
    response = requests.post(server_url, json={'input': input_string})

    # controllo il codice di ritorno, se 200 ok
    if response.status_code == 200:
        risultato = response.json().get('risultato', 'Errore')
        print("Risultato:", risultato)

        container = client.containers.get(name)
        container.stop() #stoppo il container per diminuire consumi

        return risultato

    else:
        print("Errore nella richiesta HTTP:", response.status_code)


def call_function_1(image_name):

    docker_absolute = ""

    # costruttio if-else per il ports mapping e per scegliere il dockerfile corretto
    if image_name == "docker-hanoi-py":
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
    result = data.get('result')
    input_ok = data['input']
    name = data['nome']

    # start application per far partire il processo passando il nome della funzione e l'input
    risultato = start_application(name, input_ok)
    results[0] = result
    return jsonify({'risultato': risultato})


def get_last_access_time(container):

    container_info = container.attrs
    # prendo l'ultimo accesso
    last_access_str = container_info['State']['FinishedAt']
    # rimuovo i millisecondi dal formato dell'orario
    last_access_str = last_access_str.split('.')[0] + 'Z'
    last_access = datetime.strptime(last_access_str, '%Y-%m-%dT%H:%M:%S%z')
    last_access = last_access.replace(tzinfo=None)

    return last_access


def close_inactive_containers():

    client = docker.from_env()

    while True:

        now = datetime.now(pytz.utc)  # pytz.utc per il fuso orario

        print("Sono nel ciclo while")

        # limite inattività con 2 minuti
        inactive_limit = (now - timedelta(minutes=2)).replace(tzinfo=None)

        running_containers = client.containers.list(filters={"status": "exited"})  # Lista container stati exited
        print(running_containers)

        for container in running_containers:
            last_access = get_last_access_time(container)

            # Check sull'accesso
            if last_access < inactive_limit:
                print(inactive_limit)
                print(last_access)
                # chiudo solo i container inattivi da 2 minuti
                container.remove(force=True)

        # sleep 120 secondi per l'attesa
        time.sleep(120)


def start_control_cont():
    thread = threading.Thread(target=close_inactive_containers) #thread per il garbage collector
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    with open('src/GUI/config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_server = config_data['port_server']
    port_hanoi = config_data['port_hanoi']
    port_sort = config_data['port_sort']
    port_matrix = config_data['port_matrix']
    dockerfile_path = config_data['path_dockerfile']

    start_control_cont()

    app.run(host='0.0.0.0', port=port_server)
