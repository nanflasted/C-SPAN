#Backend for C-SPAN
##In this directory:
* backend.py
 * Script for interfacing with frontend
* dbinit.py
 * For database initialization
* dbmngr.py
 * For basic manipulation of the database
* nwmngr.py
 * For scraping information from twitter, and construction RNNs
* dbpopl.py
 * Code for database population with congress info
* csplog.py
 * Error and event logging utility
* loginit.py
 * Log utiliy initialization
* /prestored
 * prestored data
* twcred.py
 * twitter API oauth credentials

##Dependencies:
[Tensorflow](https://www.tensorflow.org/versions/r0.12/get_started/os_setup.html#download-and-setup)
[Tweepy](http://www.tweepy.org/) `pip install Tweepy`
[Sqlite3](https://sqlite.org/)

##To Set-up:
Run
```
python backend.py
```
**Note that this will also hard reset everything**
If you don't want neural nets deleted, run the `softreset()` function in backend.py

##For more detailed documentation:
Refer to 
* databaseDoc.html
* backendDoc.html

	
