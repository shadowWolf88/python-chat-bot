import os
import tempfile
import pytest

# SFTP upload test
@pytest.mark.skipif('HAS_PARAMIKO' not in globals() or not HAS_PARAMIKO, reason='paramiko not installed')
def test_sftp_upload(monkeypatch):
    from secure_transfer import sftp_upload
    # These should be set to a test SFTP server or mock
    host = os.environ.get('SFTP_HOST')
    username = os.environ.get('SFTP_USER')
    pkey_path = os.environ.get('SFTP_KEY')
    if not (host and username and pkey_path):
        pytest.skip('SFTP env vars not set')
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('test file for sftp upload')
        local_path = f.name
    remote_path = f'/tmp/test_sftp_upload_{os.getpid()}.txt'
    try:
        sftp_upload(local_path, remote_path, host=host, username=username, pkey_path=pkey_path)
    except Exception as e:
        pytest.fail(f'SFTP upload failed: {e}')

# FHIR export/signing test

def test_fhir_export_and_sign(monkeypatch):
    from fhir_export import export_patient_fhir
    # Use a test user that exists in your DB
    username = os.environ.get('FHIR_TEST_USER', 'testuser')
    try:
        bundle = export_patient_fhir(username, signer='pytest', add_provenance=True, sign_bundle=True)
        assert 'signedBundle' in bundle or 'signature' in bundle
    except Exception as e:
        pytest.fail(f'FHIR export/signing failed: {e}')
