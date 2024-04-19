import subprocess
import os
import http.server
import socketserver

# Define the packages to install
packages = ["nginx", "mysql80-server", "wordpress"]

# Install the packages
for package in packages:
    print(f"Installing {package}...")
    subprocess.run(["pkg", "install", "-y", package])

# Configure MySQL
print("Configuring MySQL...")
subprocess.run(["sysrc", "mysql_enable=YES"])
subprocess.run(["service", "mysql-server", "start"])

# Create a setup wizard
class SetupWizard:
    def __init__(self):
        self.mysql_root_password = ""
        self.wordpress_db_name = ""
        self.wordpress_db_user = ""
        self.wordpress_db_password = ""

    def handle_request(self, request):
        if request.path == "/":
            return self.index(request)
        elif request.path == "/setup":
            return self.setup(request)
        else:
            return "Not Found", 404

    def index(self, request):
        html = """
        <html>
        <body>
        <h1>WordPress Setup Wizard</h1>
        <form action="/setup" method="post">
        <label for="mysql_root_password">MySQL Root Password:</label>
        <input type="password" id="mysql_root_password" name="mysql_root_password">


        <label for="wordpress_db_name">WordPress Database Name:</label>
        <input type="text" id="wordpress_db_name" name="wordpress_db_name">


        <label for="wordpress_db_user">WordPress Database User:</label>
        <input type="text" id="wordpress_db_user" name="wordpress_db_user">


        <label for="wordpress_db_password">WordPress Database Password:</label>
        <input type="password" id="wordpress_db_password" name="wordpress_db_password">


        <input type="submit" value="Setup">
        </form>
        </body>
        </html>
        """
        return "200 OK", html

    def setup(self, request):
        self.mysql_root_password = request.form["mysql_root_password"]
        self.wordpress_db_name = request.form["wordpress_db_name"]
        self.wordpress_db_user = request.form["wordpress_db_user"]
        self.wordpress_db_password = request.form["wordpress_db_password"]

        # Configure MySQL
        subprocess.run(["mysql", "-uroot", "-e", f"CREATE DATABASE {self.wordpress_db_name};"])
        subprocess.run(["mysql", "-uroot", "-e", f"GRANT ALL PRIVILEGES ON {self.wordpress_db_name}.* TO '{self.wordpress_db_user}'@'localhost' IDENTIFIED BY '{self.wordpress_db_password}';"])
        subprocess.run(["mysql", "-uroot", "-e", "FLUSH PRIVILEGES;"])

        # Configure Nginx
        nginx_config = """
        server {
            listen 80;
            server_name localhost;

            root /usr/local/www/wordpress;
            index index.php index.html index.htm;

            location / {
                try_files $uri $uri/ /index.php?q=$uri&$args;
            }

            location ~ \.php$ {
                try_files $uri =404;
                fastcgi_pass 127.0.0.1:9000;
                fastcgi_param SCRIPT_FILENAME $request_filename;
                include fastcgi_params;
            }
        }
        """
        with open("/usr/local/etc/nginx/nginx.conf", "w") as f:
            f.write(nginx_config)

        # Configure WordPress
        wordpress_config = """
        <?php
        define('DB_NAME', '{wordpress_db_name}');
        define('DB_USER', '{wordpress_db_user}');
        define('DB_PASSWORD', '{wordpress_db_password}');
        define('DB_HOST', 'localhost');
        define('DB_CHARSET', 'utf8');
        define('DB_COLLATE', '');
       ?>""".format(wordpress_db_name=self.wordpress_db_name, wordpress_db_user=self.wordpress_db_user, wordpress_db_password=self.wordpress_db_password)
        with open("/usr/local/www/wordpress/wp-config.php", "w") as f:
            f.write(wordpress_config)

        html = """
        <html>
        <body>
        <h1>Setup Complete!</h1>
        <p>WordPress is now available at <a href="http://localhost">http://localhost</a></p>
        </body>
        </html>
        """
        return "200 OK", html

# Start the setup wizard
setup_wizard = SetupWizard()
httpd = socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler)
httpd.RequestHandlerClass.handle_request = setup_wizard.handle_request
print("Setup Wizard available at http://localhost:8000")
httpd.serve_forever()
