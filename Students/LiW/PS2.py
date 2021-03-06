
#import packages
import numpy as np
import scipy.optimize as opt
import math
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os


'''
Check the feasibility of an initial guess for the steady-state with 
constraints of K > 0 and c_s > 0 for all s

Variables:
		K([b_2, b_3]) = aggregate capital stock
		r([b_2, b_3]) = interest rate
		w([b_2, b_3]) = real wage
		cvec        = consumption c_s for all s in S
		b_cnstr     = True if b_s >= 0
		K_cnstr     = True if K >= 0
		c_cnstr     = True if c >= 0
		feasibility = True if bvec is feasible

Returns: feasibility, K_cnstr, b_cnstr, c_cnstr
'''

# Inputs

S      = [1, 2, 3]
A      = 1                      # total factor productivity Cobb-Douglas production function
alpha  = 0.35                   # capital share of income in production function
delta  = 0.6415                 # 20-year depreciation rate of capital
beta   = 0.442					# 20-year discount factor
nvec   = np.array([1, 1, .2])   # exogenous labor supply n_s
L      = nvec.sum()             # aggregate labor        
sigma  = 3
SS_tol = math.e ** (-13)



# K
def K(bvec):
	'''
	Inputs:
		bvec = np.array([b_2, b_3])
  
	Return:
		K(bvec) = b_2 + b_3
	'''
	K = np.sum(bvec)
	return K

# w
def w(bvec, alpha, A):
	'''
	Inputs:
		alpha, A
		L = L(nvec)
		K = K(bvec)

	Returns:
		w = (1 - alpha) * A * (K / L) ** alpha
	'''
	w = (1 - alpha) * A * (K(bvec) / L) ** alpha
	return w
	
# r
def r(bvec, nvec, alpha, A, delta):
	'''
	Inputs:
		alpha, A, delta
		L = L(nvec)
		K = K(bvec)

	Return:
		r = alpha * (L / K) ** (1 - alpha) - delta
	'''
	r = alpha * (L / K(bvec)) ** (1 - alpha) - delta
	return r
 
# set up c_s = [c_1, c_2, c_3]
def  c_s(bvec, alpha, A, delta):
	'''
	Inputs:c
		params = alpha, A, , delta
		w = w(bvec, params)
		r = r(bvec, params)
		L = L(nvec)
		K = K(bvec)

	Return:
		c_s  = np.array([c_1, c_2, c_3])
	'''
 
	nvec = np.array([1, 1, .2]) 
	w0 = w(bvec, alpha, A)
	r0 = r(bvec, nvec, alpha, A, delta)
	b2 = bvec[0]
	b3 = bvec[1]
	
	cvec = np.zeros(3)
	for i in range(3):
         cvec[i] = w0*nvec[i] + (1+r0)*b2 - b3

	return cvec

# Y
def  Y(bvec, alpha, A):
	'''
	Inputs:
		A, alpha
		K = K(bvec)
		L = L(bvec)

	Return:
		Y = A * K ** alpha * L ** (1 - alpha)
	'''
	Y = A * K(bvec) ** alpha * L ** (1 - alpha)
	return Y

# feasibility
def feasible(S, alpha, A, delta, nvec, bvec):
	
	# compute K and c_s

	c = c_s(bvec, alpha, A, delta)

	# check K
	K_cnstr = K(bvec) <= 0
	if K_cnstr == True:
		feasible = False

	# check cvec
	c_cnstr = [c[0] <= 0, c[1] <=0, c[2] <= 0]

	# check bvec
	# Set b_cnstr to all False
	b_cnstr = [False, False]
	# if c_1 <= 0, c_cnstr == Ture, b_cnstr[0] == True
	if c_cnstr[0] == True:
		b_cnstr[0] == True
	print ("c_1 not feasible, b_2 not feasible")

	# if c_3 <= 0. c_cnstr == Ture, b_cnstr[1] == True
	if c_cnstr[2] == True:
		b_cnstr[1] == True
	print ("c_3 not feasible, b_3 not feasible")
		
	# if c_2 <=0, c_cnstr == True, b_cnstr = [True, True]
	if c_cnstr[1] == True:
		b_cnstr = [True, True]
	print ("c_2 not feasible, both b_2 and b_3 not feasible")

	feasible = (b_cnstr, c_cnstr, K_cnstr)
	return feasible

