```text
.______      ___   .___________.  ______  __    __  
|   _  \    /   \  |           | /      ||  |  |  | 
|  |_)  |  /  ^  \ `---|  |----`|  ,----'|  |__|  | 
|   ___/  /  /_\  \    |  |     |  |     |   __   | 
|  |     /  _____  \   |  |     |  `----.|  |  |  | 
| _|    /__/     \__\  |__|      \______||__|  |__| 
                                                    
.___  ___.      ___      .__   __.      ___       _______  _______ .___  ___.  _______ .__   __. .___________.
|   \/   |     /   \     |  \ |  |     /   \     /  _____||   ____||   \/   | |   ____||  \ |  | |           |
|  \  /  |    /  ^  \    |   \|  |    /  ^  \   |  |  __  |  |__   |  \  /  | |  |__   |   \|  | `---|  |----`
|  |\/|  |   /  /_\  \   |  . `  |   /  /_\  \  |  | |_ | |   __|  |  |\/|  | |   __|  |  . `  |     |  |     
|  |  |  |  /  _____  \  |  |\   |  /  _____  \ |  |__| | |  |____ |  |  |  | |  |____ |  |\   |     |  |     
|__|  |__| /__/     \__\ |__| \__| /__/     \__\ \______| |_______||__|  |__| |_______||__| \__|     |__|     
```

# Install

1. Clone this repository.
   ```bash
   $ cd /var/www
   $ git@github.ibm.com:ondrej-vagner/patches.git
   ```
2. Prepare `virtualenv`.
   ```bash
   $ cd patches/
   $ virtualenv env
   $ source env/bin/activate
   (env) $ pip install -r requirements.txt
   ```
3. Initialise the database.
   ```bash
   (env) $ cp utils/init_db.py /var/www/patches/
   (env) $ mkdir -p env/var/patches-instance/
   (env) $ echo "SQLDATABASE=sqlite:///var/www/patches/env/var/patches-instance/patches.sqlite" > /var/www/patches/.env
   (env) $ python init_db.py
   (env) $ rm init_db.py
   ```
4. Prepare the configuration. This guide assumes you are using `gunicorn` with the `supervisor` monitoring tool.
   ```bash
   (env) $ pip install gunicorn  # If you don't have gunicorn installed.
   (env) $ cp utils/gunicorn_config.example.py /var/www/patches/gunicorn_config.py
   (env) $ cp utils/config.example.py /var/www/patches/env/var/patches-instance/config.py
   (env) $ echo "PATCHES_EMAIL=admin@patch.application.example" >> /var/www/patches/.env
   # apt-get install supervisor  # If you don't have supervisor installed.
   # cp utils/patches.conf /etc/supervisor/conf.d/
   ```
   1. Update `config.py`:
      * Generate your own secret key
        ```bash
        (env) $ python -c "import secrets;print(secrets.token_hex(16))"
        ```
        and paste the result into the `SECRET_KEY` key. The line should look something like this:
        ```ini
        SECRET_KEY = b"75dc5fd435ec6a1cfc769cbc8768d395"
        ```
      * Update the location for `SERVER_NAME` key, including the port.
   2. Update `gunicorn_config.py`:
      * Provide path for your own `gunicorn` executable.
      * Provide the path to the `patches` directory, in case you cloned it somewhere other than `/var/www`.
      * If you changed the port in `config.py`, update the port in `bind` key here as well. Keep the IP as `0.0.0.0`.
      * Update the user which should be accessing the `patches` directory.
   3. Update `patches.conf`. The values should be same as in `gunicorn_config.py`:
      * Provide path for your own `gunicorn` executable and update the location of `gunicorn_config.py` if you installed in other than default location.
      * Provide the path to the `patches` directory.
      * Update the user which should be accessing the `patches` directory.
5. Restart `supervisor`.
   ```bash
   # service supervisor stop
   # service supervisor start
   or
   # systemctl restart supervisor
   ```
6. Your application should be available online.
