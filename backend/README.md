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

	
