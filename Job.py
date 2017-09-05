# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 14:10:07 2016

@author: alek
"""

class ClientJob(object):
    
    def __init__(self,processNumber,process,className,methodName,isClass,QID,args):
        self.processNumber = processNumber  
        self.QJobName = ''
        self.process = process
        self.className = className
        self.methodName = methodName
        self.isClass = isClass
        self.QID = QID
        self.args = args
        self.returnValue = ''
       
       
class ServerJob(object):
    
    def __init__(self,processNumber,className,methodName,QJobName,isClass,QID,ip,args):
        self.processNumber = processNumber
        self.QJobName = QJobName
        self.className = className
        self.methodName = methodName
        self.isClass = isClass
        self.QID = QID
        self.ip = ip
        self.args = args
        self.returnValue = ''