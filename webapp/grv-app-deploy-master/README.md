# grv-app-deploy

This repo is a self-contained copy of the working app.

This readme is the step-by-step procedure followed including errors and wrong paths. 
It is kept as a learning material. 

The final procedure is detailed in [deploy.md](./deploy.md)

## Procedure

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
27. Paste this code into the wsgi file:
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
33. get *.npy files from S3 into `~/grv-app-deploy/static` with:
    - `$ wget https://s3.amazonaws.com/grvappbucket/f1_array_flat.npy`
    - `mv f1_array_flat.npy.1 f1_array_flat.npy`
    - `$ wget https://s3.amazonaws.com/grvappbucket/f2_array_flat.npy`
    - `mv f2_array_flat.npy.1 f2_array_flat.npy`
    - `$ wget https://s3.amazonaws.com/grvappbucket/f3_array_flat.npy`
    - `mv f3_array_flat.npy.1 f3_array_flat.npy`
    - check/set permissions with `$ sudo chmod +755 f1_array_flat.npy f2_array_flat.npy f3_array_flat.npy`
34. Restart the Server:
    `$ sudo apachectl restart`
35. **Change ownership and permissions on app folder**, run:
    - `$ sudo chown -R www-data:www-data /var/www/html/`
    **Always double check inside grv-app-deploy and subdirectories that AT LEAST, the group of every file is www-data and that group members have rwx permission.**
36. use `$ sudo bash -c 'echo > /var/log/apache2/error.log'` to clean error log and `$ sudo apachectl restart` to restart the server
37. check the IPv4 Public IP at e.g. `54.84.76.221`
38. check the logs at: `vim /var/log/apache2/error.log`
39. ensure the absolute path on the server is used: `/var/www/html/grv-app-deploy/static`
    
**This is the end of the new procedure.**


