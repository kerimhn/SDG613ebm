#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programmet definerer noen konstanter 
(som tykkelse av blandingslag og verdenshavene, og varmekapasitet)
Strålingspådrivet, sammen med tilbakekoblingseffekter og 
varmeutveksling med dyphavet brukes til å beregne hvordan temperaturanomaliene (temperaturendringer 
fra start verdi) utvikler seg.
"""
import numpy as np

def calculate_temp_anomalies(radiative_forcing, lambda_sum, gamma):
   
    H_MIX= 100 # tykkelse av blandingslaget [m]
    H_DEEP=3700-H_MIX # gjennomsnitts tykkelse av dyphavet [m]   
    RHO = 1000 # vannets tetthet (kg m-3)
    CPO = 4200  # spesifikk varmekapasitet for vann(J kg-1 K-1)       
    f_o=0.7  # andel av jordens overflate dekket av vann
    
    Dt=365*24*60*60 # steglenge i modellen - 1 år i sekund
    
    # effektiv varmekapasitet for atmosfære-hav-systemet [J m-2 K-1]
    # Hvor mye energi skal til for å heve en vannsøyle med grunnflate en kvadratmeter og høyde   
    # tilsvarende havdybden en grad.  
    
    CEFF_M=f_o*H_MIX*CPO*RHO 
    CEFF_D=f_o*H_DEEP*CPO*RHO
    
   
    Ts=np.array([0]) #Starter temperaturseriene med temperaturen første år. 
    To=np.array([0])
    
    for t in range(1,len(radiative_forcing)):
        # --------------
        # Temperatur tendenser (den deriverte) [K/s]
        #     dTs/dt, dTo/dt
        # --------------
        dTs_dt=(radiative_forcing[t]+(lambda_sum*Ts[t-1])+(gamma*(Ts[t-1]-To[t-1])))/CEFF_M
        dTo_dt=-gamma*(Ts[t-1]-To[t-1])/CEFF_D
        
        # ----------------------------------------------------------------------
        # Antar konstant temperaturendring i løpet av et år, regner ut ny temperatur
        # ved hjelp av Eulermetoden og oppdaterer temperaturarrayene
        #----------------------------------------------------------------------
        Ts=np.append(Ts, Ts[t-1]+dTs_dt*Dt)
        To=np.append(To, To[t-1]+dTo_dt*Dt)
    return Ts, To
