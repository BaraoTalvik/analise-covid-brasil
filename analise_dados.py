import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# --- PARTE 1: CARREGAMENTO E LIMPEZA DOS DADOS ---

try:
    # Carrega o dataset
    df = pd.read_csv('caso_full.csv')

    # Filtra os dados para obter apenas a última atualização de cada cidade
    df_cidades = df[df['is_last'] == True].copy()

    # Seleciona apenas as colunas que serão utilizadas
    colunas_uteis = [
        'city',
        'state',
        'estimated_population_2019',
        'last_available_confirmed',
        'last_available_deaths'
    ]
    df_limpo = df_cidades[colunas_uteis].copy()

    # Renomeia as colunas para facilitar o uso no banco de dados
    df_limpo.rename(columns={
        'city': 'cidade',
        'state': 'estado',
        'estimated_population_2019': 'populacao_estimada',
        'last_available_confirmed': 'casos_confirmados',
        'last_available_deaths': 'mortes'
    }, inplace=True)

    # Remove linhas onde a cidade não está especificada
    df_limpo.dropna(subset=['cidade'], inplace=True)

    print("Dados carregados e limpos com sucesso.")
    print(f"Total de cidades analisadas: {len(df_limpo)}")

except FileNotFoundError:
    print("Erro: Arquivo 'caso_full.csv' não encontrado. Verifique o caminho.")
    exit()


# --- PARTE 2: INSERÇÃO NO BANCO DE DADOS MYSQL ---

# Substitua com suas credenciais do MySQL
db_user = 'root'
db_password = '' # INSIRA A SENHA DO SEU MYSQL
db_host = 'localhost'
db_port = '3306'
db_name = 'projeto_covid'
table_name = 'casos_cidades'

try:
    # String de conexão
    engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    # Insere os dados na tabela. Se a tabela já existir, ela será substituída.
    df_limpo.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"Dados inseridos com sucesso na tabela '{table_name}' do banco '{db_name}'.")

except Exception as e:
    print(f"Erro ao conectar ou inserir dados no MySQL: {e}")
    print("Verifique suas credenciais, se o banco 'projeto_covid' existe e se o serviço MySQL está rodando.")
    exit()


# --- PARTE 3: ANÁLISE E GERAÇÃO DO RELATÓRIO ---

print("\n--- RELATÓRIO DE ANÁLISE ---")

# 1. Todos os casos de morte por cidade (Top 20 para visualização)
mortes_por_cidade = df_limpo.groupby('cidade')['mortes'].sum().sort_values(ascending=False)
print("\nCasos de morte por cidade (Top 20):")
print(mortes_por_cidade.head(20))

# 2. População estimada (usaremos a de 2019 como referência "antes")
# A população "depois" não é um dado presente. O relatório mostrará a população e o impacto (mortes).
populacao_e_mortes = df_limpo[['cidade', 'populacao_estimada', 'mortes']].sort_values(by='populacao_estimada', ascending=False)
print("\nPopulação estimada e total de mortes (Top 20 Cidades mais populosas):")
print(populacao_e_mortes.head(20))

# 3. Contagem da maior cidade com quantidade de casos
maior_cidade_casos = df_limpo.loc[df_limpo['casos_confirmados'].idxmax()]
print(f"\nMaior cidade em quantidade de casos: {maior_cidade_casos['cidade']} com {maior_cidade_casos['casos_confirmados']:,} casos.")

# 4. Contagem da menor cidade com quantidade de casos (com pelo menos 1 caso)
df_com_casos = df_limpo[df_limpo['casos_confirmados'] > 0]
menor_cidade_casos = df_com_casos.loc[df_com_casos['casos_confirmados'].idxmin()]
print(f"Menor cidade em quantidade de casos (com pelo menos 1 caso): {menor_cidade_casos['cidade']} com {menor_cidade_casos['casos_confirmados']:,} casos.")

# --- GERAÇÃO DOS GRÁFICOS ---

# Gráfico 1: Top 20 Cidades com Mais Mortes
plt.figure(figsize=(12, 8))
sns.barplot(x=mortes_por_cidade.head(20).values, y=mortes_por_cidade.head(20).index, palette='Reds_r')
plt.title('Top 20 Cidades por Número de Mortes', fontsize=16)
plt.xlabel('Número de Mortes', fontsize=12)
plt.ylabel('Cidade', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_mortes_por_cidade.png')
print("\nGráfico 'grafico_mortes_por_cidade.png' salvo.")

# Gráfico 2: Top 20 Cidades mais populosas
populacao_top20 = populacao_e_mortes.head(20)
plt.figure(figsize=(12, 8))
sns.barplot(x=populacao_top20['populacao_estimada'], y=populacao_top20['cidade'], palette='Blues_r')
plt.title('Top 20 Cidades Mais Populosas (Estimativa 2019)', fontsize=16)
plt.xlabel('População Estimada', fontsize=12)
plt.ylabel('Cidade', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_populacao_por_cidade.png')
print("Gráfico 'grafico_populacao_por_cidade.png' salvo.")