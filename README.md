# wpInstaller: FreeBSD WordPress Installer

wpInstall is a Python script designed to automate the installation and configuration of WordPress on FreeBSD systems. With just a few simple steps, you can have a fully functional WordPress website up and running in no time.

## Features

- **Easy Installation**: Automates the installation of necessary packages including Nginx, MySQL, WordPress, and PHP.
- **MySQL Configuration**: Configures MySQL database and grants necessary privileges to the WordPress database user.
- **WordPress Configuration**: Sets up the wp-config.php file with the provided database credentials.
- **Nginx Configuration**: Configures Nginx server block to serve WordPress website.
- **PHP-FPM Integration**: Enables PHP-FPM in Nginx for processing PHP files.

## Requirements

- FreeBSD operating system
- Python 3.x
- Internet connection for package installation

## Usage

1. Clone the repository or download the `wpInstall.py` script to your FreeBSD system.
2. Open a terminal and navigate to the directory containing `wpInstall.py`.
3. Run the script using Python:

    ```
    python3 wpInstall.py
    ```

4. Follow the on-screen instructions to provide MySQL root password and WordPress database details.
5. Once the script completes execution, your WordPress website will be accessible at `http://localhost/wp-admin/install.php`.

## Disclaimer

This script is intended for educational and development purposes. Use it at your own risk. It is recommended to review the script and understand its functionality before running it on your system.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the [MIT License](LICENSE).
