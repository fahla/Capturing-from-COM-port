from ftplib import FTP

def upload_file_to_ftp(filename, server, username, password, directory):
    with FTP(server) as ftp:
        ftp.login(user=username, passwd=password)
        if directory:
            ftp.cwd(directory)
        with open(filename, 'rb') as file:
            ftp.storbinary(f'STOR {filename}', file)
