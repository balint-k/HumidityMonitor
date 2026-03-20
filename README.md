
# My Basic monitor for my Humidity sensor

I just wanted to monitor the humidity in our flat.

## Setup

Give execute permission for bash scripts (without it you can't run these bash files :C )

~~~
chmod +x configure.sh
chmod +x start.sh
~~~

and start configure.sh (it just downloads the required libraries and sets up the virtual environment)

~~~
bash configure.sh
~~~

## Run

The start.sh just activates the virtual environment and starts the python Code within. 

~~~
bash start.sh
~~~
