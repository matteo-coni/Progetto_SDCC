import json
import boto3
from flask import jsonify, Flask, request

app = Flask(__name__)

number_offload = 10

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

def offload_to_lambda(array):
    # Configuro il client AWS Lambda

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

    payload = {
        'input': my_string
    }

    # Chiamo la funzione Lambda
    response = lambda_client.invoke(
        FunctionName='merge_sort_lambda',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    result = response['Payload'].read()      # risultato
    print("Risultato da Lambda:", result)
    risultato_dict = json.loads(result)
    body = risultato_dict["body"]
    print(body)

    my_string = ",".join(map(str, body))

    print(my_string)

    return body  # qui ritorno una lista


def merge_sorted_lists(list1, list2):  # date le due liste ordinate separatamente
                                        # le unisco e le riordino insieme
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

        data = request.get_json()  # Input Json
        input_string = data['input']
        my_list = list(map(int, input_string.split(",")))

        print(my_list)

        # Decisione offloading nell'if
        if len(input_string) <= number_offload:
            risultato = merge_sort(my_list)
        else:

            risultato1 = merge_sort(my_list[0:number_offload-1])
            risultato2 = offload_to_lambda(my_list[number_offload-1:])

            risultato = merge_sorted_lists(risultato1, risultato2)

        return jsonify({'risultato': risultato})

    except Exception as e:
        return jsonify({'errore': str(e)})


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
    port_sort = config_data['port_sort']
    number_offload = config_data['number_offload_sort']

    app.run(host='0.0.0.0', port=int(port_sort))