## Mounting S3 bucket on to EC2 instance:
1. Diego Castañeda suggested [mounting the S3 bucket onto the EC2 instance](http://bit.ly/2NIVgMl)
2.  Procedure followed to set up an [S3 bucket](https://amzn.to/2LTKDGd)
3.  Checking with a small image:
    - upload small image to S3 - done, ok
    - check data available on EC2-mounted S3 bucket - done, ok
    - create new route in app - done, ok
    - test1: page loads with alt-text working correctly. no image but `Distribution` still `In Progress`
    - test2: now `Distribution` is `Available`, reload page: working, image is seen from the `Distribution`.
4.  Added a different small image and reloaded, it worked, confirming that S3 bucket, distribution, and mounting all work.
5.  Check with a large image (tiff does not display in chrome, trying with a large *.png image):
    - upload large image to S3 - done, ok
    - check data available on EC2-mounted S3 bucket -done, ok
    - create new route in app - done, ok
    - added `WSGIDaemonProcess grv-app-deploy threads=5 socket-timeout=20` (`socket-timeout=20`) to apache2 config file 
    - resized image in template as was showing at default size
    - test: image **loads** *very slowly*
    - interestingly, it loads *a lot faster* from the [direct link](http://d1fmtfaf606jtr.cloudfront.net/nasa_large.png)
    - this means that:
        - S3 **works**
        - mounting of S3 onto EC2 **works**
        - Distribution of data **works**
        - reading data (*.png) through apache2 and mod_wsgi **works**

## Change ownership and permissions on bucket

Run:
- `$ sudo chown -R www-data:www-data /var/www/html/grv-app-deploy/s3bucket/`
- `$ sudo chmod -R 775 /var/www/html/grv-app-deploy/s3bucket/`
- `$ sudo chmod +755 filename`

## Issue with mod_wsgi and pickles

There seems to be an issue with `mod_wsgi` and `numpy.pickles` as shown [here](http://bit.ly/2LHN7dP):

“In practice, what this means is that neither function objects, class objects or instances of classes which are defined in a WSGI application script file should be stored using the “pickle” module.”

So next step:
- flatten numpy.pickles from 3D and 4D to 2D - done
- load to S3 - done
- import to app - done
- change grvapp.py to take in these new arrays - done
- test - done, still no success
  
## Changes to WSGIDaemonProcess
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

## Changes to WSGIDaemonProcess

Based on same as above, added following line to code: `WSGIRestrictEmbedded On`
 - this **must** be added **above** the `<VirtualHost *:80>` line.

=> The server does not run

The fact that `Embedded mode of mod_wsgi disabled by runtime configuration` suggests the `WSGIRestrictEmbedded On` was placed correctly _but_ that a process _is trying_ to run in embedded mode, which mod_wsgi strongly dissaproves.
=> need to find out how to fix this.

## Changes to WSGIProcessGroup

Based on same as above (docs [here](bit.ly/2O3jZeE)), modified following line as follows:

Line before: `WSGIProcessGroup grv-app-deploy`
Line after: `WSGIProcessGroup %{GLOBAL}`

=> error persisted

`Embedded mode of mod_wsgi disabled by runtime configuration` still being returned. 

=> Code broken. Something running in embedded mode?

`/etc/apache2/sites-enabled/000-default.conf` current state:

```Python
WSGIRestrictEmbedded On

<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        WSGIDaemonProcess grv-app-deploy display-name='%{GROUP}' lang='en_US.UTF-8' locale='en_US.UTF-8' threads=5 queue-timeout=45 \
                socket-timeout=60 connect-timeout=15 request-timeout=60 inactivity-timeout=0 startup-timeout=15 deadlock-timeout=60 \
                graceful-timeout=15 eviction-timeout=0 restart-interval=0 shutdown-timeout=5 maximum-requests=0 \
                memory-limit=850000000 virtual-memory-limit=850000000

        WSGIScriptAlias / /var/www/html/grv-app-deploy/app.wsgi

        <Directory grv-app-deploy>
                #WSGIProcessGroup grv-app-deploy
                WSGIProcessGroup %{GLOBAL}
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
        </Directory>

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

From [Checking your installation](bit.ly/2O3YGtf), switch back `WSGIProcessGroup` to previous value:
 - `WSGIProcessGroup grv-app-deploy`

updates to config file:
 - `WSGIScriptAlias / /var/www/html/grv-app-deploy/app.wsgi` changed to `WSGIScriptAlias /grv-app-deploy /var/www/html/grv-app-deploy/app.wsgi`
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

=> `Truncated or oversized response headers received from daemon process 'grv-app-deploy'`
Also now with `WSGIRestrictEmbedded On` set, the app still runs on first page, suggesting it is _no longer_ running in embedded mode.

[This](http://bit.ly/2OAsdfj) github issue suggested setting `LogLevel info`, this yielded the following information:
```
[Thu Aug 02 07:40:15.473822 2018] [wsgi:info] [pid 4961:tid 140448154359680] mod_wsgi (pid=4961): Attach interpreter ''.
[Thu Aug 02 07:50:23.733644 2018] [wsgi:info] [pid 4961:tid 140448008173312] mod_wsgi (pid=4961): Create interpreter 'ip-172-31-29-84.ec2.internal|'.
```

`wsgi:info] [pid 4961:tid 140448154359680] mod_wsgi (pid=4961): Attach interpreter ''` pointed to [this post](http://bit.ly/2ODhMYs) which suggests that there is a problem with the Python installation and that `Python installation needs to have been installed with the --enable-shared option given to its 'configure' command.`. More information is available [here](http://bit.ly/2vcoahb). This suggests I should _reinstall_ `python` and therefore _rebuild_ `mod_wsgi` as it is built against a specific Python version.

**However**: I do not know how to clean old versions completely so perhaps I should just rebuild the whole app... not ideal.

## Following the errors...

Got `Invalid Mutex directory in argument file:${APACHE_LOCK_DIR}` error trying to run `apache2 -V` to follow [Apache Build Information](http://bit.ly/2O6xNoF). 

Using `source /etc/apache2/envvars` and `apache2 -V` from [here](http://bit.ly/2MgLhOk) yields for `apache2 -V`:
```shell
(py36) ubuntu@ip-172-31-29-84:/home/ubuntu/grv-app-deploy$ apache2 -V
Server version: Apache/2.4.18 (Ubuntu)
Server built:   2018-06-07T19:43:03
Server\'s Module Magic Number: 20120211:52
Server loaded:  APR 1.5.2, APR-UTIL 1.5.4
Compiled using: APR 1.5.2, APR-UTIL 1.5.4
Architecture:   64-bit
Server MPM:     event
  threaded:     yes (fixed thread count)
    forked:     yes (variable process count)
Server compiled with....
 -D APR_HAS_SENDFILE
 -D APR_HAS_MMAP
 -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
 -D APR_USE_SYSVSEM_SERIALIZE
 -D APR_USE_PTHREAD_SERIALIZE
 -D SINGLE_LISTEN_UNSERIALIZED_ACCEPT
 -D APR_HAS_OTHER_CHILD
 -D AP_HAVE_RELIABLE_PIPED_LOGS
 -D DYNAMIC_MODULE_LIMIT=256
 -D HTTPD_ROOT="/etc/apache2"
 -D SUEXEC_BIN="/usr/lib/apache2/suexec"
 -D DEFAULT_PIDLOG="/var/run/apache2.pid"
 -D DEFAULT_SCOREBOARD="logs/apache_runtime_status"
 -D DEFAULT_ERRORLOG="logs/error_log"
 -D AP_TYPES_CONFIG_FILE="mime.types"
 -D SERVER_CONFIG_FILE="apache2.conf"
```

According to [modwsgi.readthedocs](http://bit.ly/2O6xNoF) the most important details are:
 - The version of Apache from the ‘Server version’ entry. 
    => Apache/2.4.18 (Ubuntu)
 - The MPM which Apache has been compiled to use from the ‘Server MPM’ entry.
    => event

Still according to [modwsgi.readthedocs](http://bit.ly/2O6xNoF)
"What is often more useful is the actual arguments which were supplied to the ‘configure’ command when Apache was built.
To determine this information you need to do the following.

Work out where ‘apxs2’ or ‘apxs’ is installed.
Open this file and find setting for ‘$installbuilddir’.
Open the ‘config.nice’ file in the directory specified for build directory.
On MacOS X, for the operating system supplied Apache this file is located at ‘/usr/share/httpd/build/config.nice’. The contents of the file is:"

So, going to: `$ /usr/share/apache2/build` and running `vim config.nice` yields:

```shell
#! /bin/sh
#
# Created by configure

CFLAGS="-pipe -g -O2 -fstack-protector-strong -Wformat -Werror=format-security"; export CFLAGS
CPPFLAGS="-DPLATFORM='"Ubuntu"' -DBUILD_DATETIME='"2018-06-07T19:43:03"' -Wdate-time -D_FORTIFY_SOURCE=2"; export CPPFLAGS
LDFLAGS="-Wl,--as-needed -Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,now"; export LDFLAGS
LTFLAGS="--no-silent"; export LTFLAGS
"./configure" \
"--host=x86_64-linux-gnu" \
"--build=x86_64-linux-gnu" \
"--enable-layout=Debian" \
"--enable-so" \
"--with-program-name=apache2" \
"--enable-suexec" \
"--with-suexec-caller=www-data" \
"--with-suexec-bin=/usr/lib/apache2/suexec" \
"--with-suexec-docroot=/var/www" \
"--with-suexec-userdir=public_html" \
"--with-suexec-logfile=/var/log/apache2/suexec.log" \
"--with-suexec-uidmin=100" \
"--enable-suexec=shared" \
"--enable-log-config=static" \
"--with-apr=/usr/bin/apr-1-config" \
"--with-apr-util=/usr/bin/apu-1-config" \
"--with-pcre=yes" \
"--enable-pie" \
"--enable-mpms-shared=all" \
"--enable-mods-shared=all cgi ident authnz_fcgi" \
"--enable-mods-static=unixd logio watchdog version" \
"CFLAGS=-pipe -g -O2 -fstack-protector-strong -Wformat -Werror=format-security" \
"CPPFLAGS=-DPLATFORM=Ubuntu -DBUILD_DATETIME=2018-06-07T19:43:03 -Wdate-time -D_FORTIFY_SOURCE=2" \
"LDFLAGS=-Wl,--as-needed -Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,-z,now" \
"LTFLAGS=--no-silent" \
"build_alias=x86_64-linux-gnu" \
"host_alias=x86_64-linux-gnu" \
"$@"
```

Following the docs, the `--enable-layout` yields: `--enable-layout=Debian`

`Apache Modules Loaded` are yielded by `/usr/sbin$ apache2 -l` and gives:

```shell
Compiled in modules:
  core.c
  mod_so.c
  mod_watchdog.c
  http_core.c
  mod_log_config.c
  mod_logio.c
  mod_version.c
  mod_unixd.c
```

Running `/usr/sbin$ apache2 -M` to get 'determine what Apache modules will be loaded dynamically' (from docs) returns the `Invalid Mutex directory in argument file:${APACHE_LOCK_DIR}` error so run `source /etc/apache2/envvars` again to be able to run `/usr/sbin$ apache2 -M` and yield:

```shell
Loaded Modules:
 core_module (static)
 so_module (static)
 watchdog_module (static)
 http_module (static)
 log_config_module (static)
 logio_module (static)
 version_module (static)
 unixd_module (static)
 access_compat_module (shared)
 alias_module (shared)
 auth_basic_module (shared)
 authn_core_module (shared)
 authn_file_module (shared)
 authz_core_module (shared)
 authz_host_module (shared)
 authz_user_module (shared)
 autoindex_module (shared)
 deflate_module (shared)
 dir_module (shared)
 env_module (shared)
 filter_module (shared)
 mime_module (shared)
 mpm_event_module (shared)
 negotiation_module (shared)
 setenvif_module (shared)
 status_module (shared)
 wsgi_module (shared)
 ```

 'Validate that ‘mod_wsgi.so’ is using a shared library for Python' by running `$ ldd mod_wsgi.so` in `~/grv-app-deploy/mod_wsgi-4.6.4/src/server/.libs` to yield:

 ```shell
	linux-vdso.so.1 =>  (0x00007fff769a9000)
	libpython3.6m.so.1.0 => /usr/lib/x86_64-linux-gnu/libpython3.6m.so.1.0 (0x00007f7a8f964000)
	libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f7a8f747000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f7a8f37d000)
	libexpat.so.1 => /lib/x86_64-linux-gnu/libexpat.so.1 (0x00007f7a8f154000)
	libz.so.1 => /lib/x86_64-linux-gnu/libz.so.1 (0x00007f7a8ef3a000)
	libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f7a8ed36000)
	libutil.so.1 => /lib/x86_64-linux-gnu/libutil.so.1 (0x00007f7a8eb33000)
	libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f7a8e82a000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f7a90292000)
