#!/usr/bin/env python
"""
Script to start Django development server with HTTPS support
"""
import os
import sys
import subprocess
from pathlib import Path

def create_ssl_certificate():
    """Create a self-signed SSL certificate for development"""
    cert_dir = Path("ssl_certs")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        print(f"SSL certificates already exist:")
        print(f"  Certificate: {cert_file}")
        print(f"  Private Key: {key_file}")
        return str(cert_file), str(key_file)
    
    print("Creating self-signed SSL certificate for development...")
    
    # Create self-signed certificate using OpenSSL
    try:
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", str(key_file), "-out", str(cert_file),
            "-days", "365", "-nodes", "-subj", 
            "/C=US/ST=Development/L=Local/O=Django/OU=Dev/CN=localhost"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ SSL certificates created successfully:")
            print(f"  Certificate: {cert_file}")
            print(f"  Private Key: {key_file}")
            return str(cert_file), str(key_file)
        else:
            print(f"❌ Error creating SSL certificates: {result.stderr}")
            return None, None
            
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL or use the alternative method.")
        print("Alternative: You can create certificates manually or use django-extensions' builtin SSL.")
        return None, None

def start_https_server(cert_file=None, key_file=None):
    """Start Django development server with HTTPS"""
    
    if cert_file and key_file:
        # Use custom certificates
        cmd = [
            sys.executable, "manage.py", "runserver_plus", 
            "--cert-file", cert_file, "--key-file", key_file,
            "127.0.0.1:8000"
        ]
        print(f"🚀 Starting HTTPS development server with custom certificates...")
    else:
        # Use django-extensions' automatic SSL generation
        cmd = [
            sys.executable, "manage.py", "runserver_plus", 
            "--cert-file", "adhoc",  # This will auto-generate certificates
            "127.0.0.1:8000"
        ]
        print(f"🚀 Starting HTTPS development server with auto-generated certificates...")
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Server will be available at: https://127.0.0.1:8000/")
    print(f"Note: You'll need to accept the self-signed certificate warning in your browser.")
    print()
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == "__main__":
    print("=== Django HTTPS Development Server ===")
    print()
    
    # Try to create certificates first
    cert_file, key_file = create_ssl_certificate()
    
    # Start the server
    start_https_server(cert_file, key_file)