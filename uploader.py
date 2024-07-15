import ftplib
import logging
import time

def upload_file_to_ftp(filename, server, username, password, directory=None):
    """
    Uploads a file to an FTP server.

    :param filename: The name of the file to be uploaded.
    :param server: The FTP server address.
    :param username: The FTP username.
    :param password: The FTP password.
    :param directory: The directory on the FTP server to upload the file to (optional).
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        logger.info("Connecting to FTP server...")
        with ftplib.FTP(server) as ftp:
            ftp.login(user=username, passwd=password)
            logger.info(f"Logged in as {username}")

            if directory:
                logger.info(f"Changing to directory: {directory}")
                ftp.cwd(directory)

            logger.info(f"Uploading {filename} to FTP server...")
            with open(filename, 'rb') as file:
                ftp.storbinary(f'STOR {filename}', file)
            logger.info(f"Successfully uploaded {filename}")

    except ftplib.all_errors as e:
        logger.error(f"FTP error: {e}")

# Example usage
if __name__ == "__main__":
    # Replace with your details
    csv_filename = 'sensor_data.csv'
    ftp_server = 'ftp.gb.stackcp.com'
    ftp_username = 'ssns@cillyfox.com'
    ftp_password = '#SSNS9167'
    ftp_directory = ''  # Set to None if not needed


    upload_file_to_ftp(csv_filename, ftp_server, ftp_username, ftp_password, ftp_directory)
    