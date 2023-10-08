import pandas as pd
import requests
import json
import openai

df = pd.read_csv("./userIDlist-to-mkt.csv")    # le o arquivo
user_ids = df['UserID'].tolist()  # converte a coluna UserID para lista

# URL da API Santander Dev Week
sdw2023_api_url = "https://sdw-2023-prd.up.railway.app"

# Buscando usuarios no banco de dados da API da SDW


def get_user(id):
    rota = f'{sdw2023_api_url}/users/{id}'
    response = requests.get(rota)
    return response.json() if response.status_code == 200 else None


users = [user for id in user_ids if (user := get_user(id)) is not None]

# print(json.dumps(users[0], indent=2))

# Criando as mensagens usando OpenAI para cada usuario
openai.api_key = "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"


def generate_ai_message(user):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Você é um expert em marketing bancário."
            },
            {
                "role": "user",
                "content": f"Crie uma mensagem pessoal para o usuario {user['name']} oferecendo os produtos de investimento em renda fixa para sua conta no banco Santander (máximo de 150 caracteres)"
            },
        ],
    )
    return response['choices'][0]['message']['content'].strip('\"')


for user in users:
    mkt_message = generate_ai_message(user)
    user['news'].append({"description": mkt_message})
    print(user['news'])

# Atualizar a lista de "news" de cada usuário de volta para a API da santander Dev Week com a nova mensagem gerada.


def update_user(user):
    # json=user estabelece o body em formato json
    response = requests.put(
        f"{sdw2023_api_url}/users/{user['id']}", json=user)
    return True if response.status_code == 200 else False


for user in users:
    success = update_user(user)
    print(f" Usuário {user['name']} atualizado com sucesso? {success}!")
