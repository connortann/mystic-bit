# Final deployment procedure

This procedure is based on [this blog](http://bit.ly/2LJUONn) and its help is gratefully acknowledged

Modifications adapted thanks to contributions from [Diego Castañeda's fork](http://bit.ly/2MoIMcO)

1. Sign in to AWS services
2. Launch EC2 instance using `Canonical, Ubuntu, 16.04 LTS, amd64 xenial image build on 2018-06-27`
3. Connect to the instance using SSH where permissions on `key.pem` were set with
    `$ chmod 400 key.pem`
4. Connect with `ssh -i <path/to/key.pem> ubuntu@<Public DNS>`
5. Update apt-get with `$ sudo apt-get update`
6. **Always make sure all packages are up to date too** with `$ sudo apt upgrade`
7. Check no Python with `$ python -V` output: 
    The program 'python' can be found in the following packages:
    * python-minimal
    * python3
8. Install python 3.6 with:
    * `sudo add-apt-repository ppa:deadsnakes/ppa`
    * `sudo apt-get update`
    * `sudo apt-get install python3.6 python3.6-dev`
9. Install pip3 with `$ sudo apt-get install python3-pip`
10. Get virtualenv with `pip3 install virtualenv`
11. If `locale.Error: unsupported locale setting` error, run `export LC_ALL=C` from [here](http://bit.ly/2NK40lv)
12. Then run `pip3 install virtualenv` again
13. Create the project folder or clone the project from your Git repository
14. Set up the virtual environment.
    - `$ cd cloned_project`
    - `$ virtualenv py36 --python=python3.6` to create a Python 3.6 environment - Python 3.6 is required for altair
15. Activate the environment (use `$ deactivate` to exit the environment).
    `$ . py36/bin/activate`
16. Check python version with `$ python -V` output: `Python 3.6.6`
17. Install Flask and other required modules: (Note: You do not need to use pip3 or python3 within the virtualenv since it is already a Python3 virtualenv)
    - `$ pip install Flask matplotlib numpy pandas altair bokeh "holoviews[recommended]"`
18. Create the Flask file. In my case it exists already. => check that the file runs with `$ python grvapp.py` should get a dev server running with output: `* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`
    press CTRL+C to quit
19. Setup Apache - need to build for the same version of Python
20. list available apache modeules `$ sudo apt-cache search libapache2*`
21. for Ubuntu, we need to use `$ sudo apt-get install apache2 apache2-dev` (from [mod_wsgi docs](http://bit.ly/2NKJ11N) and [apache docs](http://bit.ly/2NHZ0Oc))
22. From [mod_wsgi docs](http://bit.ly/2NKJ11N), Python must be 3.3 or later, we have 3.6.6 so *should be ok*.
23. Source code for mod_wsgi is [here](http://bit.ly/2NEPNX1), download the latest version and unpack it with `$ tar xvfz mod_wsgi-X.Y.tar.gz` replacing `X.Y` with version number. So for me: `$ tar xvfz mod_wsgi-4.6.4.tar.gz`
24. To setup the package ready for building run the “configure” script from within the source code directory:
    - `cd mod_wsgi-4.6.4`
    - `./configure`
    - Then build the source code with 
    - `make`
    - Then install the Apache module into the standard location for Apache modules as dictated by Apache for your installation, run:
    - `~make install~` ~or~ `sudo make install` ~if permission denied~
25. `CMMI` or `./configure` + `make` + `sudo make install` **will probably not install the `mod_wsgi` python library in the right place. So _additionally_ With the python 3.6 env activated and inside the mod_wsgi install dir, do:**
    - `$ python setup.py install`
26. create a wsgi file with:
    - `$ cd ..` to come back into the correct folder and check paths:
    - App path='/home/ubuntu/grv-app-deploy'
    - virtualenv path='/home/ubuntu/grv-app-deploy/py36'
    - html path='/var/www/html/grv-app-deploy'
    - `$ vim app.wsgi`
27. Paste this code into the *.wsgi file:
    ```python
    activate_this = '/home/ubuntu/grv-app-deploy/py36/bin/activate_this.py'
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

    import sys
    import logging

    logging.basicConfig(stream=sys.stderr)
    sys.path.insert(0,"/var/www/html/grv-app-deploy/")

    from grvapp import app as application
    ```

28. Create a symlink so that the project directory appears in /var/www/html
    - `$ sudo ln -sT ~/grv-app-deploy /var/www/html/grv-app-deploy`
29. **In my case, I had to add the apache config file that would let apache load the wsgi module:**
    - `$ sudo vim /etc/apache2/mods-available/wsgi.load`
    include the following line in that file:
    - `LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so`
30. Enable wsgi.
    - `$ sudo a2enmod wsgi`    
31. Configure apache (you will need to sudo to edit the file)
    - `$ sudo vim /etc/apache2/sites-enabled/000-default.conf`
32. Paste this in right after the line with DocumentRoot /var/www/html
    ```python
    WSGIDaemonProcess grv-app-deploy threads=5 socket-timeout=20 memory-limit=850000000 virtual-memory-limit=850000000
    WSGIScriptAlias / /var/www/html/grv-app-deploy/app.wsgi

    <Directory grv-app-deploy>
        WSGIProcessGroup grv-app-deploy
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
    ```
33. Flatten numpy pickles to arrays with:
    ```python
    # imports
    import numpy as np

    # read files
    f1 = np.load('entropy_20180610.npy')
    f2 = np.load('mid_unit.npy')
    f3 = np.load('realisation_1_10.npy')

    # file shape
    f1.shape, f2.shape, f3.shape

    # save as array
    f1_array = np.array(f1)
    f2_array = np.array(f2)
    f3_array = np.array(f3)

    # flatten to 2D array
    f1_array_flat = f1_array.reshape(250,16200)
    f2_array_flat = f2_array.reshape(250,16200)
    f3_array_flat = f3_array.reshape(250, 3240000)

    # reshape to original dimensions
    f1_array_reshaped = f1_array_flat.reshape(250, 162, 100)
    f2_array_reshaped = f2_array_flat.reshape(250, 162, 100)
    f3_array_reshaped = f3_array_flat.reshape(250, 162, 100, 200)

    # check if arrays equal after reshape
    np.array_equal(f1_array, f1_array_reshaped),
    np.array_equal(f2_array, f2_array_reshaped),
    np.array_equal(f3_array, f3_array_reshaped)

    # save to npy
    np.save("f1_array_flat", f1_array_flat, allow_pickle=False)
    np.save("f2_array_flat", f2_array_flat, allow_pickle=False)
    np.save("f3_array_flat", f3_array_flat, allow_pickle=False)
    ```
34. Load flattened files to S3
35. get *.npy files from S3 into `~/grv-app-deploy/static` with:
    - `$ wget https://s3.amazonaws.com/grvappbucket/f1_array_flat.npy`
    - `mv f1_array_flat.npy.1 f1_array_flat.npy`
    - `$ wget https://s3.amazonaws.com/grvappbucket/f2_array_flat.npy`
    - `mv f2_array_flat.npy.1 f2_array_flat.npy`
    - `$ wget https://s3.amazonaws.com/grvappbucket/f3_array_flat.npy`
    - `mv f3_array_flat.npy.1 f3_array_flat.npy`
    - check/set permissions with `$ sudo chmod +755 f1_array_flat.npy f2_array_flat.npy f3_array_flat.npy`
36. Restart the Server:
    `$ sudo apachectl restart`
37. **Change ownership and permissions on app folder**, run:
    - `$ sudo chown -R www-data:www-data /var/www/html/`
    **Always double check inside grv-app-deploy and subdirectories that AT LEAST, the group of every file is www-data and that group members have rwx permission.**
38. use `$ sudo bash -c 'echo > /var/log/apache2/error.log'` to clean error log and `$ sudo apachectl restart` to restart the server
39. check the IPv4 Public IP at e.g. `54.84.76.221`
40. check the logs at: `vim /var/log/apache2/error.log`
41. ensure the absolute path on the server is used: `/var/www/html/grv-app-deploy/static`
    
**This is the end of the new procedure.**

# Adding https

A good guide is given [here](http://bit.ly/2MwtxOT)
For "Step 4 - Buy or get a trial SSL Certificate", I used [certbot](http://bit.ly/2MdC5gO):
- select software [Apache] and system [Ubuntu 16.04 (xenial)]
- run Install commands:
    ```shell
    $ sudo apt-get update
    $ sudo apt-get install software-properties-common
    $ sudo add-apt-repository ppa:certbot/certbot
    $ sudo apt-get update
    $ sudo apt-get install python-certbot-apache 
    ```
- run `$ sudo certbot --apache certonly` and move certificates into folders as described in the [guide](http://bit.ly/2MwtxOT)
- check renewal with `$ sudo certbot renew --dry-run`

## Forcing all trafic through https
- Activate `rewrite` with `$ sudo a2enmod rewrite`
- Run `$ sudo vim /etc/apache2/sites-available/000-default.conf`
- Add these lines after `ErroLog` and `CustomLog` (modified to match):
    ```
    RewriteEngine on
    RewriteCond %{SERVER_NAME} =example.com [OR]
    RewriteCond %{SERVER_NAME} =www.example.com
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
    ```
- Copy default config to ssl config

# Additional procedures

## Mounting an S3 bucket on to EC2 instance:
1. Diego Castañeda suggested [mounting the S3 bucket onto the EC2 instance](http://bit.ly/2NIVgMl)
2. Procedure followed to set up an [S3 bucket](https://amzn.to/2LTKDGd)

## Change ownership and permissions on bucket

Run:
- `$ sudo chown -R www-data:www-data /var/www/html/grv-app-deploy/s3bucket/`
- `$ sudo chmod -R 775 /var/www/html/grv-app-deploy/s3bucket/`
- `$ sudo chmod +755 filename`

## Issue with mod_wsgi and pickles

There seems to be an issue with `mod_wsgi` and `numpy.pickles` as shown [here](http://bit.ly/2LHN7dP):

“In practice, what this means is that neither function objects, class objects or instances of classes which are defined in a WSGI application script file should be stored using the “pickle” module.”

So next step:
- flatten numpy.pickles from 3D and 4D to 2D
- load to S3
- import to app
- change grvapp.py to take in these new arrays
  
## Changes to WSGIDaemonProcess recommended by mod_wsgi author (not implemented in working version)

Based on [video from mod_wsgi creator Graham Dumpleton](https://youtu.be/H6Q3l11fjU0) and [docs](http://bit.ly/2vq9XfS), apache config file `/etc/apache2/sites-enabled/000-default.conf` to be modified as follows:
 - Edit file with: `$ sudo vim /etc/apache2/sites-enabled/000-default.conf`
 - Paste this in right after the line with DocumentRoot /var/www/html:
 ```python
#WSGIDaemonProcess grv-app-deploy threads=5 socket-timeout=20 memory-limit=850000000 virtual-memory-limit=850000000
WSGIDaemonProcess grv-app-deploy display-name='%{GROUP}' lang='en_US.UTF-8' locale='en_US.UTF-8' threads=5 queue-timeout=45 \
    socket-timeout=60 connect-timeout=15 request-timeout=60 inactivity-timeout=0 startup-timeout=15 deadlock-timeout=60 \
    graceful-timeout=15 eviction-timeout=0 restart-interval=0 shutdown-timeout=5 maximum-requests=0 \
    memory-limit=850000000 virtual-memory-limit=850000000

WSGIScriptAlias / /var/www/html/grv-app-deploy/app.wsgi

<Directory grv-app-deploy>
    WSGIProcessGroup grv-app-deploy
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
</Directory>
 ```
=> change made, no change to errors

## WSGIRestrictEmbedded

Based on same as above (docs [here](bit.ly/2O3jZeE)), added following line to code: `WSGIRestrictEmbedded On`
 - this **must** be added **above** the `<VirtualHost *:80>` line.

`/etc/apache2/sites-enabled/000-default.conf` (without comments):
- `WSGIProcessGroup grv-app-deploy` moved out of `<Directory>`:

```Python
WSGIRestrictEmbedded On

<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        WSGIDaemonProcess grv-app-deploy display-name='%{GROUP}' lang='en_US.UTF-8' locale='en_US.UTF-8' threads=5 queue-timeout=45 \
                socket-timeout=60 connect-timeout=15 request-timeout=60 inactivity-timeout=0 startup-timeout=15 deadlock-timeout=60 \
                graceful-timeout=15 eviction-timeout=0 restart-interval=0 shutdown-timeout=5 maximum-requests=0 \
                memory-limit=850000000 virtual-memory-limit=850000000

        WSGIProcessGroup grv-app-deploy

        WSGIScriptAlias / /var/www/html/grv-app-deploy/app.wsgi

        <Directory grv-app-deploy>
                #WSGIProcessGroup grv-app-deploy
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
        </Directory>
        ...
```

## Changing instance type:

Actions:
 - create an AMI of instance using [this](https://amzn.to/2MgqZo3) page
 - then from the EC2 dashboard: Actions>Instance State>Stop
 - then from the EC2 dashboard: Actions>Instance Settings>Change Instance Type and select e.g. `t2.large`
 - then from the EC2 dashboard: Actions>Instance State>Start
 - then reloaded new `IPv4 Public IP` in a broswer and checked pages:
    - /
    - /test_image
    - /large_image
    - /altair and /entropy
 