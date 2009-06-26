
COMMENT

Kd3h5.mod

Potassium channel, Hodgkin-Huxley style kinetics
Kinetic rates based roughly on Sah et al. and Hamill et al. (1991)

Use with na3h5.mod

Author: Zach Mainen, Salk Institute, 1994, zach@salk.edu
	
ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	SUFFIX kd3
	USEION k READ ek WRITE ik
	RANGE n, gk, gbar
	RANGE ninf, ntau
	GLOBAL Ra, Rb
	GLOBAL q10, temp, tadj, vmin, vmax
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 300   	(pS/um2)	: 0.03 mho/cm2
	v 		(mV)
								
	tha  = 20	(mV)		: v 1/2 for inf
	qa   = 9	(mV)		: inf slope		
	
	Ra   = 0.02	(/ms)		: max act rate
	Rb   = 0.002	(/ms)		: max deact rate	

	dt		(ms)
	celsius		(degC)
	temp = 16	(degC)		: original temp 	
	q10  = 2.3			: temperature sensitivity

	vmin = -120	(mV)
	vmax = 100	(mV)
} 


ASSIGNED {
	a		(/ms)
	b		(/ms)
	ik 		(mA/cm2)
	gk		(pS/um2)
	ek		(mV)
	ninf
	ntau (ms)	
	tadj
}
 

STATE { n }

INITIAL { 
	trates(v)
	n = ninf
}

BREAKPOINT {
        SOLVE states
	gk = gbar*n
	ik = (1e-4) * gk * (v - ek)
} 

LOCAL nexp

PROCEDURE states() {   :Computes state variable n 
        trates(v)      :             at the current v and dt.
        n = n + nexp*(ninf-n)
        VERBATIM
        return 0;
        ENDVERBATIM
}

PROCEDURE trates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL tinc
        TABLE ninf, nexp
	DEPEND dt, celsius, temp, Ra, Rb, tha, qa
	
	FROM vmin TO vmax WITH 199

	rates(v): not consistently executed from here if usetable_hh == 1

        tadj = 3^((celsius - temp)/10)

        tinc = -dt * tadj
        nexp = 1 - exp(tinc/ntau)
}


PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.

        a = Ra * (v - tha) / (1 - exp(-(v - tha)/qa))
        b = -Rb * (v - tha) / (1 - exp((v - tha)/qa))
        ntau = 1/(a+b)
	ninf = a*ntau
}

