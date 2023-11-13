import streamlit as st
import cantera as ct
import numpy as np
import plotly.express as px   
import pandas as pd

import STube
import Reactor


st.set_page_config(
    page_title="1D non-equlibrium nozzle flow - Calc",
    layout="wide",
    )

with st.sidebar:
    st.write("# Dados de Entrada")

    st.write("## Tubo de Choque")
    X1  = st.text_input(label='Composição Inicial do Driven', value='O2: 0.21, N2: 0.79')
    st.write("*obs: a composição inicial deverá conter somente O, O2, N, NO, NO2, N2O e N2*")
    p1 =  st.number_input(label="Pressão inicial do Driven (kPa):"       , value=11.0   , min_value=1.0, step=0.1)*1e3
    T1 =  st.number_input(label="Temperatura inicial do Driven (K):"     , value=298.   , min_value=298., step=1.)
    us =  st.number_input(label="Vel. da Onda de Choque Incidente (m/s):", value=2100.0 , min_value=350., step=0.1)
    p8 =  st.number_input(label="Pressão de Estagnação Medida (MPa):"    , value=8.8    , min_value=0.0, step=0.1)*1e6
    st.write("*obs: insira 0 no campo acima na ausência de uma pressão p5 e uma estimativa será usada.*")
    bool_ST= False
    try:
        gas8 = STube.STube_Calc(T1, p1, us, p8, X1)
        bool_ST= True
        T5 = gas8.T; p5 = gas8.P; h5 = gas8.h; X = gas8.X 
        st.write(":green[**!STube Rodou Corretamente!**]")
        
    except:
        st.write(":red[**!Erro em STube Calc!**]")
        bool_ST= False


    st.write("## Tubeira")
    ang =  st.number_input(label="Semi-ângulo de divergência (graus):"  , value=15.0,   min_value=1.0, step=0.10 )
    r_0 =  st.number_input(label="Raio à Garganta (mm):"           , value=6.40,   min_value=0.0, step=0.10 )*1e-3
    r_f =  st.number_input(label="Raio à Saída (mm):"              , value=150.,   min_value=0.0, step=0.10 )*1e-3

    if bool_ST == True:
        try: 
            Reator = Reactor.PFR_Solver(r_0=r_0, r_f=r_f, ang=ang, gas=gas8, T5=T5, p5=p5, X=X )
            st.write(":green[**!NEq-Flow Rodou Corretamente!**]")
        except:
            st.write(":red[**!Erro em NEq-Flow!**]")

st.write("## Simulação 1D em Não-Equilíbrio ")
st.write("""A calculadora calcula
         1) as condições de estagnação de um tubo de choque, 
         2) as condições da garganta em equilíbrio dada a tubeira e 
         3) simula, da garganta em diante, em 1d o escoamento reativo estabelecido na tubeira.""")

## A Saída ----------------------------------------------------------------------------------------------

