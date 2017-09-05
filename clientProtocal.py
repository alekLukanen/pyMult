#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 15:28:21 2017

@author: lukanen
"""

import asyncio
import time as tm
import pickleFunctions as pf
import taskManagerOptimized as tmo

class ClientProtocal:
    
    class EchoClientProtocol(asyncio.Protocol):
        
        def __init__(self, userName, loop, client):
            self.clientObject = client
            
            self.userName = userName
            self.loop = loop
            self.count = 0
            self.transport = None
            self.connected = True
            self.addedAsUser = asyncio.Event()
            
            self.gotConnection = 'gotConnection'
            self.wasAddedAsUser = 'wasAddedAsUser'
            self.gotConfermation = 'gotConfermation'
            self.sendingJobs = 'sendingJobs'
            self.readyForJobs = 'readyForJobs'
            self.connecting = 'connecting'
            self.startOver = 'startOver'
            self.retryUserAdd = 'retryUserAdd'
            self.jobAdded = 'jobAdded'
            self.userRef = 'user'
            self.sendingLastJobAgain = 'sendingLastJobAgain'
            self.gotJob = 'gotJob'
            self.sendingNewJob = 'sendingNewJob'
            self.sendAJob = 'sendAJob'
            self.gotResult = 'gotResult'
            self.sendingResult = 'sendingResult'
            self.sendResult = 'sendResult'
            self.makeRequest = 'makeRequest'
            self.outOfJobs = 'outOfJobs'
            self.serverOutOfJobs = 'serverOutOfJobs'
            self.sendTheJob = 'sendTheJob'
            self.sendingJob = 'sendingJob'
            self.close = 'close'
            self.closed = 'closed'
            self.closingClient = 'closingClient'
            self.endOfFileInstruction = '//..//..()thisIsTheEndOfTheFile()..//..//'
            self.separator = ','
            
            self.buffer = ''
            self.state = 0
            self.jobCount = 1
    
        def connection_made(self, transport):
            self.transport = transport
            self.count += 1
    
        def data_received(self, data):
            self.printToScreen('data_received...')
            data = data.decode("utf-8")
            self.buffer += data
            self.printToScreen('---------------')
            if (self.state!=6):
                self.printToScreen('-* data : %s' % self.buffer)
            
            if (self.state==0):
                self.printToScreen('state(0)')
                self.stateZero()
            elif (self.state==1):
                self.printToScreen('state(1)')
                self.stateOne()
            elif (self.state==2):
                self.printToScreen('state(2)')
                self.stateTwo()
                
            elif (self.state==3):
                self.printToScreen('state(3)')
                self.stateThree()
                
            elif (self.state==4):
                self.printToScreen('state(4)')
                self.stateFour()
                
            elif (self.state==5):
                self.printToScreen('state(5)')
                self.stateFive()
                
            elif (self.state==6):
                self.printToScreen('state(6)')
                self.stateSix()
                
            elif (self.state==7):
                self.printToScreen('state(7)')
                self.stateSeven()
                
            else:
                print ('not a state')
                
        def stateZero(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.gotConnection):
                    self.messageToState(0,self.send_userName(),1)
                elif (data[0]==self.retryUserAdd):
                    self.messageToState(0,self.startOver,1)
        
        def stateOne(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.wasAddedAsUser):
                    self.messageToState(1,self.readyForJobs,2)
                else:
                    self.messageToState(1,self.startOver,0)
        
        def stateTwo(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.makeRequest):
                    if (self.clientObject.serverIsOutOfJobs==False): #can request a job
                    
                       isQueueEmpty = self.clientObject.taskManager.returnedValues_dynamic.empty()
                       if (isQueueEmpty==False): #send a job
                           self.messageToState(2,self.sendingResult,5)
                       else:
                           #tm.sleep(0.5)
                           self.messageToState(2,self.sendAJob,3)
                           
                    else:
                        self.printToScreen('returned: %d' % self.clientObject.numJobsReturned)
                        self.printToScreen('requested: %d' % self.clientObject.numJobsRequested)
                        if (self.clientObject.numJobsReturned<self.clientObject.numJobsRequested):
                            self.messageToState(2,self.sendingResult,5)
                        else:
                            self.messageToState(2,self.closingClient,7)
                            #self.loop.stop()
                else:
                    print ('state(?)')
                    
                
        def stateThree(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.sendingJob):
                    self.messageToState(3,self.sendTheJob,6)
                elif (data[0]==self.outOfJobs):
                    self.clientObject.serverIsOutOfJobs = True
                    self.messageToState(3,self.serverOutOfJobs,2)
                else:
                    print ('state(?)')
                
            
        def stateFour(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.gotResult):
                    if (True): #ask for another job
                        self.messageToState(4,self.gotConfermation,2)
                    else: #send another job
                        print ('something else')
                else:
                    print ('oops')
        
        def stateFive(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.sendResult):
                    job = self.clientObject.taskManager.getReturnValue_wait()
                    job.process = None
                    print ('<--- SENDING  JOB.QID : %s' % job.QID)
                    pickledFileString = pf.createPickle(job)
                    #res = 'RESULT:%s' % (self.clientObject.numJobsReturned+1)
                    self.fileToState(5,pickledFileString,4)
                    self.clientObject.numJobsReturned+=1
                else:
                    print ('oops(5) : ', self.buffer)
                    
        def stateSix(self):
            data = self.buffer.split(self.endOfFileInstruction)
            if (len(data)>=2):
                #print ('data[all] : ', data)
                #print ('data[0] : ', self.buffer)
                job = pf.unPickle(data[0].encode())
                #self.printToScreen('RECIEVED ServerJob : ', job)
                print ('---> RECIEVED Job.QID : %s' % job.QID)
                self.clientObject.taskManager.addJobWithExtra(job.processNumber
                        ,job.QJobName,job.className,job.methodName,job.isClass,job.QID,job.args)
                self.clientObject.taskManager.runAJob()
                self.buffer = 'was job string'
                self.messageToState(6,self.gotJob,2)
                self.clientObject.numJobsRequested+=1

        def stateSeven(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.close):
                    self.messageToState(7,self.closed,7)
                #elif (data[0]==self) star here
                print ('wait for server to end here')
                
        def printToScreen(self,message):
            if (self.clientObject.verbose==True):
                print (message)
                
        def fileToState(self,currentState,fileString,finalState):
            self.printToScreen('-* state(%d->%d)(fileString) : %s' % (currentState,finalState,self.buffer))
            self.send_file(fileString)
            self.buffer = ''
            self.state = finalState
            
        def send_file(self,fileString):
            fileCoded = '%s%s' % (fileString.decode(),self.endOfFileInstruction)
            self.transport.write(fileCoded.encode('utf-8'))
                    
        def messageToState(self,currentState,message,finalState):
            self.printToScreen('-* state(%d->%d)(%s) : %s' % (currentState,finalState,message,self.buffer))
            self.send_msg(message)
            self.buffer = ''
            self.state = finalState
            
        def send_msg(self, msg):
            msg = '%s%s' % (msg,self.separator)
            self.transport.write(msg.encode("utf-8"))
            
        def send_userName(self):
            return '%s%s%s' % (self.userRef,self.separator,self.userName)
            #self.send_msg(userString)
    
        def connection_lost(self, exc):
            print('The server closed the connection')
            print('Stop the event loop')
            #print('count: ', self.count)
            print ('TaskManager has ended...')
            self.loop.stop()
    
    def __init__(self):
        self.userName = 'Alek'
        self.loop = None
        self.coro = None
        self.serverIsOutOfJobs = False
        
        self.taskManager = tmo.taskManagerOptimized()
        self.taskManager.setup_dynamic()
        self.jobsRunning = []
        self.jobsReturned = []
        self.numJobsRequested = 0
        self.numJobsReturned = 0
        
        self.verbose = True
        
    def resetData(self):
        self.numJobsRequested = 0
        self.numJobsReturned = 0
        self.serverIsOutOfJobs = False
        
    def printALot(self,ver):
        self.verbose = ver
        
    def startClient(self,ip):
        while (True):
            try:
                print ('...')
                asyncio.set_event_loop(asyncio.new_event_loop())
                self.loop = asyncio.get_event_loop()
                self.coro = self.loop.create_connection(lambda: self.EchoClientProtocol(self.userName, self.loop, self),
                                              ip, 4455) #mac: 192.168.0.15
                self.loop.run_until_complete(self.coro)
                try:
                    print ('starting client...')
                    self.loop.run_forever()
                finally:
                    print ('closing client...')
                    client.taskManager.deleteAllStoppedJobs()
                    self.resetData()
                    self.loop.close()
                    
            except KeyboardInterrupt as e:
                print ("caugth keyboard interrupt")
            except:
                try:
                    tm.sleep(1)
                except KeyboardInterrupt as e:
                    print ("caugth keyboard interrupt")
                    self.loop.stop()
                    self.loop.close()
                    break
        
if __name__=='__main__':
    client = ClientProtocal()
    client.printALot(False)
    client.startClient('127.0.0.1')