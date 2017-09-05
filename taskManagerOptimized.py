# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 12:33:41 2017

@author: alek
"""

import multiprocessing as mp
import threading
import time as tm
import importlib
import Job

class taskManagerOptimized(object):
    #TO DO:
    #move the increment to deque into the individual processes and get rid of
    #the resultQueue array for the dynamic multiprocessesing methods. Add a
    #new importLibrary method for this. Making this change should increase the
    #speed of the program considerably. Use lock to avoid multiple classes
    #accessing the same variables. You should also be able to move the kill 
    #process code into here.
    
    def __init__(self):
        #jobs arrays
        self.jobsToRun = [] #jobs yet to run
        self.jobs = [] #jobs running
        self.returnedValues = [] #values returned to the main thread
        self.name = 'manager_name' #name of the main thread
        self.returnedValues_dynamic = mp.Queue(0)
        
        #general info
        self.numProcessors = mp.cpu_count() #number of cores on the machine
        self.processNumber = 0 #the process count (total processes started)
        self.runCount = 0
        self.numDequed = 0
        
        #queues
        self.queue = mp.Queue(0) #the individual processes will place their
        #return values here.
        self.resultQueue = mp.Queue(0)
        
        #thread events
        self.queueIsEmpty = threading.Event() #result queue is empty
        self.queueIsEmpty.clear()
        self.finishedAJob = threading.Event() #a job has been finished
        self.finishedAJob.clear()
        self.startFlag = threading.Event() #when to start collecting data, set
        #by the startGathering() method.
        self.startFlag.clear()
        self.allProcessesKilled = threading.Event()
        self.allProcessesKilled.clear()
        self.addedResult = threading.Event()
        self.addedResult.clear()
        self.stopCollectingResults = threading.Event()
        self.stopCollectingResults.clear()
        self.allResultsFound = threading.Event()
        self.allResultsFound.clear()
        self.resultArray = threading.Lock()
        self.halt = False
        
        #this is the thread that joins all of the processes to the main process
        #and terminates them so they don't linger around.
        self.killThread = threading.Thread(name='killProcesses', target=self.killProcesses)
        self.killThread.setDaemon(False)
        
        self.updateResultQueueThread = threading.Thread(name='updateResultQueue_dynamic', target=self.updateResultQueue_dynamic)
        self.updateResultQueueThread.setDaemon(False)
        
        self.lock = threading.Lock()
    
    def clearQueues(self):
        self.queue.close()
        self.resultQueue.close()
        self.returnedValues_dynamic.close()
        self.queue=None
        self.resultQueue = None
        self.returnedValues_dynamic = None

    def setProcessCount(self,count):
        self.numProcessors = count
    
    def setProcessCountToCoreCount(self):
        self.numProcessors = mp.cpu_count()

    #The process result queue is empty and the actual result queue is empty.
    #if this is True the entire object does not have any data. If False the
    #there is data in either queue.
    def isEmpty(self):
        if (self.queue.empty()==True and self.resultQueue.empty()==True):
            return True
        else:
            return False
     
    #call this method when you want to start gathering data from the individual
    #processes. This method simply sets the start gathering flag to True.
    def startGathering(self):
        self.startFlag.set()
            
    def setup_normal(self):
        if (self.killThread.isAlive()==False):
            self.killThread.start()
            
    def setup_dynamic(self):
        #print 'starting a dynamic type class'
        if (self.updateResultQueueThread.isAlive()==False):
            self.updateResultQueueThread = threading.Thread(name='updateResultQueue_dynamic', target=self.updateResultQueue_dynamic)
            self.updateResultQueueThread.setDaemon(False)
            self.updateResultQueueThread.start()
        #print 'result thread has been started, you can now start adding jobs'
            
    def reset_dynamic(self):
        self.numDequed = 0
        self.runCount = 0
    
    def getReturnValue_wait(self):
        return self.returnedValues_dynamic.get()
        
    def getReturnedValue(self):
        self.resultArray.acquire()
        if (self.returnedValues_dynamic.empty()==False):
            job = self.returnedValues_dynamic.get()
            self.resultArray.release()
            return job
        else:
            self.resultArray.release()
            return None
            
    def addResult(self,job):
        self.resultArray.acquire()
        self.returnedValues_dynamic.put(job)
        self.resultArray.release()
        
    def canRunAJob(self):
        if ((self.runCount-self.numDequed)<self.numProcessors):
            return True
        else:
            return False
     
    #add a job and then call this function    
    def runAJob(self):
        self.lock.acquire()
        self.deleteStoppedJobs()
        if (len(self.jobsToRun)>0):
            if ((self.runCount-self.numDequed)<self.numProcessors):
                self.addedResult.clear()
                job = self.jobsToRun[0]
                job.process.start()
                self.jobs.append(job)
                self.jobsToRun.remove(job)
                self.runCount+=1
                self.lock.release()
            else:
                self.lock.release()
                self.addedResult.wait()
                self.addedResult.clear()
                self.lock.acquire()
                if ((self.runCount-self.numDequed)<self.numProcessors):
                    job = self.jobsToRun[0]
                    job.process.start()
                    self.jobs.append(job)
                    self.jobsToRun.remove(job)
                    self.runCount+=1
                    self.lock.release()
                    
    def deleteStoppedJobs(self):
        for job in self.jobs:
            if (job.process.is_alive()==False):
                job.process.join()
                job.process.terminate()
                try:
                    self.jobs.remove(job)
                except:
                    print ('not in array')
                    
    def deleteAllStoppedJobs(self):
        for job in self.jobs:
            job.process.join()
            job.process.terminate()
            try:
                self.jobs.remove(job)
            except:
                print ('not in array')
    
    def continueToDeleteStoppedJobs(self):
        while True:
            for job in self.jobs:
                if (job.process.is_alive()==False):
                    job.process.join()
                    job.process.terminate()
                    try:
                        self.jobs.remove(job)
                    except:
                        print ('not in array')
            if len(self.jobs)==0:
                break
            tm.sleep(0.1)
    
    #take in the values queued by the processes and increment numDequed by 1.
    #this method makes sure that the class knows how many jobs are running and.    
    def updateResultQueue_dynamic(self):
        #print ('starting updateResultQueue method')
        count = 0
        while (True):
            #print 'update'
            #print 'waiting for new result'
            self.lock.acquire()
            if (self.numDequed==self.runCount and self.stopCollectingResults.is_set()):
                self.lock.release()
                self.allResultsFound.set()
                break
                #print 'self.numDequed: ', self.numDequed
                #print 'self.runCount: ', self.runCount
            else:
                self.lock.release()
                newReturn = self.resultQueue.get()
                #print ('count: ',count,' newReturn: ', newReturn.QID)
                #self.resultQueueCopy.put(newReturn)
                self.resultArray.acquire()
                self.returnedValues_dynamic.put(newReturn)
                self.resultArray.release()
                self.lock.acquire()
                self.numDequed+=1
                self.lock.release()
                count+=1
                self.addedResult.set()
                #print 'len(self.jobs): ', len(self.jobs)
     
    #wait for all jobs to finished and all zombie jobs have been terminated.       
    def waitForJobsToFinish(self):
        print ('waiting for all jobs to finish')
        self.stopCollectingResults.set()
        self.allResultsFound.wait()
        self.allResultsFound.clear()
        print ('cleaning up all of the zombie jobs')
        self.continueToDeleteStoppedJobs()
        #print 'self.numDequed: ', self.numDequed
        #print 'self.runCount: ', self.runCount
        self.stopCollectingResults.clear()
        self.reset_dynamic()
    
    def stopRetrivingResults(self):
        self.updateResultQueueThread.join()
        self.killThread.join()

    #this method adds a job to the jobsToRun array. 
    #['exSheet','estimatePi',False,QID,(10000,)]
    #not sure if isObject is correct
    def addJob(self,fileName,method,isObject,QID,args):
        #print 'adding a job: ',job,'...'
        newJob = Job.ClientJob(self.processNumber,'none',fileName,method,isObject,QID,args)
        p = mp.Process(target=self.importLibrary, args=(newJob,))
        newJob.process = p
        self.jobsToRun.append(newJob)
        self.processNumber = self.processNumber + 1
        
    def addJobWithExtra(self,processNumber,QJobName,fileName,method,isObject,QID,args):
        newJob = Job.ClientJob(processNumber,'none',fileName,method,isObject,QID,args)
        newJob.QJobName = QJobName
        p = mp.Process(target=self.importLibrary, args=(newJob,))
        newJob.process = p
        self.jobsToRun.append(newJob)
                    
    def killProcesses(self):
        while True:
            print ('killProcess')
            #allKill = True
            for job in self.jobs:
                #if (job.process.is_alive()==False):
                    job.process.join()
                    job.process.terminate()
                    try:
                        self.jobs.remove(job)
                    except:
                        print ('not in array')
                    #allKill = False
            if (len(self.jobs)==0 and self.queueIsEmpty.is_set()==True):
                self.allProcessesKilled.set()
                break
            elif (self.queueIsEmpty.is_set()==True):
                tm.sleep(0.1)
                continue
            else:
                tm.sleep(.2)
                
    def serverClear(self):
        self.stopCollectingResults.set()
        self.queueIsEmpty.set()
        self.killThread.start()
        self.allProcessesKilled.wait()
        self.allProcessesKilled.clear()
        self.queueIsEmpty.clear()
        self.stopCollectingResults.clear()
        #self.stopRetrivingResults()
            
    def waitForProcessesToBeKilled(self):
        self.allProcessesKilled.wait()
        self.allProcessesKilled.clear()
    
    def importLibrary(self,job):
        i = importlib.import_module(job.className)
        func = getattr(i,job.methodName)
        if (len(job.args)==0):
            job.returnValue = func()
            job.process = None
            self.resultQueue.put(job)
        else:
            job.returnValue = func(*job.args)
            job.process = None
            self.resultQueue.put(job)
     
    #reset the taskManager. 
    def reset(self):
        self.queueIsEmpty.clear()
        self.runCount = 0
        self.numDequed = 0
        self.killThread = threading.Thread(name='killProcesses', target=self.killProcesses)
        self.killThread.setDaemon(False)
        self.killThread.start()
        
#this is a testing function
def runDynamicSim(taskManager,iterations=30000,numJobs=16):
    print ('-runDynamicSim(): ')
    ticks = 0
    while ticks<1:
        print ('+++++++++++')
        startTime = tm.time()
        taskManager.setup_dynamic()
        for i in range(0,numJobs):
            QID = 'QID%d' % i
            taskManager.addJob('exSheet','estimatePi',False,QID,(iterations,))
            taskManager.runAJob()
        print ('out of loop')    
        taskManager.waitForJobsToFinish()
        print ('TOTAL TIME: ', tm.time()-startTime)
        #print '-retrieving results'
        count = 0
        totalValue = 0 
        while True:
            job = taskManager.getReturnedValue()
            if (job==None):
                break
            else:
                value = job.returnValue
                totalValue+=value
                print ('-final job:' , count , ',QID:', job.QID , ',value:',value)
                count+=1
        print ('pi: ',(totalValue/count))
        if (count!=numJobs):
            print ('we lost something...oops...')
            print ('taskM.numDequed: ', taskM.numDequed)
            print ('taskM.runCount: ', taskM.runCount)
            break
        else:
            tm.sleep(0.1)
            
        ticks+=1
        print ('+++++++++++')
    print ('out of while-loop')
    

if __name__ == '__main__': #main
    taskM = taskManagerOptimized()
    #taskM.setProcessCount(4) #uncomment this to change the number of process running at a given time
    runDynamicSim(taskM,300000,16) #function above
    #taskM.clearQueues()
    print ('finished runDynamicsSim()...')