tab1, tab2 = st.tabs(["Saída dos Dados", "Informações"])
with tab1:
    st.write("### Tubo de Choque ")

    col1, col2 = st.columns(2)

    with col1:
        st.write("###### Informações Iniciais:")
        st.info(f"""Pressão, p1 :         {p1/1e3 : 4.4} kPa   \\
                Temperatura, T1 :         {T1 : .0f} K         \\
                Vel. Onda Incidente, us : {us : 5.5} m/s       \\
                Composição Inicial : {X1} 
                """)
        
        st.write("###### Condições de Estagnação:")

        st.info(f"""Pressão, p5 :     {p5/1e6 : 4.4} MPa       \\
            Temperatura, T5 :         {T5 : .0f} K             \\
            Entalpia Específica, h5 : {h5/1e6 : 4.2f} MJ/kg 
            """)


    with col2:
        k = np.argsort(gas8.X)[::-1]
        Xi = np.array(gas8.species_names)

        fig = px.bar( title='Concentrações de Espécies - Estagnação', x=Xi[k], y=100*gas8.X[k],height=350,width=600,labels=dict(x='Espécies', y='Fração Molar (%)'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
        fig.update_xaxes(title_font_family="Arial")
        st.plotly_chart(fig,use_container_width=True )

    #st.write(gas8.species_names[k])

    st.write("### Geometria da Tubeira")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.area(x=100*Reator.x, y= Reator.R(Reator.x), labels=dict(x='Posição Axial (cm)', y='Raio (cm)'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
        fig.update_xaxes(title_font_family="Arial")
        fig.update_traces(line={'width': 5},hoverlabel=dict(font_size=18))
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        fig = px.area(x=100*Reator.x, y= Reator.A(Reator.x),labels=dict(x='Posição Axial (cm)', y='Area (cm^2)'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20)) )
        fig.update_xaxes(title_font_family="Arial")
        fig.update_traces(line={'width': 5},hoverlabel=dict(font_size=18))
        st.plotly_chart(fig,use_container_width=True)
        
    st.write("### Saída da Tubeira")
    st.write("#### Parâmetros Termodinâmicos Calculados")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.area(title='Velocidade',x=100*Reator.states.x, y= Reator.states.Vel.astype('int'),labels=dict(x='Posição Axial (cm)', y='Velocidade (m/s)'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_xaxes(title_font_family="Arial")
        fig.update_traces(line={'width': 5},line_color='#147852',hoverlabel=dict(font_size=18))
        st.plotly_chart(fig,use_container_width=True)

        fig = px.area(title='Mach',x=100*Reator.states.x, y= np.round(Reator.states.Mach,2),labels=dict(x='Posição Axial (cm)', y='Número de Mach'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_xaxes(title_font_family="Arial")
        fig.update_traces(line={'width': 5},line_color='#018989',hoverlabel=dict(font_size=18))
        st.plotly_chart(fig,use_container_width=True)


    with col2:
        fig = px.area(title='Temperatura',x=100*Reator.states.x, y= Reator.states.T.astype('int'),labels=dict(x='Posição Axial (cm)', y='Temperatura (K)'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_xaxes(title_font_family="Arial")
        fig.update_traces(line={'width': 5},line_color='#910902',hoverlabel=dict(font_size=18))
        st.plotly_chart(fig,use_container_width=True)
        
        fig = px.area(title='Pressão',x=100*Reator.states.x, y= Reator.states.P.astype('int'),labels=dict(x='Posição Axial (cm)', y='Pressão (Pa)'))
        fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17), type="log") )
        fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=17)) )
        fig.update_xaxes(title_font_family="Arial")
        fig.update_traces(line={'width': 5},line_color='#186211',hoverlabel=dict(font_size=18))
        st.plotly_chart(fig,use_container_width=True)

    st.write("##### Tabela de Parâmetros Termodinâmicos Calculados")
    df = pd.DataFrame( data=np.column_stack(( Reator.states.Vel, Reator.states.Mach, Reator.states.T, Reator.states.P, Reator.states.density, 
                                            1e6*Reator.states.viscosity, Reator.states.cp_mass, Reator.states.cv_mass )),
                    columns=['Velocidade, m/s','Mach', 'Temperatura, K','Pressão (Pa)','Densidade, kg/m3',
                            'Viscosidade, 1E-6Pa-s', 'Cp, J/(K.Kg)','Cv, J/(K.Kg)' ]  )

    df.set_index( Reator.states.x ,inplace=True)
    df.index.set_names("Posição, m",inplace=True)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=True).encode('utf-8')
    st.download_button(
    "Download dos Parâmetros Termodinâmicos",
    csv,
    "NEq_Termo-Params.csv",
    "text/csv",
    key='download-csv'
    )

    st.write("#### Concentração de Espécies Químicas")
    df_X = 100*pd.DataFrame(Reator.states.X)
    df_X.columns = Reator.states.species_names
    df_X.set_index( Reator.states.x ,inplace=True)
    df_X.index.set_names("Posição, m",inplace=True)

    fig = px.line(df_X, title='Concentração de Espécies Químicas', labels={'index':'Posição Axial (cm)', 'value':'Fração Molar'} )
    fig.update_layout( yaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20), type="log" ),yaxis_range=[-3,2] )
    fig.update_layout( xaxis = dict(tickfont = dict(size=15),titlefont = dict(size=20) ) )
    fig.update_xaxes(title_font_family="Arial")
    fig.update_traces(line={'width': 10},hoverlabel=dict(font_size=20))
    st.plotly_chart(fig,use_container_width=True)

    st.write("##### Tabela de Espécies Químicas Calculadas")
    st.dataframe(df_X, use_container_width=True)

    csv_X = df_X.to_csv(index=True).encode('utf-8')
    st.download_button( "Download da Distribuição de Espécies Químicas",
                            csv_X,
                            "NEq_Especies.csv",
                            "text/csv",
                            key='download-csv_X'  )

