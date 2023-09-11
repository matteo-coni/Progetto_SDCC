import json

import boto3
from flask import Flask, request, jsonify


app = Flask(__name__)


def hanoi(n, da_asta, a_asta, asta_di_appoggio):
    if n == 1:
        # Caso base: sposta il disco 1 da 'da_asta' a 'a_asta'
        return [(1, da_asta, a_asta)]

    else:
        # Sposta n-1 dischi da 'da_asta' all'asta d'appoggio
        steps = hanoi(n - 1, da_asta, asta_di_appoggio, a_asta)

        # Sposta il disco rimanente
        steps.append((n, da_asta, a_asta))

        # Sposta gli n-1 dischi da 'asta_di_appoggio' a 'a_asta' usando l'asta iniziale come ausiliaria
        steps.extend(hanoi(n - 1, asta_di_appoggio, a_asta, da_asta))

        return steps


def offload_to_lambda(input):
    # Configura il client AWS Lambda


    #aws_access_key_id="ASIAZXICDICSL5WV3W32"
    #aws_secret_access_key="v3ucFmfZXr7+cv0ABElmamXfh4COGK8RansQGcwa"
    #aws_session_token="FwoGZXIvYXdzEOD//////////wEaDMoTooHXU2AQ+W/BHCK8Aa+g/ECmIygO4cej5Tb6NKpAyUuSgonRryYqp/JBpvhrUFMrzBPyd5Zs2bDRljEq+26SQTLhUL6aRICY6qeZ6Gz7725tSfs2PsKm0RYxwXsKXlQ46qSjFz3lGPvw2seBfehsaXHeUeYi2cNBA1S78xiRAQvpU2Ekkdy6OWy41U1l3noW04fd8bYADWl2Lj1S/OFoEE5b0i8mesjsrM6We5Rg6EKKgORPut5dsUEUGAbIipHSwL8nb8v3EyOqKLrs7KcGMi2oe/k1kRwTBk8fNUf7QdtfUYkCAmuNAuCri+qNRr5PsHGMUa91yJHyew1dKHU="

    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    aws_access_key_id = config_data['aws_access_key_id']
    aws_secret_access_key = config_data['aws_secret_access_key']
    aws_session_token = config_data['aws_session_token']

    lambda_client = boto3.client('lambda', region_name='us-east-1',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 aws_session_token=aws_session_token)

    print("sto processando su aws lambda")

    payload = {
        'input': input
    }

    # Chiama la funzione Lambda
    response = lambda_client.invoke(
        FunctionName='hanoi_lambda',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    # Ottieni il risultato dalla risposta
    result = response['Payload'].read()
    print("Risultato da Lambda:", result)
    risultato_dict = json.loads(result)
    body = risultato_dict["body"]
    print(body)

    return body


@app.route('/esegui-funzione', methods=['POST'])
def esegui_funzione():
    print("funzione in esecuzione")
    try:
        # Ricevi i dati dalla richiesta HTTP come JSON
        data = request.get_json()

        # Estrai la stringa di input dalla richiesta
        input_string = data['input']

        input_int = int(input_string)

        if input_int > 4:
            risultato = offload_to_lambda(input_string)
        else:
            risultato = hanoi(int(input_string), 'A', 'B', 'C')

        # Restituisci il risultato come JSON
        return jsonify({'risultato': risultato})

    except Exception as e:

        return jsonify({'errore': str(e)})


if __name__ == '__main__':

    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_hanoi = config_data['port_hanoi']
    app.run(host='0.0.0.0', port=int(port_hanoi))
