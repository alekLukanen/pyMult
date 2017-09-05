# pyMult
The pyMult library will allow you to quickly and easily perform distributed computing on any number of computers. All that you will need is a trusted network to put your computer(s) on and at least one computer. pyMult does not require any setup outside of python, the entire process of setting up and distributing jobs is done using common python 3 libraries.

# How to Use
To use the code you will need to download the repo onto two separate computers. One of the computers will be the client and the other will be the server. To run the server simply execute
```python
python serverProtocal.py
```
on the computer that will be the server.
And on the client side you will need to change the line
```python
client.startClient('127.0.0.1')
```
to reflect the ip address of the server. The line is at the bottom of the clientProtocal.py file. This will be the address of the server on the network. Once the address is set, run
```python
python clientProtocal.py
```
With both the server and client running the client will then begin requesting jobs from the server. In both clientProtocal.py and serverProtocal.py there are mains which contain some simple testing code. In this case the server distributes a few jobs to the client. You should be able to see the output in the console of the server. The client will also print out the jobs it has recieved. 

# Issues
At the moment no error checking is really done, so don't be supprised if one or two of your jobs go missing. Also, it is expected that the code you submit to the server runs. There is no security at this point.

# Future Work
In the future I would like to completely redo the entire process so it will be easier to generate and distrubute jobs. I would also like to add the ability for the clients to send new jobs back to the server for execution. 
