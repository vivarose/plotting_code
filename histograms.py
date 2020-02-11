import numpy as np

## https://stackoverflow.com/questions/32765333/how-do-i-replicate-this-matlab-function-in-numpy/32765547#32765547
def histc(X, bins):
    map_to_bins = np.digitize(X,bins)
    r = np.zeros(bins.shape)
    for i in map_to_bins:
        r[i-1] += 1
    return [r, map_to_bins]


"""
cumulative distribution function, the integral of a histogram
"""
def CDF(S):
    M = len(S); # size of array = number of elements
    sorteddata = sort(S); # ascending sort is CDF, descending sort is 1-CDF
    cum_prob = [elem/M for elem in range(M)] # probability integrated from 0 to sorteddata.
    cum_prob2 = [1-p for p in cum_prob] # probability integrated from sorteddata to inf
    return sorteddata,cum_prob2

"""
nonlinearhistc allows you to make a histogram with a logarithmic (or other nonlinear) set of bins.
by Viva Horowitz, 2018

example usage:

onbins=np.logspace(np.log10(min(ontimes)-small),np.log10(max(ontimes)+small), numonbins_log)
onprobs, _ = nonlinearhistc(ontimes, onbins) 
"""
def nonlinearhistc(X,bins, thresh=3, verbose = False):
    map_to_bins = np.digitize(X,bins)
    r = np.zeros(bins.shape)
    for i in map_to_bins:
        r[i-1] += 1
    if verbose:
        print r 
        #print bins
    ## normalize by bin width
    probability = np.zeros(bins.shape)
    area = 0;
    thinbincount = 0
    for i in range(len(bins)-1):
        if r[i]<=1:
            thinbincount += 1;
        thisbinwidth = bins[i+1] - bins[i]
        probability[i] = r[i]/thisbinwidth
        area += probability[i]*thisbinwidth;
        
    if thinbincount > thresh:
        print("Warning: too many bins for data, thinbincount=" + str(thinbincount))
    elif verbose:
        print("thinbincount=" + str(thinbincount))
    ## normalize area.
    normedprobability = [eachprobability / area for eachprobability in probability]
    return normedprobability, map_to_bins
