# -*- coding: utf-8 -*-
"""
"""

from mmc import MMC
import random as r
from operator import itemgetter
import numpy as np
import math as m
import matplotlib.pyplot as plt


def make_choice(p):
    '''chooses an action from a set with discrete cumulative distribution p.
    Returns index of p based on a generated random number.  Index corresponds
    to an action for that set'''
    
    n = r.random()
    i=0
    
    while p[i] < n:
        i+=1

    return i
    

if __name__ == '__main__':
    #simulation will start upon execution of file
    
    depart_prob = np.cumsum([.05,.95]) #probabiilty of [leaving,staying]
    
    '''The baseline transition matrix'''
#    block_prob = np.cumsum([[.05,.95,0,0],
#                             [0,.05,.95,0],
#                             [0,0,.05,.95],
#                             [.95,0,0,.05]],axis=1) #transition probability beween blocks
    
    ''' The "Busy" time transition matrix '''
    #1 is the popular/busy block, make expensive
    #2 is average
    #3 is unpopular "far away", make cheap
    #4 is average
    block_prob = np.cumsum([[0,.4,.2,.4],
                             [0,.05,.85,.1],
                             [0,.5,.05,.45],
                             [0,.1,.85,.05]],axis=1)
    
    #block parameters
    num_blocks = 4
    block_sizes = [10,10,10,10]
    lambdas = [15,15,15,15]
    mus = [1,2,2,2]
    
    '''uniform travel times'''
#    travel_times = [[1,1,1,1],
#                    [1,1,1,1],
#                    [1,1,1,1],
#                    [1,1,1,1]]
#    
    
    '''baseline travel times'''
#    travel_times = [[2*block_sizes[1]*block_sizes[2]*block_sizes[3], ,None,None],
#                    [None,2*block_sizes[2]*block_sizes[3]*block_sizes[0],1,None],
#                    [None,None,2*block_sizes[3]*block_sizes[0]*block_sizes[1],1],
#                    [1,None,None,2*block_sizes[0]*block_sizes[1]*block_sizes[2]]]
        
    '''travel times when circling to any block permitted'''
    travel_times = [[30,1,10,20],
                [20,30,1,10],
                [10,20,30,1],
                [1,10,20,30]]
                
    #container for queue node for each block
    blocks = [MMC(block_sizes[i],lambdas[i],mus[i]) for i in range(num_blocks)]
        
    simulation_end = 1000
    
    #arrival information
    arrivals_exog = [float('inf')]*len(block_sizes)
    arrivals_endo = [[] for _ in range(num_blocks)]
    arr_next_endo = float('inf')
    arr_endo_blocknum = None
    
    #simulation clock
    clock = 0
    
    #additional logs
    abandon_log =[]
    num_discouraged = 0
    arr_count = 0
    
    #calculate the first arrivals to each block to start simulation
    for i in range(len(arrivals_exog)):
        arrivals_exog[i] = r.expovariate(lambdas[i])
        
    
    while clock < simulation_end:
        arr_count+=1
        #start of loop occurs at the time of the last arrival event
                    
        #find block number/index of the next exogenous arrival
        arr_exog_blocknum = min(enumerate(arrivals_exog),key=itemgetter(1))[0]
        arr_next_exog = arrivals_exog[arr_exog_blocknum]

        if arr_endo_blocknum == None:
            #last internal arrival was used, need to find next one
            for idx, block in enumerate(arrivals_endo):
                if block:
                    #if block has any incoming internal arrivals, check earliest time
                    if block[0] < arr_next_endo:
                        #arrival at this block is earliest internal event found so far
                        arr_next_endo = block[0]
                        arr_endo_blocknum = idx
            
#        #determine which arrival is next event, set general variables
        if arr_next_exog <= arr_next_endo:
            #exogenous arrival happens next, generate new exog arrival time at this block
            next_event_time = arr_next_exog
            next_arr_block = arr_exog_blocknum
            arrivals_exog[next_arr_block] = next_event_time + r.expovariate(lambdas[next_arr_block])
            arrtype = 0
            
        else:
            #internal arrival happens next, set as general and remove from block's arrival list
            #print('internal arrival', arr_next_endo, 'block:', arr_endo_blocknum)
            next_event_time = arr_next_endo
            next_arr_block = arr_endo_blocknum
            arrivals_endo[arr_endo_blocknum].pop(0)
            
            #reset internal arrival information
            arr_endo_blocknum = None
            arr_next_endo = float('inf')
            arrtype = 1
        
        #update departures that occur before next arrival
        for b in blocks:
            #check blocks for activity, remove any departures before handling next arrival
            if b.num_inservice > 0:
                num_depart = b.update_departures(next_event_time)
                      
        #process arrival
        block = blocks[next_arr_block]
        if block.num_inservice == block.num_servers:
            #block full...choose whether to abandon or continue search
            action = make_choice(depart_prob)
            num_discouraged += 1
                            
            if action == 1:
                #choose to keep searching, pick next destination
                destination = make_choice(block_prob[next_arr_block])
                
                #set arrival time at destination block
                arrivals_endo[destination].append(next_event_time + \
                                            travel_times[next_arr_block][destination])
                                            
                #sort arrivals at block from earliest to latest
                arrivals_endo[destination].sort()
                
            else:
                #choose to abandon
                abandon_log.append(next_event_time)
            
        else:
            #space available, park
            block.add_customer(next_event_time)
            
        #increment simulation clock
        clock = next_event_time
                        
                                    
    #end of simulation, process logs
    server_logs = [[0]*simulation_end for _ in range(num_blocks)]
    
    
    for i,block in enumerate(blocks):
        #check server logs for each 
        t = 0
        for n,e in enumerate(block.server_log):
            #check number in service at each event
            if n == 0:
                #0s before first event already in log, skip ahead
                t = m.floor(e[1])
            else:
                t1 = m.floor(e[1])
                while t < t1-1:
                    #fill in server log 
                    server_logs[i][t] = e[0]
                    t+=1
                
                
    #stats and plotting of server histories
    avg_pct_occupancy = []
    for i,log in enumerate(server_logs):
        avg_pct_occupancy.append((sum(log)/len(log))/block_sizes[i])
        
    print('Avg occupancy by block', avg_pct_occupancy)
    print(len(abandon_log), 'abandonments')
    #print('Abandonments:', abandon_log)
    print('Pct Discouraged:',num_discouraged/arr_count)
    
#    
    y = server_logs[0]
    x = list(range(len(y)))
    
    plt.figure(1)
    plt.plot(x,y)
   
    y = server_logs[1]   
    plt.figure(2)
    plt.plot(x,y)
        
    y = server_logs[2]
    plt.figure(3)
    plt.plot(x,y)
    
    y = server_logs[3]
    plt.figure(4)
    plt.plot(x,y)
    
    plt.show()
#
#        