print ("#1 Checking feasibility")
print ("feasibility of [1, 1.2]", feasible(S, alpha, A, delta, nvec, np.array([1.0, 1.2])))
print ("feasibility of [.06, -.001]", feasible(S, alpha, A, delta, nvec, np.array([0.06, -0.001])))
print ("feasibility of [.1, .1]", feasible(S, alpha, A, delta, nvec, np.array([0.1, 0.1])))
 
 
	
# Euler Error Function
	
def EulErr_ss(bvec, *arg):
	'''
	sigma
	beta
	K = K(bvec)
	L = L(nvec)
	w = w(bvec, alpha, A)
	r = r(bvec, nvec, alpha, A, delta)
	'''
	arg = alpha, A, delta, sigma
	w0 = w(bvec, alpha, A)
	r0 = r(bvec, nvec, alpha, A, delta)
	b_2 = bvec[0]
	b_3 = bvec[1]

	#marginal utilities
	mu = np.zeros(3)
	mu[0] = (w0 - b_2) ** (-sigma)
	mu[1] = (w0 + (1 + r0) * b_2 - b_3) ** (-sigma)
	mu[2] = (nvec[2] * w0 + (1 + r0) * b_3) ** (-sigma)

	# Euler Errors
	EulErr_ss = np.zeros(2)
	EulErr_ss[0] = beta * (1+r0) * mu[1] ** (-sigma) -  mu[0] ** (-sigma)
	EulErr_ss[1] = beta * (1+r0) * mu[2] ** (-sigma) -  mu[1] ** (-sigma)
	
	return EulErr_ss

def get_SS(beta, sigma, L, A, alpha, bvec_guess, nvec, SS_graphs):
	start_time = time.clock()
     
	# Values at steady states
	# savings
	b_ss = opt.fsolve(EulErr_ss, bvec_guess, args=(beta, sigma, L, A, alpha), xtol = SS_tol)
	# aggregate capital
	K_ss = K(b_ss)
	# interest rate
	r_ss = r(bvec_guess, nvec, alpha, A, delta)
	# real wages
	w_ss = w(bvec_guess, alpha, A)
	# consumption
	c_ss = c_s(bvec_guess, alpha, A, delta)
	# production
	Y_ss = Y(bvec_guess, alpha, A)
	# resource constraint error
	RCerr_ss = Y_ss - c_ss.sum() - delta * K_ss

	elapsed_time = time.clock() - start_time

 # ploting graphs
	if SS_graphs == True:
		period = [1, 2, 3]
		plt.plot(period, c_ss, '^-', label = 'beta = '+format(beta)+ \
			' Consumption')
		plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		plt.plot(period, np.concatenate((np.array([0]), b_ss)), 'o-', label= \
			'beta =' + format(beta) + ' Capital')
		plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		plt.grid(b=True, which='major', color='0.65', linestyle='-')
		plt.show()

	ss_output = {'b_ss': b_ss, 'c_ss': c_ss, 'w_ss': w_ss, 'r_ss': r_ss, 'K_ss': K_ss, 'Y_ss': Y_ss, 'EulErr_ss': EulErr_ss(b_ss, ), 'RCerr_ss': RCerr_ss, 'ss_time': elapsed_time}
	return ss_output

bvec_guess = np.array([.1, .1])
print("#2 steady-state outputs")
print("ss_output = ", get_SS(beta, sigma, L, A, alpha, bvec_guess, nvec, "True"))

