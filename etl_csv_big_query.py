# -*- coding: utf-8 -*-
"""ETL csv -> Google Big Query.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17aAfVYpaA9d7j9KFk5uycMatoHn6Ti9E

#ETL Com Python

Projeto de ETL (Extract Transform and Load) de dados, utilizando linguagem Python.
 - Extração de dados no formato.csv.
 - Limpeza, transformação e henriquecimento desses dados.
 - Carregamento desses dados em uma instância do Google Big Query.

Dados Fonte: https://dados.gov.br/dados/conjuntos-dados/dados-abertos-de-contratos-administrativos

# Bibliotecas Utilizadas
"""

import pandas as pd
from IPython.display import Image
from google.oauth2 import service_account

"""# Extração dos Dados"""

df_contratos = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/contratos-2020/tabela_contratos.csv')

display(df_contratos)

df_empresas = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/contratos-2020/tabela_empresas.csv')

display(df_empresas)

df_datas = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/contratos-2020/tabela_datas.csv')

display(df_datas)

"""# Limpeza, Transformação e Henriquecimento de Dados"""

Image('https://datasagar.com/illionso_awesome/2023/02/joinsinsql_.jpg')

# Fazendo join com df_empresas
contratos_joined = df_contratos.merge(df_empresas,
                                   left_on='fk_empresa_contratada',
                                   right_on='id_empresa',
                                   how='left')

display(contratos_joined)

# Excluíndo as colunas que contém o id_empresa
contratos_joined.drop(columns=['id_empresa', 'fk_empresa_contratada'], inplace=True)

# Exibindo as 5 primeiras linhas do dataframe
contratos_joined.head(5)

# Fazendo join com df_datas para pegar a data de inicio da vigência do contrato
contratos_joined_2 = contratos_joined.merge(df_datas,
                                   left_on='inicio_vigencia',
                                   right_on='id_data',
                                   how='left')

# Exibindo as 5 primeiras linhas do dataframe
contratos_joined_2.head(5)

# Excluíndo as colunas que contém o id_data
contratos_joined_2.drop(columns=['inicio_vigencia', 'id_data'], inplace=True)

# Renomeando coluna de data
contratos_joined_2.rename(columns={'data': 'data_inicio_vigencia'}, inplace=True)

# Exibindo as 5 primeiras linhas do dataframe
contratos_joined_2.head(5)

# Fazendo 2º join com df_datas para pegar a data de término da vigência do contrato
contratos_joined_3 = contratos_joined_2.merge(df_datas,
                                   left_on='termino_vigencia',
                                   right_on='id_data',
                                   how='left')

# Excluíndo as colunas que contém o id_data
contratos_joined_3.drop(columns=['termino_vigencia', 'id_data'], inplace=True)

# Renomeando coluna de data
contratos_joined_3.rename(columns={'data': 'data_termino_vigencia'}, inplace=True)

# Exibindo as 5 primeiras linhas do dataframe
contratos_joined_3.head(5)

# Modificando o nome do dataframe
contratos_final = contratos_joined_3
display(contratos_final)

# Verificando existência de registros nulos
contratos_final.count()

# Verificando tipo de dados de cada coluna
contratos_final.dtypes

# Modificando o tipo de dados das colunas de data
contratos_final.data_inicio_vigencia = pd.to_datetime(contratos_final.data_inicio_vigencia, format='%d/%m/%Y').dt.date

contratos_final.data_termino_vigencia = pd.to_datetime(contratos_final.data_termino_vigencia, format='%d/%m/%Y').dt.date

# Verificando na coluna data termino vigencia qual registro de data incorreto
for i in contratos_final.data_termino_vigencia:
  print(i)
  print(pd.to_datetime(i))

# Identifiquei que possuimos um registro de data como 31/09/2017 - Setembro possui apenas 30 dias
# Corrigindo esse registro
contratos_final.data_termino_vigencia = contratos_final.data_termino_vigencia.str.replace('31/09/2017', '30/09/2017')

# Modificando o tipo de dados das colunas de data
contratos_final.data_termino_vigencia = pd.to_datetime(contratos_final.data_termino_vigencia, format='%d/%m/%Y').dt.date

display(contratos_final)

# Acrescentando uma coluna para calcular a diferença de tempo entre o inicio e término do contrato
contratos_final['tempo_contrato'] = (contratos_final.data_termino_vigencia - contratos_final.data_inicio_vigencia).dt.days

contratos_final

# Verificando se possuimos registros duplicados
contratos_final.nome_contrato.value_counts()

contratos_final[contratos_final.nome_contrato == '004/16']

contratos_final.tempo_contrato.value_counts()

# Filtrando o dataframe para retirar os registros de tempo de contrato negativo ou zerado
contratos_final = contratos_final[contratos_final.tempo_contrato > 0]

contratos_final.tempo_contrato.value_counts()

# Resetando o indice após a exclusão dos registros
contratos_final.reset_index(drop=True, inplace=True)

contratos_final.tail()

"""# Carregando Dados Limpos e Tratados no Big Query"""

credentials = service_account.Credentials.from_service_account_file(filename='/content/drive/MyDrive/Colab Notebooks/GBQ_credentials_project.json',
                                                                    scopes=['https://www.googleapis.com/auth/cloud-platform'])

# Carregando os dados no big query
# Parametro if_exists: replace = dropa a tabela sempre que o código for executado, append = preserva a tabela e acrescenta o novo dataframe no final.
contratos_final.to_gbq(credentials=credentials,
                       destination_table='etl_python.contratos_csv',
                       if_exists='replace',
                       table_schema=[{'name': 'data_inicio_vigencia', 'type': 'DATE'},
                                     {'name': 'data_termino_vigencia', 'type': 'DATE'}])