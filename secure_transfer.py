try:
    import paramiko
    HAS_PARAMIKO = True
except Exception:
    paramiko = None
    HAS_PARAMIKO = False

import os

def sftp_upload(local_path: str, remote_path: str, host: str, port: int = 22, username: str = None, password: str = None, pkey_path: str = None, timeout: int = 10) -> None:
    """Upload a local file to remote SFTP server. Raises RuntimeError on failure.
    Supports either password or private key auth (pkey_path).
    """
    if not HAS_PARAMIKO:
        raise RuntimeError('paramiko is not installed; please pip install paramiko')

    transport = None
    try:
        if pkey_path:
            pkey = None
            try:
                # Try RSAKey
                pkey = paramiko.RSAKey.from_private_key_file(pkey_path)
            except Exception:
                try:
                    pkey = paramiko.Ed25519Key.from_private_key_file(pkey_path)
                except Exception:
                    pkey = None
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, pkey=pkey)
        else:
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)
        remote_dir = os.path.dirname(remote_path)
        # ensure remote dir exists (best-effort)
        try:
            sftp.chdir(remote_dir)
        except IOError:
            # attempt to create directories recursively
            parts = remote_dir.split('/')
            cur = ''
            for p in parts:
                if not p: continue
                cur = cur + '/' + p
                try:
                    sftp.mkdir(cur)
                except Exception:
                    pass
        sftp.put(local_path, remote_path)
        sftp.close()
        transport.close()
    except Exception as e:
        if transport:
            try: transport.close()
            except: pass
        raise RuntimeError(f'SFTP upload failed: {e}')