def print_time(seconds):
    '''
    --------------------------------------------------------------------
    Takes a total amount of time in seconds and prints it in terms of
    more readable units (days, hours, minutes, seconds)
    --------------------------------------------------------------------
    INPUTS:
    seconds = scalar > 0, total amount of seconds

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:

    OBJECTS CREATED WITHIN FUNCTION:
    secs = scalar > 0, remainder number of seconds
    mins = integer >= 1, remainder number of minutes
    hrs  = integer >= 1, remainder number of hours
    days = integer >= 1, number of days

    RETURNS: Nothing
    --------------------------------------------------------------------
    '''
    if seconds < 60:  # seconds
        secs = round(seconds, 4)
        print('SS computation time: ' + str(secs) + ' sec')
    elif seconds >= 60 and seconds < 3600:  # minutes
        mins = int(seconds / 60)
        secs = round(((seconds / 60) - mins) * 60, 1)
        print('SS computation time: ' + str(mins) + ' min, ' +
              str(secs) + ' sec')
    elif seconds >= 3600 and seconds < 86400:  # hours
        hrs = int(seconds / 3600)
        mins = int(((seconds / 3600) - hrs) * 60)
        secs = round(((seconds / 60) - hrs * 60 - mins) * 60, 1)
        print('SS computation time: ' + str(hrs) + ' hrs, ' +
              str(mins) + ' min, ' + str(secs) + ' sec')
    elif seconds >= 86400:  # days
        days = int(seconds / 86400)
        hrs = int(((seconds / 86400) - days) * 24)
        mins = int(((seconds / 3600) - days * 24 - hrs) * 60)
        secs = round(
            ((seconds / 60) - days * 24 * 60 - hrs * 60 - mins) * 60, 1)
        print('SS computation time: ' + str(days) + ' days, ' +
              str(hrs) + ' hrs, ' + str(mins) + ' min, ' +
              str(secs) + ' sec')





# TPI

# b_ss
b_ss = opt.fsolve(EulErr_ss, bvec_guess, args=(beta, sigma, L, A, alpha), xtol = SS_tol)
print ("b_ss = ", b_ss)


SS = get_SS(beta, sigma, L, A, alpha, bvec_guess, nvec, "False")
nvec = np.array([1 , 1, .2])
T = 30
A = 1
alpha = 0.35
beta = 0.442
delta = 0.6415
sigma = 3
L = nvec.sum()

# Kpath0
'''
K1 = initial aggregate capital
K_ss = steady state K
T_guess = 30
Kpath0 = [T,] vector, initial guess for time path of K
Kpath1 = [T-1,] vector, time path for K with optimised b

'''

KT = b_ss.sum()
b_init = np.array([.8 * b_ss[0], 1.1 * b_ss[1]])
K1 = b_init.sum()

# get Kpath0
def get_Kpath0(K1, KT, T, spec):
    '''
    #from GitHub

    --------------------------------------------------------------------
    This function generates a path from point K1 to point KT such that
    that the path K is a linear or quadratic function of time t.

        linear:    K = d*t + e
        quadratic: K = a*t^2 + b*t + c

    The identifying assumptions for quadratic are the following:

        (1) K1 is the value at time t=0: K1 = bvec_guess[0] + bvec_guess[1]
        (2) KT is the value at time t=T-1: KT = a*(T-1)^2 + b*(T-1) + K1
        (3) the slope of the path at t=T-1 is 0: 0 = 2*a*(T-1) + b
    --------------------------------------------------------------------
    INPUTS:
    K1 = scalar, initial value of the function K(t) at t=0
    KT = scalar, value of the function K(t) at t=T-1
    T  = integer >= 3, number of periods of the path
    spec = string, "linear" or "quadratic"

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:

    OBJECTS CREATED WITHIN FUNCTION:
    cc    = scalar, constant coefficient in quadratic function
    bb    = scalar, coefficient on t in quadratic function
    aa    = scalar, coefficient on t^2 in quadratic function
    Kpath0 = (T,) vector, parabolic Kpath from K1 to KT

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: Kpath0
    --------------------------------------------------------------------
    '''

    if spec == "linear":
        Kpath0 = np.linspace(K1, KT, T)
    elif spec == "quadratic":
        cc = K1
        bb = 2 * (KT - K1) / (T - 1)
        aa = (K1 - KT) / ((T - 1) ** 2)
        Kpath0 = aa * (np.arange(0, T) ** 2) + (bb * np.arange(0, T)) + cc

    return Kpath0
    
    
