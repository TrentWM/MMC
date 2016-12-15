# -*- coding: utf-8 -*-
"""
Quick Example using the MMC class
"""


from mmc import MMC
import random as r


if __name__ == '__main__':
    
    #parameters for MMC node    
    num_servers = 2
    lambd = 1
    mu = 3
    
    
    
    #create a single MMC queue
    node = MMC(num_servers,lambd,mu)
    
    #log customer histories...record attributes will change over course of simulation
    cust_log = []
    q_waits = []
    q_log = []
    t = 0   
    arrivals = 0
    departures = 0
    
    #Actual simulation loop
    simulation_end = 50000
    print('starting simulation')    
    while t< simulation_end:
        
        #get next arrival time
        t_next_arr = t + r.expovariate(lambd)
        
        if node.num_inservice > 0:
            #customers in-service...update any departures occuring before next arrival
        
            num_depart = node.update_departures(t_next_arr)
            departures += num_depart
            
        #add next customer customer
        cust = node.add_customer(t_next_arr)
        arrivals += 1
        
        #log customer object for use after simulation
        cust_log.append(cust)
        
        #increment clock to the next event
        t = t_next_arr
        
    #stats from simulation
    services = [c.service_time for c in cust_log]
    cwaits = [c.service_start-c.arrival_time for c in cust_log]
    systtimes = [c.time_in_syst for c in cust_log]    
    
    util = sum(services)/t
    q_area = 0
    prev_t = 0
    
    for e in node.q_log:
        area_increment = e[0]*(e[1]-prev_t)
        prev_t = e[1]
        q_area += area_increment
        
#    print('util', util)
    avg_wait_c = sum(cwaits)/len(cwaits)
    avg_service = sum(services)/len(services)
    avg_syst = sum(systtimes)/len(systtimes)
    avg_q2 = q_area/t
    
    print('final queue length:', len(node.q))
    print('arrivals/departures:', arrivals,'/', departures )
    print('avg_qt:', avg_q2)
    print('avg wait:', avg_wait_c)
    print('avg system time:', avg_syst)
