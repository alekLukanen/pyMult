# pyMult
The pyMult library will allow you to quickly and easily perform distributed computing on any number of computers at any time. All that you will need is a trusted network to put your computer(s) on and at least one computer.

# How to use
To use the code you will need to download the repo onto two separate computers. One of the computers will be the client and the other will be the server. To run the server simply run
'''python
python serverProtocal.py
'''
And on the client side you will need to change the line
'''python
client.startClient('127.0.0.1')
''' 
to reflect the ip address of the server. This will be the address that the client will look to for jobs to be run.
