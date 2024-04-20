import subprocess

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
            try_files $uri $uri/ /index.php?$args;
        }

        location ~ \.php$ {
            include fastcgi_params;
            fastcgi_pass unix:/var/run/php-fpm.sock;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
            fastcgi_param SCRIPT_NAME $fastcgi_script_name;
        }

        location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
            expires max;
            log_not_found off;
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

# Enable Nginx
print("Enabling Nginx...")
subprocess.run(["sysrc", "nginx_enable=YES"])

# Start Nginx
print("Starting Nginx...")
subprocess.run(["service", "nginx", "start"])

print("WordPress is now available at http://localhost/wp-admin/install.php")
