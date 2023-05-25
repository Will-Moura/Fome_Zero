#===========================================================================
#BIBLIOTECAS 
#===========================================================================
import pandas as pd 
import re 
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#===========================================================================
#DEFININDO O ENQUANDRO DA PAGINA 
#===========================================================================
st.set_page_config( 
   page_title="🍴Culinárias",
   layout="wide",
)


#===========================================================================
#FUNÇÕES: 
#===========================================================================
#Criando a coluna com nomes nomes de países:
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]
#==============================================================

#Criando uma coluna com os tipos de acordo com a coluna price_range
def create_price_tye(price_range): 
   if price_range == 1:
       return "cheap"
   elif price_range == 2:
       return "normal"
   elif price_range == 3:
       return "expensive"
   else:
       return "gourmet"
#==============================================================

CURRENCY = {
    'Botswana Pula(P)': 0.076,
    'Brazilian Real(R$)': 0.19,
    'Dollar($)': 1,
    'Emirati Diram(AED)': 0.27,
    'Indian Rupees(Rs.)': 0.012,
    'Indonesian Rupiah(IDR)': 0.000065,
    'NewZealand($)': 0.61,
    'Pounds(£)': 1.20,
    'Qatari Rial(QR)': 0.27,
    'Rand(R)': 0.055,
    'Sri Lankan Rupee(LKR)': 0.0031,
    'Turkish Lira(TL)': 0.059 
}

def convert_dollar(cc):
    return CURRENCY[cc]
#==============================================================

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]
#==============================================================

def clean_code (df):
    #alterando nome das colunas:
    df = df.rename(columns={'Restaurant ID': 'restaurant_id' , 'Restaurant Name':'restaurant_name', 'Country Code':'country_code', 'City': 'city', 'Address': 'address',
        'Locality':'locality', 'Locality Verbose':'locality_verbose' , 'Longitude':'longitude', 'Latitude':'latitude', 'Cuisines': 'cuisines',
        'Average Cost for two':'cost_for_two', 'Currency':'currency', 'Has Table booking':'has_table_booking',
        'Has Online delivery':'has_online_delivery', 'Is delivering now':'is_delivering_now', 'Switch to order menu':'switch_to_order_menu',
        'Price range':'price_range', 'Aggregate rating':'aggregate_rating', 'Rating color':'rating_color', 'Rating text':'rating_text',
        'Votes':'votes'})


    # 0. tirando os valores vazios (NaN) das colunas selecionadas("~" inverte o isnull e pega so as que nao sao nulas):
    linhas_sem_nulos = ~df['cuisines'].isnull()
    df = df.loc[linhas_sem_nulos, :].copy() 
    #### Verificar se há nulos
    #### Identificar valores nulos em todas as colunas
    #valores_vazios = df.isnull()
    #### Contar valores vazios em cada coluna
    #contagem_vazios = valores_vazios.sum()
    ##### Imprimir contagem de valores vazios em cada coluna
    #print(contagem_vazios) 

    #Código para aparecer todas as colunas quando usar o ".head()"
    #pd.set_option('display.max_columns', None)  # exibir todas as colunas
    #pd.set_option('display.width', None)  # exibir todas as colunas sem quebrar linhas

    #Apagando uma linha onde o preço do restaurante está errado:
    df = df.drop(df[df.cost_for_two == 25000017.0].index)

    #Limpar a coluna de "Tipo de Culinária"
    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

    #Criar a coluna "country_name", nome dos países.
    df['country_name'] = df['country_code'].apply(lambda x: country_name(x))

    df['cost_for_two'] = df['cost_for_two']*df['currency'].apply(lambda x: convert_dollar(x))

    df['name_color'] = df['rating_color'].apply(lambda x: color_name(x))

    pd.set_option('display.max_columns', None) 

    return df
#==============================================================

def top_10_restaurant(df):
    cols = [ 'restaurant_id', 'restaurant_name', 'country_name', 'city', 'cuisines', 'cost_for_two', 'aggregate_rating' ]
    df_aux = df.loc[linhas_selecionadas, cols].groupby( ['restaurant_id', 'restaurant_name', 'country_name', 'city', 'cuisines', 'cost_for_two'] ).mean().sort_values('aggregate_rating', ascending=False).reset_index()
    df_aux = df_aux.head(df_display)
    
    return df_aux
#==============================================================

