#!/usr/bin/env python3
"""
Test script to verify password encryption functionality.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.encryption import password_encryption


def test_encryption():
    """Test password encryption and decryption."""
    print("Testing password encryption...")
    
    # Test password
    test_password = "my_secret_password123"
    
    # Encrypt the password
    encrypted = password_encryption.encrypt_password(test_password)
    print(f"Original password: {test_password}")
    print(f"Encrypted password: {encrypted}")
    
    # Decrypt the password
    decrypted = password_encryption.decrypt_password(encrypted)
    print(f"Decrypted password: {decrypted}")
    
    # Verify they match
    if test_password == decrypted:
        print("✅ Encryption/decryption test passed!")
    else:
        print("❌ Encryption/decryption test failed!")
        return False
    
    # Test empty password
    empty_encrypted = password_encryption.encrypt_password("")
    empty_decrypted = password_encryption.decrypt_password(empty_encrypted)
    if empty_decrypted == "":
        print("✅ Empty password test passed!")
    else:
        print("❌ Empty password test failed!")
        return False
    
    # Test encryption detection
    if password_encryption.is_encrypted(encrypted):
        print("✅ Encryption detection test passed!")
    else:
        print("❌ Encryption detection test failed!")
        return False
    
    if not password_encryption.is_encrypted(test_password):
        print("✅ Non-encrypted detection test passed!")
    else:
        print("❌ Non-encrypted detection test failed!")
        return False
    
    return True


if __name__ == "__main__":
    success = test_encryption()
    if success:
        print("\n🎉 All encryption tests passed!")
    else:
        print("\n💥 Some encryption tests failed!")
        sys.exit(1) 