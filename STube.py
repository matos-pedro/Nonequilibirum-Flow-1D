## encoding: utf-8
import numpy as np
import cantera as ct


def Shock12(t1, p1, us, X):
    gas1 = ct.Solution('./Data/Redlich-Kwong_Air.yaml')
    gas1.TPX = t1,p1,X
    gas1.equilibrate('TP')

    r1 = gas1.density                                                                    #calcula densidade
    h1 = gas1.enthalpy_mass                                                              #calcula entalpia
    Ms = us/np.sqrt((gas1.cp/gas1.cv)*(ct.gas_constant/gas1.mean_molecular_weight)*t1)   #estima Ms

    r2 = r1*10

    for i in np.arange(20):                        #processo iterativo para encontrar condicoes apos onda 
        p2 = p1 +  r1*us*us*(1.0 - r1/r2        )  #de choque
        h2 = h1 + 0.5*us*us*(1.0 - (r1/r2)**2.0 )

        gas1.HP = h2,p2
        gas1.equilibrate('HP')
        r2 = gas1.density
    
    u2 = us*(1.-r1/r2)
    return gas1, u2

def Shock25(gas2, u2):
    p2 = gas2.P
    r2 = gas2.density
    h2 = gas2.enthalpy_mass

    r5 = r2*10.0
    for i in np.arange(20):
        vr = u2/(r5/r2  -  1.)
        p5 = p2 +  r2*(vr + u2)*(vr + u2)*( 1. - r2/r5 )
        h5 = h2 + 0.5*(p5 - p2)*( 1./r2 + 1./r5 )

        gas2.HP = h5,p5
        gas2.equilibrate('HP')
        r5 = gas2.density
    return gas2


def Shock5E(gas5,p8,p5):
    if p8 == 0:
        p8 = p5
    
    gas5.SP = gas5.entropy_mass, p8
    gas5.equilibrate('SP')
    return gas5
    

def STube_Calc(T1, p1, us, p8, X):   
    gas2,u2 = Shock12(T1,p1,us,X)
    gas5    = Shock25(gas2,u2)
    gas8    = Shock5E(gas5,p8,gas5.P)
    return gas8