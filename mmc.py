# -*- coding: utf-8 -*-
"""


"""

import random as r

class MMC:
    
    class Customer:
        def __init__(self,arrival_time,service_time,wait):
            
            self.arrival_time=arrival_time
            self.service_start = None
            self.service_time=service_time
            self.service_end= None #self.service_start + self.service_time
            self.time_in_syst = None
            self.wait = wait
                
    
    def __init__(self,num_servers,arrival_rate,service_rate,max_queue=None):
        self.num_servers = num_servers
        self.service = [None]*num_servers
        self.clock = 0
        self.lambd = arrival_rate #mean arrival rate
        self.mu = service_rate #mean service rate

        self.q = [] #queue/waiting line
        self.current_wait = 0
            
        self.full = False #True if all servers in use -- prevents need to search customer list each time
        self.num_inservice = 0
        self.num_queued = 0
        self.next_departure = float('inf')
        self.q_log = []
        self.server_log = [] #[[times],[numbers]]
        self.departure_log = []
        self.arrival_log = []
        
        
    def add_customer(self,arrival_time):
        '''adds another customer to this MMC node, at a server if available
        otherwise in the queue'''
        #print('adding customer')
        
        if self.num_inservice < self.num_servers:
    
            #server(s) available...add customer here
        
            s = self.choose_server() #can use this approach later for server-specific service rates
            service_time = r.expovariate(self.mu)
            c = self.Customer(arrival_time,service_time,self.current_wait)
            c.service_start = arrival_time
            c.service_end = arrival_time + service_time
            c.time_in_syst = service_time
            c.wait = 0
            
            self.service[s] = c
            self.num_inservice += 1
            self.server_log.append([self.num_inservice, arrival_time])

        else:
            #servers full, increment queue
            service_time = r.expovariate(self.mu)
            c = self.Customer(arrival_time,service_time,self.current_wait)
            c.wait = self.current_wait
            self.current_wait += service_time
            self.q.insert(0,c)
            self.num_queued +=1
            
        #log event
        self.server_log.append([self.num_inservice,arrival_time])
        self.q_log.append([len(self.q),arrival_time])
        self.arrival_log.append(arrival_time)
        
        return c
              
    def choose_server(self):
        '''selects an empty server for a new customer'''        
        #***need to add response here in case servers are full and no choice is made***        
        choice = None
        if self.num_inservice < self.num_servers:
            choice = 0 
            i = 0
            stop = False
            while i < self.num_servers and not stop:
                #find an empty server to use and select its index
                if self.service[i] == None:
                    choice = i 
                    stop = True
                else:
                    i += 1
         
        return choice
            
    def find_next_departure(self):
        '''checks for proximate departure from servers'''
        
        dep_time = float('inf')
        dep_c = None
        
        for c in self.service:
            if c != None:
                #check nonempty servers for departure times
                if c.service_end < dep_time:
                    dep_time = c.service_end
                    dep_c = c
                
        return dep_time, dep_c
        
    def update_departures(self,next_arrival):
        '''will remove any customers from server who finish before next arrival'''        

        num_departing = 0
        dep_time = 0
        
        while dep_time < next_arrival:
            #keep checking servers/queue until next departure after given time
            dep_time,c = self.find_next_departure()
            if dep_time<next_arrival:
                #next departure leaving before next arrival,adjust queues and servers
                if self.q:
                    #move customer from queue into service spot of departing customer
                    #record service endtime and time in system
                    next_c = self.q.pop()
                    next_c.service_start = dep_time
                    next_c.service_end = dep_time + next_c.service_time
                    next_c.time_in_syst = next_c.service_end - next_c.arrival_time
                    self.service[self.service.index(c)] = next_c
                    self.current_wait -= next_c.service_time
                    
                else:
                    #no queue, simply finish the current customer
                    self.service[self.service.index(c)] = None
                    self.num_inservice -= 1
                
                #log the departure event
                self.q_log.append([len(self.q),dep_time])
                self.departure_log.append(dep_time)
                     
                num_departing += 1
                   
        return num_departing