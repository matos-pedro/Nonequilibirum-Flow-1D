import cantera as ct
import numpy as np
import scipy.integrate
from scipy import optimize
from scipy.interpolate import interp1d as i1d
from scipy.interpolate import UnivariateSpline as us1d


class PFR_Ode:
    def __init__(self, gas, mdot, A_x, dAdx_x):
        self.gas  = gas
        self.mdot = mdot
        self.A_x = A_x
        self.dAdx_x = dAdx_x

    def __call__(self, x, Y):  

        self.gas.TDY = Y[0], Y[1], Y[2::]

        rho = self.gas.density
        T   = self.gas.T
        y   = self.gas.Y
        A    = self.A_x
        dAdx = self.dAdx_x
       
        MW_mix = self.gas.mean_molecular_weight
        Rnd    = ct.gas_constant/(self.gas.cp_mass*MW_mix) # non-dimensional R = 1 - cp/cv
        
        ux = self.mdot/(rho*(A(x)))

        P = rho*(ct.gas_constant/MW_mix)*T

        MW = self.gas.molecular_weights
        h  = self.gas.standard_enthalpies_RT*(ct.gas_constant/MW_mix)*T
        w  = self.gas.net_production_rates
        cp = self.gas.cp_mass
            
        drhodx = (((rho*ux)**2.)*(1.-Rnd)*(dAdx(x)/A(x))+(rho/ux)*Rnd*np.sum(MW*w*(h-(MW_mix/MW)*cp*T)))/(P*(1.+ux**2./(cp*T)) - rho*ux**2.)
        dTdx   = (ux**2./cp)*(drhodx/rho +  dAdx(x)/A(x)) - np.sum(h*w*MW)/(ux*rho*cp)   
        dYdx   =  w*MW/(rho*ux)
                                   
        return np.hstack((dTdx, drhodx, dYdx))


class PFR_Solver:
    def __init__(self, **kargs):
        self.Tubeira(**kargs)
        self.Garganta(**kargs)
        self.Solver()

    
    def Tubeira(self, **kargs):
        x_0 = 0
        x_f = (kargs['r_f'] - kargs['r_0'])/np.tan(np.pi*kargs['ang']/180.)

        self.x = np.linspace(x_0, x_f, 50)
        self.r = np.linspace(kargs['r_0'], kargs['r_f'], 50)

        self.A = us1d( self.x, np.pi*self.r**2.0, k=3 )
        self.R = us1d( self.x, self.r, k=3 )
        self.dAdx = self.A.derivative()    

    def Garganta(self,**kargs):
        self.gas = kargs['gas']
        self.T5  = kargs['T5']
        self.p5  = kargs['p5']
        self.X   = kargs['X']

        self.gas.TPX = self.T5, self.p5, self.X
        self.gas.equilibrate('TP')
        
        s5 = self.gas.entropy_mass
        g5 = self.gas.cp/self.gas.cv
        h5 = self.gas.h
        pg = self.p5*((1+0.5*(g5-1))**(-g5/(g5-1)))

        # Encontrando Pressão na Garganta -------------------------------------------------------------------
        def acha_pg(p):
            self.gas.SP = s5, p
            self.gas.equilibrate('SP')
            hg = self.gas.h
            vg = (2.0*(h5-hg))**0.5
            ag = np.sqrt( (self.gas.cp/self.gas.cv)*(ct.gas_constant/self.gas.mean_molecular_weight)*self.gas.T )
            return  (vg-ag)**2 
        
        rranges = (slice(pg*0.8, pg*1.2, pg/100.0 ),)
        resbrute = optimize.brute(acha_pg, rranges, full_output=True, finish=optimize.fmin)
        pg = resbrute[0]
        #----------------------------------------------------------------------------------------------------



        self.gas.SP = s5, pg
        self.gas.equilibrate('SP')
        gas_0 = self.gas

        r0 = gas_0.density
        g0 = gas_0.cp/gas_0.cv
        T0 = gas_0.T
        h0 = gas_0.enthalpy_mass

        self.mdot = 1.01*r0*np.sqrt( g0*(ct.gas_constant/gas_0.mean_molecular_weight)*T0 )*self.A(0)
        u0 = self.mdot/(r0*self.A(0))
        M0 = u0/( np.sqrt(g0*(ct.gas_constant/gas_0.mean_molecular_weight)*T0)  )

        self.states = ct.SolutionArray(self.gas, 1, extra={ 'x':[0], 'tempo':[0], 'dt':[0], 'Mach':[M0], 'Vel':[u0], 'Enthalpy':[h0], 'Gamma':[g0]   })
        self.Y0 = np.hstack((self.gas.T, self.gas.density,  self.gas.Y))
    
    
    def Solver(self):
        gas    = self.gas
        ode    = PFR_Ode(self.gas, self.mdot,self.A,self.dAdx)        #objeto
        solver = scipy.integrate.ode(ode)  #objeto

        solver.set_integrator(name='vode', method='bdf', with_jacobian=True)
        solver.set_initial_value(self.Y0,0)

        dx, x_end = 1e-3, self.x[-1] #Passo e comprimento total da tubeira

        tempo = 0
        for x in np.arange(dx,x_end+dx,dx): 

            try:
                solver.integrate(x)  
            except:     
                print('Erro em x = ', x)
                    
            gas.TDY = solver.y[0], solver.y[1], solver.y[2::]
            
            #outros parametros
            hx      = gas.enthalpy_mass    
            ux      = self.mdot/(self.A(x)*gas.density) 
            MW_mix  = gas.mean_molecular_weight
            gamma   = gas.cp/self.gas.cv
            a_sound = np.sqrt( gamma*(ct.gas_constant/MW_mix)*gas.T )     
            Mach    = ux/a_sound
            tempo   = tempo + dx/ux
            

            self.states.append(gas.state,  x=solver.t, tempo=tempo, dt=dx/ux, Mach=Mach, Vel=ux, Enthalpy=hx, Gamma=gamma)
            
                
