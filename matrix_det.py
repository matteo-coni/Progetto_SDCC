import json

import boto3
from flask import jsonify, Flask, request

app = Flask(__name__)

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

def divide_matrix(matrix):

    submatrices = []
    for col in range(len(matrix)):
        submatrix = [row[:col] + row[col + 1:] for row in (matrix[1:])]
        submatrices.append(submatrix)

    return submatrices


@app.route('/esegui-funzione', methods=['POST'])
def esegui_funzione():
    print("funzione in esecuzione")
    try:
        # Ricevi i dati dalla richiesta HTTP come JSON
        data = request.get_json()

        # Estrai la stringa di input dalla richiesta
        input_string = data['input']

        print(type(input_string))

        #input_string = "1,2,3\n4,5,6\n7,8,9"  # La tua stringa
        matrix = [list(map(int, line.split(','))) for line in input_string.split('\n')]


        """matrix = [[1,4,3,1],
                  [1,1,2,2],
                  [2,3,4,3],
                  [11,2,3,10]]"""

        print("ok")
        # Esegui la tua funzione
        payload = {
                'matrix': matrix
        }

        # Invoca la funzione Lambda per calcolare i cofattori
        response = lambda_client.invoke(
            FunctionName='matrix_lambda',  # Nome della tua funzione Lambda
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Estrai la risposta dalla chiamata Lambda
        result = json.loads(response['Payload'].read())
        cofactors = result['cofactors']

        # Calcola il determinante utilizzando i cofattori calcolati in locale
        determinant = 0
        for i in range(len(matrix)):
            print(cofactors[i])# + " int: " + int(cofactors[i]))
            print(round(cofactors[i]))

            determinant += matrix[0][i] * round(cofactors[i])

        print("Determinante:", determinant)

        # Restituisci il risultato come JSON
        return jsonify({'risultato': determinant})

    except Exception as e:
        return jsonify({'errore': str(e)})


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_matrix = config_data['port_matrix']
    app.run(host='0.0.0.0', port=int(port_matrix))