with tab2:
    st.write('''##### O que é feito aqui?''')
    st.write('''Especifica-se as condições ''')
    st.write('''Inicialmente especifica-se por completo o tubo de choque a partir de informações do gás de driven e
             velocidade da onda de choque incidente (1,2). A pressçao de estagnação, se conhecida, pode ser usada também
             como dado de entrada; caso contrário, o campo associado pode ser preenchido com zero, e uma pressão p5 será estimada.''')
    
    st.write('''A partir da estagnação e dos dados inseridos referentes à geometria da tubeira, o código assume equilíbrio
             termodinâmico da entrada da tubeira até a garganta, que é então caracterizada.''')    
    
    st.write('''Por fim, o escoamento desenvolvido após a garganta é aproximado de um reator do tipo *plug flow*,
             que resolve equações diferenciais estacionárias de conservação momento, energia, massa e de espécies, que são (3,4):''')    
    
    st.latex(r'''\frac{d\rho}{dx} = \frac{ \left( 1 - \frac{R_U}{c_p MW_{mix}} \right)\rho^2v_x^2\left( \frac{1}{A}\frac{dA}{dx}\right)  + \frac{\rho R_U}{v_x c_p MW_{mix}}\sum_i MW_i \dot{\omega_i} \left( h_i - \frac{MW_{mix}}{MW_i}c_p T \right)}{P\left( 1 + \frac{v_x^2}{c_p T}\right) - \rho v_x^2 }''')
    st.latex(r'''\frac{dT}{dx} = \frac{v_x^2}{\rho c_p}\frac{d\rho}{dx} +  \frac{v_x^2}{c_p}\left( \frac{1}{A}\frac{dA}{dx}\right) - \frac{1}{v_x \rho c_p } \sum_i h_i MW_i  \dot{\omega_i}''')
    st.latex(r'''\frac{dY_i}{dx} = \frac{\omega_i MW_i}{\rho v_x}''')

    st.write(''' De acordo com (4), um reator do tipo *plug-flow* representa um reator ideal que possui as seguintes características:\\
             1 - fluxo estacionário;\\
             2 - sem mistura na direção axial: a difusão de massa molecular e/ou turbulenta é insignificante na direção do fluxo;\\
             3 - propriedades uniformes na direção perpendicular ao fluxo, ou seja, fluxo unidimensional: isso significa que em qualquer seção transversal, um único conjunto definido por velocidade, temperatura, composição, etc., é suficiente para caracterizar localmente o fluxo;\\
             4 - fluxo ideal sem atrito: usa-se da simples equação de Euler para relacionar pressão e velocidade;\\
             5 - comportamento de gás ideal: permite-se o uso de euações de estado mais simples para relacionar $T$, $P$, $ρ$, $Y_i$, $h$ e $\omega_i$.''')


    st.write('''###### Referências''')
    st.write('''1 - Matos, P.A.S., Velocimetria a Laser em Túnel de Choque Hipersônico. Tese de Doutorado – ITA, 2018.\\
                2 - Ribeiro, L.A.G, Semi-Empirical Study of The Air Mass Flow Rate Captured by a Supersonic Combustor. Disertação de Mestrado - ITA, 2022.\\
                3 - General Plug Flow Reactor,Ashwin Kumar and Dr.Joseph Meadows, https://cantera.org/examples/matlab/Plug_Flow_Reactor.m.html . \\
                4 - Turns, S. R., An introduction to combustion: concepts and applications, third edition. ed., McGraw-Hill series in mechanical engineering, McGraw-Hill, New York, 2012.''')

