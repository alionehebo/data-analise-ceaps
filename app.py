import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Senado", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO (Com Cache para evitar erros de memória) ---
@st.cache_data
def load_data():
    url = "https://www.senado.gov.br/transparencia/LAI/verba/despesa_ceaps_2022.csv"
    # Usando os parâmetros que descobrimos na Etapa 1
    data = pd.read_csv(url, sep=';', encoding='latin1', skiprows=1)
    
    # LIMPEZA IMEDIATA (Para o df já nascer pronto)
    data['VALOR_REEMBOLSADO'] = data['VALOR_REEMBOLSADO'].str.replace(',', '.').astype(float)
    data['DATA'] = pd.to_datetime(data['DATA'], dayfirst=True, errors='coerce')
    return data

# --- EXECUÇÃO DO CARREGAMENTO ---
# Aqui garantimos que o 'df' existe antes de qualquer outra linha rodar
try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop() # Interrompe a aplicação se não carregar o dado

# --- INTERFACE DO USUÁRIO (UI) ---
st.title("🎯 Análise de Gastos - Senado 2022")

# Sidebar para filtros
st.sidebar.header("Filtros")
senadores = sorted(df['SENADOR'].unique())
senador_selecionado = st.sidebar.selectbox("Selecione um Senador", ["Todos"] + senadores)

# Lógica de Filtro
if senador_selecionado != "Todos":
    df_plot = df[df['SENADOR'] == senador_selecionado]
else:
    df_plot = df

# --- VISUALIZAÇÃO ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Maiores Gastos por Senador")
    
    # 1. Criamos a figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 2. Lógica de Agrupamento Correta:
    # Agrupamos por SENADOR, somamos o valor e pegamos os 10 maiores
    top_gastadores = df_plot.groupby('SENADOR')['VALOR_REEMBOLSADO'].sum().sort_values(ascending=False).head(10).reset_index()
    
    # 3. Geramos o gráfico usando o novo DataFrame 'top_gastadores'
    sns.barplot(
        data=top_gastadores, 
        x='VALOR_REEMBOLSADO', 
        y='SENADOR', 
        ax=ax, 
        palette='magma'
    )
    
    ax.set_xlabel("Soma de Gastos (R$)")
    ax.set_ylabel("Senador")
    
    st.pyplot(fig)

    #Dados brutos

with col2:
    st.subheader("Visualização dos Dados")
    
    # Se "Todos" estiver selecionado, mostramos os maiores gastos individuais de 2022
    if senador_selecionado == "Todos":
        st.write("Exibindo os 100 maiores reembolsos individuais de 2022:")
        # Ordenamos pelo valor para não ver apenas o primeiro senador da lista
        dados_exibicao = df_plot.sort_values(by='VALOR_REEMBOLSADO', ascending=False).head(100)
    else:
        st.write(f"Notas fiscais de: {senador_selecionado}")
        # Se um senador for selecionado, mostramos os gastos dele do mais caro para o mais barato
        dados_exibicao = df_plot.sort_values(by='VALOR_REEMBOLSADO', ascending=False)

    # Exibindo a tabela com colunas selecionadas para não poluir a tela
    colunas_visiveis = ['SENADOR', 'DATA', 'TIPO_DESPESA', 'VALOR_REEMBOLSADO', 'FORNECEDOR']
    st.dataframe(dados_exibicao[colunas_visiveis], use_container_width=True)