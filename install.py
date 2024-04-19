import os
import subprocess

# Define the packages to install
packages = ["nginx", "php74", "mysql80-server", "wordpress"]

# Define the configuration files
nginx_conf = "/usr/local/etc/nginx/nginx.conf"
wordpress_conf = "/usr/local/www/wordpress/wp-config.php"

# Install the required packages
print("Installing required packages...")
for package in packages:
    subprocess.run(["pkg", "install", "-y", package])

# Configure Nginx
print("Configuring Nginx...")
with open(nginx_conf, "w") as f:
    f.write("""
server {
    listen 80;
    server_name localhost;

    root /usr/local/www/wordpress;
    index index.php index.html;

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
""")

# Configure WordPress
print("Configuring WordPress...")
with open(wordpress_conf, "w") as f:
    f.write("""
<?php
define('DB_NAME', 'wordpress');
define('DB_USER', 'wordpress');
define('DB_PASSWORD', 'wordpress');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8');
define('DB_COLLATE', '');

define('AUTH_KEY', 'put your unique phrase here');
define('SECURE_AUTH_KEY', 'put your unique phrase here');
define('LOGGED_IN_KEY', 'put your unique phrase here');
define('NONCE_KEY', 'put your unique phrase here');
define('AUTH_SALT', 'put your unique phrase here');
define('SECURE_AUTH_SALT', 'put your unique phrase here');
define('LOGGED_IN_SALT', 'put your unique phrase here');
define('NONCE_SALT', 'put your unique phrase here');

$table_prefix = 'wp_';

define('WP_DEBUG', false);

if (!defined('ABSPATH') )
    define('ABSPATH', dirname(__FILE__). '/');

require_once(ABSPATH. 'wp-settings.php');
""")

# Create the WordPress database
print("Creating WordPress database...")
subprocess.run(["mysql", "-uroot", "-e", "CREATE DATABASE wordpress;"])

# Create the WordPress user
print("Creating WordPress user...")
subprocess.run(["mysql", "-uroot", "-e", "GRANT ALL PRIVILEGES ON wordpress.* TO wordpress@localhost IDENTIFIED BY 'wordpress';"])

# Start Nginx and PHP-FPM
print("Starting Nginx and PHP-FPM...")
subprocess.run(["service", "nginx", "start"])
subprocess.run(["service", "php-fpm", "start"])

print("WordPress is now available at http://localhost/")
