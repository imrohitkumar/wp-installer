import os
import subprocess

def install_apache():
    # Install Apache
    subprocess.run(["pkg", "install", "apache24"], check=True)
    
    # Enable and start Apache service
    subprocess.run(["sysrc", "apache24_enable=YES"], check=True)
    subprocess.run(["service", "apache24", "start"], check=True)
    subprocess.run(["service", "apache24", "status"], check=True)

def install_php():
    # Install PHP and related packages
    subprocess.run(["pkg", "install", "php82", "php82-mysqli", "mod_php82"], check=True)
    
    # Copy php.ini and rehash
    subprocess.run(["cp", "/usr/local/etc/php.ini-production", "/usr/local/etc/php.ini"], check=True)
    subprocess.run(["rehash"], check=True)
    
    # Create mod_php.conf file
    with open("/usr/local/etc/apache24/modules.d/001_mod-php.conf", "w") as file:
        file.write("<IfModule dir_module>\n")
        file.write("    DirectoryIndex index.php index.html\n")
        file.write("    <FilesMatch \\.php$>\n")
        file.write("        SetHandler application/x-httpd-php\n")
        file.write("    </FilesMatch>\n")
        file.write("    <FilesMatch \\.phps$>\n")
        file.write("        SetHandler application/x-httpd-php-source\n")
        file.write("    </FilesMatch>\n")
        file.write("</IfModule>\n")
    
    # Restart Apache
    subprocess.run(["apachectl", "restart"], check=True)
    
    # Test PHP by creating index.php file
    os.remove("/usr/local/www/apache24/data/index.html")
    with open("/usr/local/www/apache24/data/index.php", "w") as file:
        file.write("<?php phpinfo(); ?>")

def install_mysql():
    # Install MySQL server
    subprocess.run(["pkg", "install", "mysql80-server"], check=True)
    
    # Enable and start MySQL service
    subprocess.run(["sysrc", "mysql_enable=YES"], check=True)
    subprocess.run(["service", "mysql-server", "start"], check=True)
    
    # Run mysql_secure_installation
    subprocess.run(["mysql_secure_installation"], check=True)

def setup_https_and_virtualhosts():
    # Enable mod_ssl in httpd.conf
    with open("/usr/local/etc/apache24/httpd.conf", "a") as file:
        file.write("LoadModule ssl_module libexec/apache24/mod_ssl.so\n")
    
    # Include httpd-ssl.conf
    with open("/usr/local/etc/apache24/httpd.conf", "a") as file:
        file.write("Include etc/apache24/extra/httpd-ssl.conf\n")
    
    # Generate self-signed certificate
    subprocess.run(["openssl", "req", "-x509", "-nodes", "-newkey", "rsa:2048", "-keyout", "/usr/local/etc/apache24/server.key", "-out", "/usr/local/etc/apache24/server.crt", "-days", "365"], check=True)

def test_setup_with_wordpress():
    # Change to apache data directory
    os.chdir("/usr/local/www/apache24/data")
    
    # Remove index.html and download Wordpress
    os.remove("index.html")
    subprocess.run(["wget", "https://wordpress.org/latest.tar.gz"], check=True)
    
    # Extract and move Wordpress files
    subprocess.run(["tar", "xzf", "latest.tar.gz"], check=True)
    subprocess.run(["mv", "wordpress/*", "."], check=True)
    
    # Change ownership of files
    subprocess.run(["chown", "-R", "www:www", "*"], check=True)
    
    # Create MySQL database and user for Wordpress
    subprocess.run(["mysql", "-u", "root", "-p"], input="create database wordpress;\ncreate user 'wordpress'@'localhost' identified by 'password';\ngrant all privileges on wordpress.* to 'wordpress'@'localhost';\nflush privileges;\n", check=True)

if __name__ == "__main__":
    install_apache()
    install_php()
    install_mysql()
    setup_https_and_virtualhosts()
    test_setup_with_wordpress()
    print("FAMP stack installation and setup completed successfully.")