```

'What you want to see is a reference to an instance of ‘libpythonX.Y.so’. Normally the operating system shared library version suffix would always be ‘1.0’. What it is shouldn’t really matter though.'

Here we have: `libpythonX.Y.so = libpython3.6m.so.1.0`

As the `operating system shared library version suffix` is 1.0, this is OK according to the docs.

## Python Installation In Use

Replacing app.wsgi content with:

```python
import sys

def application(environ, start_response):
    status = '200 OK'

    output = u''
    output += u'sys.version = %s\n' % repr(sys.version)
    output += u'sys.prefix = %s\n' % repr(sys.prefix)

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output.encode('UTF-8')]
```

yields: 
```python
sys.version = '3.6.6 (default, Jun 28 2018, 04:42:43) \n[GCC 5.4.0 20160609]'\
sys.prefix = '/usr'
```

which should produce:
```python
sys.version = "'2.6.1 (r261:67515, Feb 11 2010, 00:51:29) \\n[GCC 4.2.1 (Apple Inc. build 5646)]'"
sys.prefix = '/usr'
```

which appears to be correct as I was _not_ expecting a Python installation under '/usr/local/'


## Embedded Or Daemon Mode

Replacing app.wsgi content with:

```python
import sys

def application(environ, start_response):
    status = '200 OK'
    output = u'mod_wsgi.process_group = %s' % repr(environ['mod_wsgi.process_group'])
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output.encode('UTF-8')]
```

yields: `mod_wsgi.process_group = 'grv-app-deploy'` which is correct.

## Sub Interpreter Being Used

Replacing app.wsgi content with:

```python
import sys

