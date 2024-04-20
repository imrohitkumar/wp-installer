import subprocess
import os

# Define the packages to install
packages = ["nginx", "mysql80-server", "wordpress", "php82"]

# Install the packages
for package in packages:
    print(f"Installing {package}...")
    subprocess.run(["pkg", "install", "-y", "--force", package])

# Configure MySQL
print("Configuring MySQL...")
subprocess.run(["sysrc", "mysql_enable=YES"])
subprocess.run(["service", "mysql-server", "start"])

# Set MySQL root password
mysql_root_password = input("Enter MySQL root password: ")
subprocess.run(["mysqladmin", "-u", "root", "password", mysql_root_password])

# Get database credentials from user
wordpress_db_name = input("Enter WordPress database name: ")
wordpress_db_user = input("Enter WordPress database user: ")
wordpress_db_password = input("Enter WordPress database password: ")

# Configure MySQL database
print("Configuring MySQL database...")
subprocess.run(["mysql", "-uroot", "-p" + mysql_root_password, "-e", f"CREATE DATABASE {wordpress_db_name};"])
subprocess.run(["mysql", "-uroot", "-p" + mysql_root_password, "-e", f"GRANT ALL PRIVILEGES ON {wordpress_db_name}.* TO '{wordpress_db_user}'@'localhost' IDENTIFIED BY '{wordpress_db_password}';"])
subprocess.run(["mysql", "-uroot", "-p" + mysql_root_password, "-e", "FLUSH PRIVILEGES;"])

# Configure WordPress
print("Configuring WordPress...")
wordpress_config = f"""
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
"""
with open("/usr/local/www/wordpress/wp-config.php", "w") as f:
    f.write(wordpress_config)

# Configure Nginx
print("Configuring Nginx...")
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

# Create the conf.d directory if it doesn't exist
if not os.path.exists("/usr/local/etc/nginx/conf.d/"):
    os.makedirs("/usr/local/etc/nginx/conf.d/")

with open("/usr/local/etc/nginx/conf.d/wordpress.conf", "w") as f:
    f.write(nginx_config)

# Set permissions on the WordPress directory
subprocess.run(["chown", "-R", "www:www", "/usr/local/www/wordpress"])

# Set permissions on the wp-config.php file
subprocess.run(["chmod", "640", "/usr/local/www/wordpress/wp-config.php"])

# Set permissions on the uploads directory
subprocess.run(["chmod", "755", "/usr/local/www/wordpress/wp-content/uploads"])

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
