## Escoamento em Não Equilíbrio [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://neq-flow.streamlit.app/)

### Objetivo
Estimar concentrações de espécies químicas à saída de uma tubeira cônica acoplada a um tubo de choque.

### Como?
Inicialmente especifica-se por completo o tubo de choque a partir de informações do gás de driven e velocidade da onda de choque incidente (1,2). A pressçao de estagnação, se conhecida, pode ser usada também como dado de entrada; caso contrário, o campo associado pode ser preenchido com zero, e uma pressão p5 será estimada.
    
A partir da estagnação e dos dados inseridos referentes à geometria da tubeira, o código assume equilíbrio termodinâmico da entrada da tubeira até a garganta, que é então caracterizada.   
    
Por fim, o escoamento desenvolvido após a garganta é aproximado de um reator do tipo *plug flow*, que resolve equações diferenciais estacionárias de conservação momento, energia, massa e de espécies, que são (3,4):    
    
$$ \frac{d\rho}{dx} = \frac{ \left( 1 - \frac{R_U}{c_p MW_{mix}} \right)\rho^2v_x^2\left( \frac{1}{A}\frac{dA}{dx}\right)  + \frac{R_U}{v_x c_p MW_{mix}}\sum_i MW_i \dot{\omega_i} \left( h_i - \frac{MW_{mix}}{MW_i}c_p T \right)} {P\left( 1 + \frac{v_x^2}{c_p T}\right) - \rho v_x^2 } $$


$$\frac{dT}{dx} = \frac{v_x^2}{\rho c_p}\frac{\rho}{dx} +  \frac{v_x^2}{c_p}\left( \frac{1}{A}\frac{dA}{dx}\right) - \frac{1}{v_x c_p } \sum_i h_i MW_i  \dot{\omega_i}$$

$$\frac{dY_i}{dx} = \frac{\omega_i MW_i}{\rho v_x}$$

Para o particular caso de *equilíbrio isentrópico*, é forçado o equilíbrio termodinâmico a cada passo de itera para especificação dos parâmetros termodinâmicos e manutenção da entropia. Já para o caso *congelado isentrópico*, anulam-se todas as taxas $w_i$ de formação de espécies.

De acordo com (4), um reator do tipo *plug-flow* representa um reator ideal que possui as seguintes características:
        1 - fluxo estacionário;\
        2 - sem mistura na direção axial: a difusão de massa molecular e/ou turbulenta é insignificante na direção do fluxo;\
        3 - propriedades uniformes na direção perpendicular ao fluxo, ou seja, fluxo unidimensional: isso significa que em qualquer seção transversal, um único conjunto definido por velocidade, temperatura, composição, etc., é suficiente para caracterizar localmente o fluxo;\
        4 - fluxo ideal sem atrito: usa-se da simples equação de Euler para relacionar pressão e velocidade;\
        5 - comportamento de gás ideal: permite-se o uso de euações de estado mais simples para relacionar $T$, $P$, $ρ$, $Y_i$, $h$ e $\omega_i$.


### Referências
1 - Matos, P.A.S., Velocimetria a Laser em Túnel de Choque Hipersônico. Tese de Doutorado – ITA, 2018\
2 - Ribeiro, L.A.G, Semi-Empirical Study of The Air Mass Flow Rate Captured by a Supersonic Combustor. Disertação de Mestrado - ITA, 2022.\
3 - General Plug Flow Reactor, Ashwin Kumar and Dr.Joseph Meadows, https://cantera.org/examples/matlab/Plug_Flow_Reactor.m.html . \
4 - Turns, S. R., An introduction to combustion: concepts and applications, third edition. ed., McGraw-Hill series in mechanical engineering, McGraw-Hill, New York, 2012.