# get wt 
'''
'''
Kpath0 = get_Kpath0(K1,KT,T,"quadratic")
def wt(alpha, A, L):
    wt = []
    for t in range(T):
        w = (1 - alpha) * A * (Kpath0[t] / L) ** alpha
        wt.append(w)
    return wt


# get rt
def rt(alpha, A, L, delta):
    rt = []
    for t in range(T):
        r = alpha * A * (L / Kpath0[t]) ** (1 - alpha) - delta
        rt.append(r)
    return rt
    
# get bvec(b(2,t), b(3,t+1))
'''
f1 = mu(c(1,t-1)) - beta * (1+r(t)) * mu(c(2,t))
f2 = mu(c(2,t)) - beta * (1+r(t+1)) * mu(c(3,t+1))
'''
def f1(bvec, t):
    b2 = bvec[0]
    b3 = bvec[1]
    w = wt(alpha, A, L)
    r = rt(alpha, A, L, delta)
    T = 30
    f = np.zeros(2)
    f[0] = (w[t-2]-b2)**(-sigma)-beta*(1+r[t-1])*(w[t-1]+(1+r[t-1])*b2\
-b3)**(-sigma)
    f[1] = (w[t-1]+(1+r[t-1])*bvec[0]-b3)**(-sigma)-\
beta*(1+r[t])*((1+r[t])*b3+0.2*w[t])**(-sigma)
    return f

bvec = []
for t in range(T):
    b = opt.fsolve(f1, [.1, .1], t)
    bvec.append(b)



# compute b(3,2)
'''
mu(c(2,1)) = beta * (1+r2) * mu(c(3,2))
'''

def f2(b_32, *arg):
    w = wt(alpha, A, L)
    r = rt(alpha, A, L, delta)
    f2 = (w[0]+(1+r[0])* b_init[0] - b_32)**(-sigma)-beta*(1+r[1])*\
((1+r[1])*b_32+0.2*w[1])**(-sigma)
    return f2
    
b_guess = np.sum(b_init)/2

b_32 = opt.fsolve(f2, b_guess , args = (alpha, A, delta), xtol = math.e ** (-9))
print ("b_32 = ", b_32)


# get Kpath1
'''
Kpath1 = [KK1, KK2,..., KKT]
KKt = b(2,t) + b(3,t)
t in range(T)
b(2,t) = bvec[t][0]
b(3,t) = bvec[t-1][1]

'''
Kpath1 = []
for t in range(T):
    b_2t = bvec[t][0]
    b_3t = bvec[t-1][1]
    KKt = b_2t + b_3t
    Kpath1.append(KKt)
    

# compute the norm
'''
norm = (Kt - KKt) ** 2
while iter < 200 and norm > 1e**(-9)
    iter += 1

'''

def dist(Kpath0, Kpath1):
    Kpath0 = get_Kpath0(K1, KT, T, "quadratic")
    dist = np.zeros(T)
    for t in range(T):
        dist[t] += (Kpath1[t] - Kpath0[t]) ** 2
    return dist.sum()

 
# iteration
'''
iter = 1
xi = 0.2
if any(dco) > math.e**(-9):
    iter += 1
    Kpath1_prime[t] = xi * Kpath1[t] + (1 - xi) * Kpath0[t]
print ('iter: ', iter, ', dist: ', d)
'''
        

    
    

    

















