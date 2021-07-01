# ShowTracker Website

## Summary:
This is a basic website made to keep track of a users list of weekly shows. Sort of like a calander of just a week that lists what shows air on what day.

# How to run:
The website runs using the web framwork Flask in python. Make sure you have pipenv working so that you can use the configured pipenv environment.

Here is the code to setup the environment using pipenv:
```
 pipenv install
```
Now you can enter the environment using the line:
```
pipenv shell
```
Then we just need to run a rundev.sh file. You will need to make it using rundev_example.sh as base. You will need a database connection string and secret hash key in your rundev.sh.

First you should copy rundev_example.sh as rundev.sh:
```
cp rundev_example.sh rundev.sh
```
After that you should have a rundev.sh file so you just need to replace DB_HOST and SECRET_KEY variable values to your own value.

If you need help making a hash key just go to a python interpreter and run these lines of code:
```
import os;
print(os.urandom(16))
```
This should output a string of randomish characters that can be used as the SECRET_KEY. Note that you may need to redo this until you have a string with no " ' " character just because it affect how the variable is set in the rundev.sh file.

I should also mention that before running the file you may need to change the permissions on the rundev.sh file to run it. Here is the code you need to do that:
```
chmod +x rundev.sh
```
Finally, You can run the file with the line:
```
./rundev.sh
```
After that the website should be running. You can see the website if you type into a browser 'localhost:5000'.