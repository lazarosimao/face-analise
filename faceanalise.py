import boto3
import json

s3 = boto3.resource('s3')
client = boto3.client('rekognition')

def main(event, context):
    faces_detectadas = detecta_faces()
    faceId_detectadas = cria_lista_faceId_detectadas(faces_detectadas)
    resultado_comparacao = compara_imagens(faceId_detectadas)
    dados_json = gera_dados_json(resultado_comparacao)
    publica_dados(dados_json)
    excluir_imagem_colecao(faceId_detectadas)
    print(json.dumps(dados_json, indent=4))

def detecta_faces():
    faces_detectadas=client.index_faces(
        CollectionId='faces',
        DetectionAttributes=[
            'DEFAULT'
        ],
        ExternalImageId='TEMPORARIA',
        Image={
            'S3Object': {
                'Bucket': 'curso-lambda-images',
                'Name': '_analise.jpeg',
            }
        }
    )

    return faces_detectadas

def cria_lista_faceId_detectadas(faces_detectadas):
    faceId_detectadas = []
    for i in range(len(faces_detectadas['FaceRecords'])):
        faceId_detectadas.append(faces_detectadas['FaceRecords'][i]['Face']['FaceId'])
    return faceId_detectadas

def compara_imagens(faceId_detectadas):
    resultado_comparacao = []
    for i in faceId_detectadas:
        resultado_comparacao.append(
            client.search_faces(
                CollectionId='faces',
                FaceId=i,
                FaceMatchThreshold=80,
                MaxFaces=10,
            )
        )
    return resultado_comparacao

def gera_dados_json(resultado_comparacao):
    dados_json = []
    for i in resultado_comparacao:
        if (len(i.get('FaceMatches')) >= 1):
            perfil = dict(nome=i['FaceMatches'][0]['Face']['ExternalImageId'], faceMatch=round(i['FaceMatches'][0]['Similarity'], 2))
            dados_json.append(perfil)
    return dados_json

def publica_dados(dados_json):
    arquivo = s3.Object('curso-alura-site', 'dados.json')
    arquivo.put(Body=json.dumps(dados_json))

def excluir_imagem_colecao(faceId_detectadas):
    client.delete_faces(
        CollectionId='faces',
        FaceIds=faceId_detectadas
    )