#Top 10 melhores tipos de culinária
def best_types_cuisines(df):
    df_aux11 = df.loc[:, ['cuisines', 'aggregate_rating']].groupby('cuisines').mean().sort_values('aggregate_rating', ascending=False).reset_index()
    df_aux = df_aux11.head(10)
    
    df_aux['aggregate_rating'] = df_aux['aggregate_rating'].round(2)
    
    fig = px.bar(df_aux, x='cuisines', y='aggregate_rating',
                title='Top 10 Melhores tipos de Culinárias',
                labels={'cuisines':'Culinária', 'aggregate_rating':'Avaliações'},
                text='aggregate_rating')
    return fig

#==============================================================
def worst_types_cuisines(df):
    df_aux11 = df.loc[:, ['cuisines', 'aggregate_rating']].groupby('cuisines').mean().sort_values('aggregate_rating', ).reset_index()
    df_aux = df_aux11.head(10)
    
    df_aux['aggregate_rating'] = df_aux['aggregate_rating'].round(2)
    
    fig = px.bar(df_aux, x='cuisines', y='aggregate_rating',
                title='Top 10 Piores tipos de Culinárias',
                labels={'cuisines':'Culinária', 'aggregate_rating':'Avaliações'},
                text='aggregate_rating')
    return fig

#===========================================================================
#IMPORTANDO O DATAFRAME
#===========================================================================
df_row = pd.read_csv('dataset/zomato.csv') 
df = df_row.copy()

#===========================================================================
#LIMPANDO OS DADOS
#===========================================================================
df = clean_code (df)

#=====================================================================================
#LAYOUT e BARRA LATERAL (ESQUERDA)
#===================================================================================== 
#textos
st.title( "🍴Melhores Restaurantes dos Principais tipos Culinários" ) 

#imagem
image = Image.open( 'imagem2.png' )
st.sidebar.image( image, width=40 ) 

st.sidebar.markdown('### Fome Zero!')
st.sidebar.markdown('---')

#=====================================================================================
# FILTRO DOS DADOS
#===================================================================================== 

# Filtro de PAISES
traffic_options = st.sidebar.multiselect('#### Escolha os países que deseja visualizar os  restaurantes:',
['Philippines', 'Brazil', 'Australia', 'United States of America',
'Canada', 'Singapure', 'United Arab Emirates', 'India',
'Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa',
'Sri Lanka', 'Turkey'],
    default=['Brazil', 'Australia', 'Canada', 'England', 'Qatar', 'South Africa',] )

# FILTRO DE QUANTIDADE DE RESTAURANTES
df_display = st.sidebar.slider( 
    'Ate qual valor?',         
    value=( 10 ), 
    max_value=( 20 ), 
    min_value=( 1 ), )

# CRIANDO SELEÇÃO DE TIPO DE CULINARIA
st.sidebar.markdown("## Selecione as condições de transito que deseja:") 
cuisines_options = st.sidebar.multiselect( 
    'Quais as condições do transito?',
    ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza', 'Taiwanese', 
     'Japanese', 'Coffee', 'Chinese', 'Seafood', 'Singaporean', 'Vietnamese', 'Latin American',  
     'Healthy Food', 'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery', 'Tex-Mex',  
     'Bar Food', 'International', 'French', 'Steak', 'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',  
     'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary', 'Desserts', 'Juices', 'Beverages', 'Spanish',  
     'Thai', 'Indian', 'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian', 'Author',  
     'Gourmet Fast Food', 'Lebanese', 'Modern Australian', 'African', 'Coffee and Tea', 'Australian', 
     'Middle Eastern', 'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern', 'Diner', 'Donuts',  
     'Southwestern', 'Sandwich', 'Irish', 'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',  
     'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco', 'Caribbean', 'Polish', 'Deli', 'British', 
     'California', 'Others', 'Eastern European', 'Creole', 'Ramen', 'Ukrainian', 'Hawaiian', 'Patisserie', 'Yum Cha', 
     'Pacific Northwest', 'Tea', 'Moroccan', 'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian', 'Continental',  
     'South Indian', 'North Indian', 'Salad', 'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani', 'Biryani',  
     'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai', 'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls', 
     'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab', 'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 
     'Awadhi', 'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean', 'Egyptian', 'Malwani', 'Armenian',  
     'Roast Chicken', 'Indonesian', 'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian', 'Balti',  
     'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji', 'South African', 'Drinks Only', 'Durban', 'World Cuisine',  
     'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe', 'Kumpir', 'Döner', 'Turkish Pizza', 
     'Ottoman', 'Old Turkish Bars', 'Kokoreç'],
