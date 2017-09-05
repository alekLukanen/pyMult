#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 11:13:49 2017

@author: lukanen
"""

import asyncio
import multiprocessing as mp
import time as tm
import threading
import Job
import pickleFunctions as pf

class ChatServer:

    class ChatProtocol(asyncio.Protocol):
        
        def __init__(self, chat_server):
            self.chat_server = chat_server
            self.username = None
            self.buffer = ""
            self.transport = None
            
            self.verbose = self.chat_server.printALot
            
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
            
            self.state = 0
            self.QIDNum = 0
            
        def setVerbose(self,ver):
            self.verbose = ver

        def connection_made(self, transport):
            # Callback: when connection is established, pass in transport.
            self.transport = transport
            self.send_msg(self.gotConnection)
            print ('connection_made...')
                        

        def data_received(self, data):
            # Callback: whenever data is received - not necessarily buffered.
            #print ('data_received...')
            data = data.decode("utf-8")
            self.buffer += data
            self.printToScreen('---------------')
            self.printToScreen('address : %s' % self.transport.get_extra_info('peername')[0])
            #print ('-* data : ', data)
        
            if (self.state==0):
                self.printToScreen('state(0)')
                self.stateZero()
                
            elif (self.state==1):
                #self.printToScreen('state(1)')
                self.stateOne()
                
            elif (self.state==2):
                #self.printToScreen('state(2)')
                self.stateTwo()
                
            elif (self.state==3):
                #self.printToScreen('state(3)')
                self.stateThree()
                
            elif (self.state==4):
                #self.printToScreen('state(4)')
                self.stateFour()
            
            elif (self.state==5):
                #self.printToScreen('state(5)')
                self.stateFive()
                
            elif (self.state==6):
                #self.printToScreen('state(6)')
                self.stateSix()
                
            elif (self.state==7):
                #self.printToScreen('state(7)')
                self.stateSeven()
                
            elif (self.state==8):
                #self.printToScreen('state(8)')
                self.stateEight()
                
            else:
                print ('not a state')
        
        def stateZero(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.userRef):
                    address = self.transport.get_extra_info('peername')[0]
                    print ('name : ', address)
                    userWasAdded = self.chat_server.add_user(address,data[1], self.transport)
                    print ('connections : ', self.chat_server.connections)
                    if (userWasAdded):
                        self.messageToState(0,self.wasAddedAsUser,1)
                    else:
                        self.messageToState(0,self.wasAddedAsUser,1)
                elif (data[0]==self.startOver):
                    self.messageToState(0,self.gotConnection,0)
                else:
                    self.messageToState(0,self.gotConnection,0)
            
        def stateOne(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                print ('self.chat_server.sendJobs : ' , self.chat_server.sendJobs.is_set())
                #self.chat_server.sendJobs.wait()
                if (data[0]==self.readyForJobs):
                    self.messageToState(1,self.makeRequest,2)
                elif (data[0]==self.startOver):
                    self.messageToState(1,self.gotConnection,0)
                
        def stateTwo(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.sendAJob):
                    if (len(self.chat_server.jobsToRun)!=0):
                        self.messageToState(2,self.sendingJob,4)
                    else:
                        self.messageToState(2,self.outOfJobs,6)
                elif (data[0]==self.sendingResult):
                    self.messageToState(2,self.sendResult,3)
                elif (data[0]==self.closingClient):
                    self.messageToState(2,self.close,8)
                else:
                    print ('in state 2, not of commands : ', data)
                    
                    
        def stateThree(self): #nothing goes here now
            data = self.buffer.split(self.endOfFileInstruction)
            if (len(data)>=2):
                job = pf.unPickle(data[0].encode())
                #print ('ServerJob : ', job)
                self.chat_server.jobsReturned.put(job)
                address = self.transport.get_extra_info('peername')[0]
                self.chat_server.updateUserJobsRecv(address,1)
                self.chat_server.numJobsRecv+=1
                print ('ServerJob.QID : ',job.QID,', address: ',address)
                #print ('connections : ', self.chat_server.connections)
                if (self.chat_server.queueCount==self.chat_server.numJobsRecv):
                    print ('ALL JOBS RECIEVED...')
                    #self.transport.write_eof()
                    self.chat_server.diconnectAllClients()
                    self.chat_server.chat_loop.stop()
                else:
                    self.buffer = 'this was a job'
                    self.messageToState(3,self.gotResult,5)
                    
        def stateFour(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                address = self.transport.get_extra_info('peername')[0]
                if (data[0]==self.sendTheJob):
                    self.printToScreen('state(4->4)(send new job here) : %s' % self.buffer)
                    #message = 'QID:%d' % self.QIDNum
                    job = self.chat_server.jobsToRun[0]
                    del self.chat_server.jobsToRun[0]
                    self.printToScreen('job.QID : %s' % job.QID)
                    pickledFileString = pf.createPickle(job)
                    #print ('pickledFileString : ', pickledFileString)
                    self.fileToState(4,pickledFileString,7)
                    self.chat_server.updateUserJobsSend(address,1)
                    self.chat_server.numJobsSent+=1
                    #print ('connections : ', self.chat_server.connections)
                    self.QIDNum+=1
                else:
                    self.printToScreen('state(?) : %s' % self.buffer)
                    
                    
        def stateFive(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.gotConfermation):
                    self.messageToState(5,self.makeRequest,2)
                else:
                    self.printToScreen('state(?) : %s' % self.buffer)
                    
        def stateSix(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.serverOutOfJobs):
                    self.messageToState(6,self.makeRequest,2)
                else:
                    self.printToScreen('state(?) : %s' % self.buffer)
                    
        def stateSeven(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.gotJob):
                    self.messageToState(7,self.makeRequest,2)
                else:
                    self.printToScreen('state(?) : %s' % self.buffer)
                    
        def stateEight(self):
            data = self.buffer.split(self.separator)
            if (len(data)>=2):
                if (data[0]==self.closed):
                    self.printToScreen('...the client is currently closed...')
                    #self.messageToState(7,self.makeRequest,2)
                else:
                    self.printToScreen('state(?) : %s'% self.buffer)
                    
        
        def messageToState(self,currentState,message,finalState):
            self.printToScreen('-* state(%d->%d)(%s) : %s' % (currentState,finalState,message,self.buffer))
            self.send_msg(message)
            self.buffer = ''
            self.state = finalState
           
        def fileToState(self,currentState,fileString,finalState):
            self.printToScreen('-* state(%d->%d)(fileString) : %s' % (currentState,finalState,self.buffer))
            self.send_file(fileString)
            self.buffer = ''
            self.state = finalState
           
        def eof_received(self):
            print ('RECIEVED END OF FILE REQUEST...')
            #print ('buffer : ', self.buffer)
            self.buffer = ''
            #self.send_msg(self.wasAddedAsUser)

        def connection_lost(self, exc):
            # Callback: client disconnected.
            if self.username is not None:
                self.chat_server.remove_user(self.username)
                
        def printToScreen(self,message):
            if (self.verbose==True):
                print (message)

        def send_msg(self, msg):
            msg = '%s%s' % (msg,self.separator)
            try:
                self.transport.write(msg.encode("utf-8"))
            except:
                print ('THE CONNECTIONS WAS CLOSED...')
            
        def send_file(self,fileString):
            fileCoded = '%s%s' % (fileString.decode(),self.endOfFileInstruction)
            self.transport.write(fileCoded.encode('utf-8'))

        def handle_lines(self):
            print ('hangle_lines...')
            while self.separator in self.buffer:
                line, self.buffer = self.buffer.split(self.separator, 1)
                print ('line: ' , line)
                print ('self.buffer: ',self.buffer)
                if self.username is None:
                    if self.chat_server.add_user(line, self.transport):
                        self.username = line
                    else:
                        self.send_msg("Sorry, that name is taken\nUsername: ")
                else:
                    self.chat_server.user_message(self.username, line)

    
    def __init__(self, server_name, port, loop):
        self.server_name = server_name
        self.connections = {}
        self.numJobsSent = 0
        self.numJobsRecv = 0
        self.queueCount = 0
        self.printALot = True
        self.sendJobs = threading.Event()
        self.sendJobs.clear()
        self.jobsToRun = []
        self.jobsReturned = mp.Queue(0)
        self.chat_loop = loop
        self.server = loop.create_server(
                lambda: self.ChatProtocol(self),
                host="", port=port)

    def diconnectAllClients(self):
        print ('disconnectAllClients...')
        for userData in self.connections.values():
            transport = userData['transport']
            transport.write_eof()
            userData['transClosed'] = True

    def broadcast(self, message):
        for transport in self.connections.values():
            transport.write((message + "\n").encode("utf-8"))
            
    def updateUserJobsSend(self,address,numJobsSent):
        self.connections[address]['numJobsSent'] = self.connections[address]['numJobsSent'] + numJobsSent
                        
    def updateUserJobsRecv(self,address,numJobsRecv):
        self.connections[address]['numJobsRecv'] = self.connections[address]['numJobsRecv'] + numJobsRecv

    def add_user(self, address , userName, transport):
        if address in self.connections:
            self.connections[address]['numReconnects']+=1
            return False
        self.connections[address] = {'userName' : userName , 'transport' : transport
                        ,'numJobsSent' : 0, 'numJobsRecv' : 0
                        , 'jobsRunning' : [], 'jobsRecieved' : []
                        , 'numReconnects' : 0, 'transClosed' : False}
        #self.broadcast("User " + username + " joined the room")
        return True

    def remove_user(self, username):
        del self.connections[username]
        #self.broadcast("User " + username + " left the room")

    def get_users(self):
        return self.connections.keys()

    def user_message(self, username, msg):
        self.broadcast(username + ": " + msg)

class server(object):
    
    def __init__(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.chat_server = ChatServer("Test Server", 4455, self.loop)
        self.newLoop = None
        self.serverThread = threading.Thread(target=self.serverCoroutine, args=(self.loop,))
        self.waitForServerEnd = threading.Event()
        self.waitForServerEnd.clear()
        
    def setPrintALot(self,boolVal):
        self.chat_server.printALot = boolVal
        
    def closeLoop(self):
        self.loop.close()
        
    '''
    def addJob(self,job):
        print ('adding a job: ', job)
        self.chat_server.jobsToRun.put(job)
        self.chat_server.queueCount+=1
    '''
    
    def addJob(self,className,methodName,QJobName,clientIP,args):
        QID = 'QID%d' % self.chat_server.queueCount
        self.chat_server.queueCount+=1
        job = Job.ServerJob(self.chat_server.queueCount,className,methodName,QJobName,
            False,QID,clientIP,args)
        self.chat_server.jobsToRun.append(job)
        
    def getResult(self):
        #if (self.chat_server.jobsReturned.empty()==False):
        try:
            return self.chat_server.jobsReturned.get(timeout=0.2)
        except:
            return None
        #else:
            #return None
        
    def runJobs(self):
        self.loop.call_soon_threadsafe(asyncio.async, self.runJobsCoroutine())
        
    #@asyncio.coroutine
    def runJobsCoroutine(self):
        self.chat_server.sendJobs.set()
   
    @asyncio.coroutine
    def printThing(self):
        yield from asyncio.sleep(3)
        print ('hello, world')
        
    def serverCoroutine(self,loop):
        asyncio.set_event_loop(loop)
        server = loop.run_until_complete(self.chat_server.server)
        try:
            loop.run_forever()
        finally:
            self.waitForServerEnd.set()
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()
     
        
    def startServer(self):
        try:
            self.serverThread.start()
        except:
            self.serverThread.join()
            self.serverThread.terminate()
            
        
    def waitForServerShutdown(self):
        self.waitForServerEnd.wait()
        self.waitForServerEnd.clear()

def main(argv):
    
    loop = asyncio.get_event_loop()
    chat_server = ChatServer("Test Server", 4455, loop)
    loop.run_until_complete(chat_server.server)
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    newServer = server()
    print ('start server')
    
    for i in range(0,8):
        newServer.addJob('exSheet','estimatePi','tester','anyIP',(1000,))
        
    startTime = tm.time()
    newServer.startServer()
    newServer.setPrintALot(False)
    #tm.sleep(7)
    print ('started the server')
    #newServer.runJobs()
    #newServer.runJobsCoroutine()
    newServer.waitForServerShutdown()
    print ('RUN TIME: ',tm.time()-startTime)
    print ('SERVER HAS ENDED')
    count = 0
    sum_pi = 0
    while(True):
        value = newServer.getResult()
        if (value!=None):
            print ('proc#: ',value.processNumber,', QJobName: ',value.QJobName,', QID: ',value.QID,'Result : ', value.returnValue)
            count +=1
            sum_pi += value.returnValue
        else:
            break
    print ('pi : ', (sum_pi/count))
    print ('count : ', count)
    #newServer.closeLoop()
    print ('server ended')