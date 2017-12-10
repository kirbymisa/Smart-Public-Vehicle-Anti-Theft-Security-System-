# python-firebase highly makes use of the requests library so before you begin, you need to have that package installed.

# $ sudo pip install requests==1.1.0
# $ sudo pip install python-firebase

# Import firebase (python-firebase)
from firebase import firebase

# Firebase setup
firebase = firebase.FirebaseApplication('https://vehiclegpstrackingapp.firebaseio.com/', None)

# Fetch all data in JSON child database
allDataResult = firebase.get('vehicleinfo', None)

# Fetch data from firebase JSON database
dataResult = firebase.get('vehicleinfo', 'DriverName')

# Prints the output of the query result
print allDataResult
