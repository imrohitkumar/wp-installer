import subprocess
import os
import tarfile
import shutil

# Define the packages to install
packages = ["nginx", "mysql80-server", "php82"]

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

# Download and extract WordPress installation archive
print("Downloading and extracting WordPress installation archive...")
wordpress_archive_url = "https://wordpress.org/latest.tar.gz"
wordpress_archive_file = "/tmp/wordpress.tar.gz"
subprocess.run(["fetch", "-o", wordpress_archive_file, wordpress_archive_url])
with tarfile.open(wordpress_archive_file, 'r:gz') as tar:
    tar.extractall(path='/tmp/')

# Move WordPress installation to /usr/local/www/
print("Moving WordPress installation to /usr/local/www/...")
shutil.move('/tmp/wordpress', '/usr/local/www/wordpress')

# Set permissions for WordPress installation
print("Setting permissions for WordPress installation...")
subprocess.run(["chown", "-R", "www:www", "/usr/local/www/wordpress"])

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
define('WP_CONTENT_DIR', 'wp-content');
define('WP_PLUGIN_DIR', 'wp-content/plugins');
define('WP_UPLOADS_DIR', 'wp-content/uploads');
?>
""".format(wordpress_db_name=wordpress_db_name, wordpress_db_user=wordpress_db_user, wordpress_db_password=wordpress_db_password)
with open("/usr/local/www/wordpress/wp-config.php", "w") as f:
    f.write(wordpress_config)

# Configure Nginx
print("Configuring Nginx...")
nginx_config = """
events {
    worker_connections 1024;
}

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

# Set permissions for Nginx configuration
print("Setting permissions for Nginx configuration...")
subprocess.run(["chown", "root:wheel", "/usr/local/etc/nginx/nginx.conf"])

# Enable PHP in Nginx
print("Enabling PHP in Nginx...")
subprocess.run(["sysrc", "php_fpm_enable=YES"])
subprocess.run(["service", "php-fpm", "start"])

# Enable Nginx
print("Enabling Nginx...")
subprocess.run(["sysrc", "nginx_enable=YES"])

# Start Nginx
print("Starting Nginx...")
subprocess.run(["service", "nginx", "start"])

print("WordPress is now available at http://localhost/wp-admin/install.php")
