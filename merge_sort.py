import base64
import json
import os

import boto3
from flask import jsonify, Flask, request

app = Flask(__name__)

def merge_sort(arr):

    if len(arr) > 1:
        mid = len(arr) // 2  # Trova il punto medio del vettore
        left_half = arr[:mid]  # Divide il vettore in due metà
        right_half = arr[mid:]

        merge_sort(left_half)  # Ordina la prima metà
        merge_sort(right_half)  # Ordina la seconda metà

        i = j = k = 0

        # Combinazione delle due metà ordinate
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

    return arr
# Esempio di utilizzo:

def offload_to_lambda(array):
    # Configura il client AWS Lambda

    #aws_access_key_id="ASIAZXICDICSL5WV3W32"
    #aws_secret_access_key="v3ucFmfZXr7+cv0ABElmamXfh4COGK8RansQGcwa"
    #aws_session_token="FwoGZXIvYXdzEOD//////////wEaDMoTooHXU2AQ+W/BHCK8Aa+g/ECmIygO4cej5Tb6NKpAyUuSgonRryYqp/JBpvhrUFMrzBPyd5Zs2bDRljEq+26SQTLhUL6aRICY6qeZ6Gz7725tSfs2PsKm0RYxwXsKXlQ46qSjFz3lGPvw2seBfehsaXHeUeYi2cNBA1S78xiRAQvpU2Ekkdy6OWy41U1l3noW04fd8bYADWl2Lj1S/OFoEE5b0i8mesjsrM6We5Rg6EKKgORPut5dsUEUGAbIipHSwL8nb8v3EyOqKLrs7KcGMi2oe/k1kRwTBk8fNUf7QdtfUYkCAmuNAuCri+qNRr5PsHGMUa91yJHyew1dKHU="

    with open('GUI/config.json', 'r') as config_file:
        config_data = json.load(config_file)
    aws_access_key_id = config_data['aws_access_key_id']
    aws_secret_access_key = config_data['aws_secret_access_key']
    aws_session_token = config_data['aws_session_token']

    lambda_client = boto3.client('lambda', region_name='us-east-1',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 aws_session_token=aws_session_token)

    print("sto processando su aws lambda")

    my_string = ",".join(map(str, array))

    print(my_string)

    payload = {
        'input': my_string
    }

    # Chiama la funzione Lambda
    response = lambda_client.invoke(
        FunctionName='merge_sort_lambda',
        InvocationType='RequestResponse',  # Cambia in base alle tue esigenze
        Payload=json.dumps(payload)
    )

    # Ottieni il risultato dalla risposta
    result = response['Payload'].read()
    print("Risultato da Lambda:", result)
    risultato_dict = json.loads(result)
    body = risultato_dict["body"]
    print(body)

    my_string = ",".join(map(str, body))
    #risultato_json = {
    #    'risultato': body
    #}

    print(my_string)
    # Ritorna il risultato come JSON
    #return jsonify(risultato_json)
    return body

def merge_sorted_lists(list1, list2):

    merged_list = []
    i = j = 0

    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            merged_list.append(list1[i])
            i += 1
        else:
            merged_list.append(list2[j])
            j += 1

    # Aggiungi gli elementi rimanenti, se presenti
    merged_list.extend(list1[i:])
    merged_list.extend(list2[j:])

    return merged_list


@app.route('/esegui-funzione', methods=['POST'])
def esegui_funzione():
    print("funzione in esecuzione")
    try:
        # Ricevi i dati dalla richiesta HTTP come JSON
        data = request.get_json()

        # Estrai la stringa di input dalla richiesta
        input_string = data['input']
        my_list = list(map(int, input_string.split(",")))

        print(my_list)
        # prova
        #input_string = [64, 34, 25, 12, 22, 11, 90, 1, 34, 78, 123, 23, 88, 11, 1989]


        # Esegui la tua funzione
        if len(input_string) <= 10:
            risultato = merge_sort(my_list)
        else:

            risultato1 = merge_sort(my_list[0:9])
            risultato2 = offload_to_lambda(my_list[9:])

            risultato = merge_sorted_lists(risultato1, risultato2)

        # Restituisci il risultato come JSON
        return jsonify({'risultato': risultato})

    except Exception as e:
        return jsonify({'errore': str(e)})


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_sort = config_data['port_sort']
    app.run(host='0.0.0.0', port=int(port_sort))