default=['American', 'Japanese', 'Brazilian', 'Italian', 'Arabian', 'BBQ', 'Home-made' ] )

linhas_selecionadas = df['cuisines'].isin(cuisines_options)
# df_filtro = df.loc[linhas_selecionadas, :]

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by William Moura')

#=====================================================================================
#PERGUNTAS SOBRE CULINÁRIA
#===================================================================================== 

#1. Dos restaurantes que possuem o tipo de culinária italiana, qual o nome do restaurante com a maior média de avaliação?

with st.container():
    col1, col2, col3, col4, col5= st.columns( 5, gap='large' )

    with col1:

        
        cols0 = ['restaurant_name', 'cuisines', 'aggregate_rating']
        lines0 = df['cuisines'] == 'Italian'
        df_aux0 = df.loc[lines0 , cols0].groupby(['restaurant_name', 'cuisines']).mean().sort_values('aggregate_rating', ascending=False).reset_index()
        
        restaurant = (df_aux0.iloc[0,0])
        voto = (df_aux0.iloc[0,2])
        
        st.markdown("Italiano:")
        col1.metric(restaurant, voto )

#2. Culinária Americana
    with col2: 
        
        cols2 = ['restaurant_name', 'cuisines', 'aggregate_rating']
        lines2 = df['cuisines'] == 'American'
        df_aux2 = df.loc[lines2 , cols2].groupby(['restaurant_name', 'cuisines']).mean().sort_values('aggregate_rating', ascending=False).reset_index()
        
        restaurant1 = (df_aux2.iloc[0,0])
        voto1 = (df_aux2.iloc[0,2])

        st.markdown("Americano")
        col2.metric(restaurant1, voto1 )

#3. Culinária Árabe:
    with col3:
        
        cols4 = ['restaurant_name', 'cuisines', 'aggregate_rating']
        lines4 = df['cuisines'] == 'Arabian'
        df_aux4 = df.loc[lines4 , cols4].groupby(['restaurant_name', 'cuisines']).mean().sort_values('aggregate_rating', ascending=False).reset_index()
        
        restaurant2 = (df_aux4.iloc[0,0])
        voto2 = (df_aux4.iloc[0,2])

        st.markdown("Árabe")
        col3.metric(restaurant2, voto2 )

#4. Culinária Japonesa
    with col4:

        cols6 = ['restaurant_name', 'cuisines', 'aggregate_rating']
        lines6 = df['cuisines'] == 'Japanese'
        df_aux6 = df.loc[lines6 , cols6].groupby(['restaurant_name', 'cuisines']).mean().sort_values('aggregate_rating', ascending=False).reset_index()
        
        #df_aux6.head() 
    
        restaurant3 = (df_aux6.iloc[0,0])
        voto3 = (df_aux6.iloc[0,2])

        st.markdown("japonês")
        col4.metric(restaurant3, voto3 )

    with col5:
        
    #5. Culinária Caseira
        cols8 = ['restaurant_name', 'cuisines', 'aggregate_rating']
        lines8 = df['cuisines'] == 'Home-made'
        df_aux8 = df.loc[lines8 , cols8].groupby(['restaurant_name', 'cuisines']).mean().sort_values('aggregate_rating', ascending=False).reset_index()
        
        restaurant4 = (df_aux8.iloc[0,0])
        voto4 = (df_aux8.iloc[0,2])

        st.markdown("Caseiro")
        col5.metric(restaurant4, voto4 )

#===================================================================================== 
#GRAFICOS MENORES DO SEGUNDO CONTAINER
#===================================================================================== 
with st.container():

###Top 10 Restaurantes 

    df_aux = top_10_restaurant(df)
    st.dataframe(df_aux)
#===================================================================================== 
#===================================================================================== 

with st.container():
    col1, col2=st.columns(2 , gap='large')

    with col1:

        fig = best_types_cuisines(df)
        st.plotly_chart(fig, use_container_width=True)
#=======================================

    with col2:

        fig = worst_types_cuisines(df)
        st.plotly_chart(fig, use_container_width=True)
   
#===================================================================================== 
#===================================================================================== 
#fim
    
    