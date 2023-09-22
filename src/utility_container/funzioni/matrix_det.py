import json

import boto3
from flask import jsonify, Flask, request

app = Flask(__name__)

# Qui imposto le credenziali come variabili globali
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
aws_access_key_id = config_data['aws_access_key_id']
aws_secret_access_key = config_data['aws_secret_access_key']
aws_session_token = config_data['aws_session_token']

lambda_client = boto3.client('lambda', region_name='us-east-1',
                             aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             aws_session_token=aws_session_token)


def divide_matrix(matrix):

    submatrices = []
    for col in range(len(matrix)):
        submatrix = [row[:col] + row[col + 1:] for row in (matrix[1:])]
        submatrices.append(submatrix)

    return submatrices


@app.route('/esegui-funzione', methods=['POST'])
def esegui_funzione():

    try:
        # prendo i dati in json
        data = request.get_json()

        # prendo l'input sotto forma di stringa
        input_string = data['input']

        matrix = [list(map(int, line.split(','))) for line in input_string.split('\n')]  # essendo l'input una stringa, lo trasformo in una lista

        payload = {
                'matrix': matrix  # metto la lista matrix in un campo di un oggetto json
        }

        # chiamo la funzione lambda con l'api di aws
        response = lambda_client.invoke(
            FunctionName='matrix_lambda',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        result = json.loads(response['Payload'].read())  # Qui prendo il risultato dal json
        cofactors = result['cofactors']

        # Calcola il determinante utilizzando i cofattori calcolati su aws lambda
        determinant = 0
        for i in range(len(matrix)):
            determinant += matrix[0][i] * round(cofactors[i])

        print("Determinante:", determinant)

        # restituzione risultato come JSON
        return jsonify({'risultato': determinant})

    except Exception as e:
        return jsonify({'errore': str(e)})


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_matrix = config_data['port_matrix']
    app.run(host='0.0.0.0', port=int(port_matrix))