def application(environ, start_response):
    status = '200 OK'
    output = u'mod_wsgi.application_group = %s' % repr(environ['mod_wsgi.application_group'])

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output.encode('UTF-8')]
```

yields: `mod_wsgi.application_group = 'ip-172-31-29-84.ec2.internal|'` 

From [here](http://bit.ly/2MbQEOv):
'If being run in the main interpreter, ie., the first interpreter created by Python, this will output:'

`mod_wsgi.application_group = ''`

'This actually corresponds to the directive:'

`WSGIApplicationGroup %{GLOBAL}`

The output above _seems ok_ but not sure.

## Single Or Multi Threaded

Replacing app.wsgi content with:

```python
import sys

def application(environ, start_response):
    status = '200 OK'
    output = u'wsgi.multithread = %s' % repr(environ['wsgi.multithread'])

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output.encode('UTF-8')]
```

From [here](http://bit.ly/2Mcap8G)
'If multithreaded, this will yield:'

`wsgi.multithread = True`

yields: `wsgi.multithread = True` which is correct as `thread=5` is set in config file.

## Following the errors:

For the error: `wsgi:error Truncated or oversized response headers received from daemon process`

[this](http://bit.ly/2O8hw2n) and other pages suggest setting `WSGIApplicationGroup %{GLOBAL}`, but this is already done in my app. I also tried putting this command at different levels of the config file but to no avail.

[this page](http://bit.ly/2OaD4Mb) suggests increasing `header-buffer-size=nnn` in the [WSGIDaemonProcess](http://bit.ly/2O8AVk5) but the poster had no success with this.

let's try, in `WSGIDaemonProcess` I add `header-buffer-size=1000000`, no success error persists:

```shell
[Fri Aug 03 08:49:11.742568 2018] [wsgi:error] [pid 10820:tid 140447980713728] [client 185.50.221.158:63860] Truncated or oversized response headers received from daemon process 'grv-app-deploy': /var/www/html/grv-app-deploy/app.wsgi
```

remove `header-buffer-size`

On [this page](http://bit.ly/2OaD4Mb) someone also mentions simply scaling up the EC2 instance - as Matt Hall has suggested. 
Let's try.

## Result of changing instance type:

Actions:
 - created an AMI of my instance using [this](https://amzn.to/2MgqZo3) page
 - then from the EC2 dashboard: Actions>Instance State>Stop
 - then from the EC2 dashboard: Actions>Instance Settings>Change Instance Type and selected `t2.large`
 - then from the EC2 dashboard: Actions>Instance State>Start
 - then reloaded new `IPv4 Public IP` in a broswer and checked pages:
    - / works
    - /test_image works
    - /large_image works
    - /altair and /entropy give the same error as before, see stack trace below:
    ```
    [Fri Aug 03 08:50:42.594930 2018] [mpm_event:notice] [pid 14686:tid 140448154359680] AH00494: SIGHUP received.  Attempting to restart
    [Fri Aug 03 08:50:42.788889 2018] [mpm_event:notice] [pid 14686:tid 140448154359680] AH00489: Apache/2.4.18 (Ubuntu) mod_wsgi/4.6.4 Python/3.6 configured -- resuming normal operations
    [Fri Aug 03 08:50:42.788912 2018] [core:notice] [pid 14686:tid 140448154359680] AH00094: Command line: '/usr/sbin/apache2'
    [Fri Aug 03 08:50:43.536582 2018] [wsgi:error] [pid 10949:tid 140448008148736] /usr/lib/python3.6/importlib/_bootstrap.py:219: RuntimeWarning: numpy.dtype size changed, may indicate binary incompatibility. Expected 96, got 88
    [Fri Aug 03 08:50:43.536614 2018] [wsgi:error] [pid 10949:tid 140448008148736]   return f(*args, **kwds)
    [Fri Aug 03 11:28:01.678986 2018] [mpm_event:notice] [pid 14686:tid 140448154359680] AH00491: caught SIGTERM, shutting down
    [Fri Aug 03 11:28:35.501633 2018] [mpm_event:notice] [pid 1291:tid 140647754004352] AH00489: Apache/2.4.18 (Ubuntu) mod_wsgi/4.6.4 Python/3.6 configured -- resuming normal operations
    [Fri Aug 03 11:28:35.502281 2018] [core:notice] [pid 1291:tid 140647754004352] AH00094: Command line: '/usr/sbin/apache2'
    [Fri Aug 03 11:48:02.644204 2018] [mpm_event:notice] [pid 1291:tid 140647754004352] AH00491: caught SIGTERM, shutting down
    [Fri Aug 03 11:51:09.446378 2018] [mpm_event:notice] [pid 1318:tid 140516636018560] AH00489: Apache/2.4.18 (Ubuntu) mod_wsgi/4.6.4 Python/3.6 configured -- resuming normal operations
    [Fri Aug 03 11:51:09.446851 2018] [core:notice] [pid 1318:tid 140516636018560] AH00094: Command line: '/usr/sbin/apache2'
    [Fri Aug 03 11:52:30.204934 2018] [wsgi:error] [pid 1321:tid 140516489832192] /usr/lib/python3.6/importlib/_bootstrap.py:219: RuntimeWarning: numpy.dtype size changed, may indicate binary incompatibility. Expected 96, got 88
    [Fri Aug 03 11:52:30.204988 2018] [wsgi:error] [pid 1321:tid 140516489832192]   return f(*args, **kwds)
    [Fri Aug 03 12:02:28.557734 2018] [wsgi:error] [pid 1322:tid 140516305864448] [client 185.50.221.158:64747] Truncated or oversized response headers received from daemon process 'grv-app-deploy': /var/www/html/grv-app-deploy/app.wsgi
    [Fri Aug 03 12:02:29.179056 2018] [core:notice] [pid 1318:tid 140516636018560] AH00051: child pid 1321 exit signal Segmentation fault (11), possible coredump in /etc/apache2
    [Fri Aug 03 12:08:05.619540 2018] [wsgi:error] [pid 1499:tid 140516489832192] /usr/lib/python3.6/importlib/_bootstrap.py:219: RuntimeWarning: numpy.dtype size changed, may indicate binary incompatibility. Expected 96, got 88
    [Fri Aug 03 12:08:05.619591 2018] [wsgi:error] [pid 1499:tid 140516489832192]   return f(*args, **kwds)
    [Fri Aug 03 12:08:06.616868 2018] [wsgi:error] [pid 1323:tid 140516526647040] [client 185.50.221.158:64909] Truncated or oversized response headers received from daemon process 'grv-app-deploy': /var/www/html/grv-app-deploy/app.wsgi
    [Fri Aug 03 12:08:07.555846 2018] [core:notice] [pid 1318:tid 140516636018560] AH00051: child pid 1499 exit signal Segmentation fault (11), possible coredump in /etc/apache2
    ```
    - i.e. the same errors and notices as before:
        - `RuntimeWarning: numpy.dtype size changed, may indicate binary incompatibility. Expected 96, got 88`
        - `Truncated or oversized response headers received from daemon process 'grv-app-deploy'` 
        - `exit signal Segmentation fault (11), possible coredump in /etc/apache2`
