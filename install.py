import subprocess
import os

# Define the packages to install
packages = ["nginx", "mysql80-server", "wordpress", "php82"]

# Install the packages
for package in packages:
    print(f"Installing {package}...")
    subprocess.run(["pkg", "install", "-y", package])

# Configure MySQL
print("Configuring MySQL...")
subprocess.run(["sysrc", "mysql_enable=YES"])
subprocess.run(["service", "mysql-server", "start"])

# Get database credentials from user
mysql_root_password = input("Enter MySQL root password: ")
wordpress_db_name = input("Enter WordPress database name: ")
wordpress_db_user = input("Enter WordPress database user: ")
wordpress_db_password = input("Enter WordPress database password: ")

# Configure MySQL database
print("Configuring MySQL database...")
subprocess.run(["mysql", "-uroot", "-e", f"CREATE DATABASE {wordpress_db_name};"])
subprocess.run(["mysql", "-uroot", "-e", f"GRANT ALL PRIVILEGES ON {wordpress_db_name}.* TO '{wordpress_db_user}'@'localhost' IDENTIFIED BY '{wordpress_db_password}';"])
subprocess.run(["mysql", "-uroot", "-e", "FLUSH PRIVILEGES;"])

# Configure WordPress
print("Configuring WordPress...")
wordpress_config = """
<?php
define('DB_NAME', '{wordpress_db_name}');
define('DB_USER', '{wordpress_db_user}');
define('DB_PASSWORD', '{wordpress_db_password}');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8');
define('DB_COLLATE', '');
?>
""".format(wordpress_db_name=wordpress_db_name, wordpress_db_user=wordpress_db_user, wordpress_db_password=wordpress_db_password)
with open("/usr/local/www/wordpress/wp-config.php", "w") as f:
    f.write(wordpress_config)

# Configure Nginx
print("Configuring Nginx...")
nginx_config = """
http {
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
}
"""
with open("/usr/local/etc/nginx/nginx.conf", "w") as f:
    f.write(nginx_config)

# Enable PHP in Nginx
print("Enabling PHP in Nginx...")
subprocess.run(["sysrc", "php_fpm_enable=YES"])
subprocess.run(["service", "php-fpm", "start"])

# Restart Nginx
print("Restarting Nginx...")
subprocess.run(["service", "nginx", "restart"])

print("WordPress is now available at http://localhost/wp-admin/install.php")
