import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

try:
    df = pd.read_csv('caso_full.csv')

    df_cidades = df[df['is_last'] == True].copy()

    colunas_uteis = [
        'city',
        'state',
        'estimated_population_2019',
        'last_available_confirmed',
        'last_available_deaths'
    ]
    df_limpo = df_cidades[colunas_uteis].copy()

    df_limpo.rename(columns={
        'city': 'cidade',
        'state': 'estado',
        'estimated_population_2019': 'populacao_estimada',
        'last_available_confirmed': 'casos_confirmados',
        'last_available_deaths': 'mortes'
    }, inplace=True)

    df_limpo.dropna(subset=['cidade'], inplace=True)

    print("Dados carregados e limpos com sucesso.")
    print(f"Total de cidades analisadas: {len(df_limpo)}")

except FileNotFoundError:
    print("Erro: Arquivo 'caso_full.csv' não encontrado. Verifique o caminho.")
    exit()

db_user = 'root'
db_password = ''
db_host = 'localhost'
db_port = '3306'
db_name = 'projeto_covid'
table_name = 'casos_cidades'

try:
    engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    df_limpo.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"Dados inseridos com sucesso na tabela '{table_name}' do banco '{db_name}'.")

except Exception as e:
    print(f"Erro ao conectar ou inserir dados no MySQL: {e}")
    print("Verifique suas credenciais, se o banco 'projeto_covid' existe e se o serviço MySQL está rodando.")
    exit()

print("\n--- RELATÓRIO DE ANÁLISE ---")

mortes_por_cidade = df_limpo.groupby('cidade')['mortes'].sum().sort_values(ascending=False)
print("\nCasos de morte por cidade (Top 20):")
print(mortes_por_cidade.head(20))

populacao_e_mortes = df_limpo[['cidade', 'populacao_estimada', 'mortes']].sort_values(by='populacao_estimada', ascending=False)
print("\nPopulação estimada e total de mortes (Top 20 Cidades mais populosas):")
print(populacao_e_mortes.head(20))

maior_cidade_casos = df_limpo.loc[df_limpo['casos_confirmados'].idxmax()]
print(f"\nMaior cidade em quantidade de casos: {maior_cidade_casos['cidade']} com {maior_cidade_casos['casos_confirmados']:,} casos.")

df_com_casos = df_limpo[df_limpo['casos_confirmados'] > 0]
menor_cidade_casos = df_com_casos.loc[df_com_casos['casos_confirmados'].idxmin()]
print(f"Menor cidade em quantidade de casos (com pelo menos 1 caso): {menor_cidade_casos['cidade']} com {menor_cidade_casos['casos_confirmados']:,} casos.")

plt.figure(figsize=(12, 8))
sns.barplot(x=mortes_por_cidade.head(20).values, y=mortes_por_cidade.head(20).index, palette='Reds_r')
plt.title('Top 20 Cidades por Número de Mortes', fontsize=16)
plt.xlabel('Número de Mortes', fontsize=12)
plt.ylabel('Cidade', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_mortes_por_cidade.png')
print("\nGráfico 'grafico_mortes_por_cidade.png' salvo.")

populacao_top20 = populacao_e_mortes.head(20)
plt.figure(figsize=(12, 8))
sns.barplot(x=populacao_top20['populacao_estimada'], y=populacao_top20['cidade'], palette='Blues_r')
plt.title('Top 20 Cidades Mais Populosas (Estimativa 2019)', fontsize=16)
plt.xlabel('População Estimada', fontsize=12)
plt.ylabel('Cidade', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_populacao_por_cidade.png')
print("Gráfico 'grafico_populacao_por_cidade.png' salvo.")