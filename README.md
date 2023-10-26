# Explorando IA Generativa em um Pipeline de ETL com Python

Uso do GPT da OpenAI para gerar mensagens de marketing personalizadas para um sistema bancário. 

<img width="300"  src="https://media.giphy.com/media/iiSb58oATiANL65Dd2/giphy.gif">


Este projeto é baseado no desafio de projeto [Santander Bootcamp 2023 - Ciência de Dados com Python](https://web.dio.me/track/71477949-f762-43c6-9bf2-9cf3d7f61d4a) da [DIO](https://www.dio.me/). 

- [Repositorio da API Santander Dev Week 20](https://github.com/digitalinnovationone/santander-dev-week-2023-api)
- [Swager da API](https://sdw-2023-prd.up.railway.app/swagger-ui/index.html#/)
- [Colab  ETL com Python](https://colab.research.google.com/drive/1SF_Q3AybFPozCcoFBptDSFbMk-6IVGF-?usp=sharing)

## Passos da ETL

1. [Extract](#1-extract)
2. [Transform](#2-transform)
3. [Load](#3-load)

## 1. Extract

> Objetivo: Extrair os IDs do arquivo .csv e obter os dado de cada ID usando a API da Santander Dev Week 2023.

Biblioteca Panda lê arquivo .csv e transforma em data frame.

```python
import pandas as pd

df = pd.read_csv('SDW2023.csv')
user_ids = df['UserID'].tolist()
print(user_ids)
```

Para buscar usuário pelo ID na API, precisamos importar as bibliotecas `request` e `json`. 

Vamos criar uma função' que receba a response da API e busque os usuários.

> Obs: A URL da API pra retornar o usuario 4520 é `https://sdw-2023-prd.up.railway.app/users/4520`. 
>> sdw2023_api_url = `https://sdw-2023-prd.up.railway.app`

```python
import requests
import json

def get_user(id):
  response = requests.get(f'{sdw2023_api_url}/users/{id}')                       # busca o usuario na API
  return response.json() if response.status_code == 200 else None                # retorna a response em formato json se o status code for 200, se nao, nao retorne nada

users = [user for id in user_ids if (user := get_user(id)) is not None]          # se get_user(id) é diferente de None, user = get_user(id)
                                                                                 # faca isso enquanto percorre a lista user_ids como id  
print(json.dumps(users, indent=2))                                               # funcao dumps formata a saida e indenta 

```

## 2. Transform

> Objetivo: Usar a API do OpenAI GPT-4 para gerar uma mensagem de marketing personalizada para cada usuário.

Instalando a OpenAI

```
!pip install openai
```

É preciso criar uma conta na OpenAI e inserir sua API Key da OpenAI.

```python
openai_api_key = 'jambalaia'
```

Importanto a API e gerando as mensagens, baseado na documentação [Create chat completion](https://platform.openai.com/docs/api-reference/chat/create):

```python
import openai

openai.api_key = openai_api_key  # insere chave unica

def generate_ai_news(user):                   # funcao para gerar mensagem para o usuario
  completion = openai.ChatCompletion.create(
    model="gpt-4",     # aqui é onde eu converso com o chat gpt
    messages=[
      {
          "role": "system",
          "content": "Você é um especialista em marketing bancário."
      },
      {
          "role": "user",
          "content": f"Crie uma mensagem para {user['name']} sobre a importância dos investimentos (máximo de 100 caracteres)"
      }
    ]
  )
  return completion.choices[0].message.content.strip('\"')

for user in users:
  news = generate_ai_news(user)    # chamando a funcao para cada usuario
  print(news)
  user['news'].append({
      "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
      "description": news
  })
```


## 3. Load

> Objetivo: Atualizar a lista de "news" de cada usuário de volta para a API da santander Dev Week com a nova mensagem gerada.

```python
def update_user(user):                                                           # criando uma funcão que atualiza o a API com PUT 
  response = requests.put(f"{sdw2023_api_url}/users/{user['id']}", json=user)    # json=user estabelece o body em formato json
  return True if response.status_code == 200 else False                       

for user in users:                                      #  percorrendo os usuários
  success = update_user(user)
  print(f"User {user['name']} updated? {success}!")
```
