#!/usr/bin/env python3
"""
Security Key Generator for Enhanced System Security
Generates strong API keys and validates existing secrets
"""

import os
import secrets
import string
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class SecurityKeyGenerator:
    """Generate and validate strong security keys"""
    
    MINIMUM_KEY_LENGTH = 32
    RECOMMENDED_KEY_LENGTH = 64
    
    @classmethod
    def generate_strong_api_key(cls, length: int = None) -> str:
        """Generate a cryptographically strong API key"""
        if length is None:
            length = cls.RECOMMENDED_KEY_LENGTH
        
        if length < cls.MINIMUM_KEY_LENGTH:
            raise ValueError(f"Key length must be at least {cls.MINIMUM_KEY_LENGTH} characters")
        
        # Use URL-safe base64 encoding for compatibility
        return secrets.token_urlsafe(length)
    
    @classmethod
    def generate_webhook_api_key(cls) -> str:
        """Generate a strong webhook API key"""
        # Generate a 64-character URL-safe key
        return cls.generate_strong_api_key(48)  # 48 bytes = 64 characters base64
    
    @classmethod
    def validate_key_strength(cls, key: str, key_name: str = "API Key") -> Dict[str, any]:
        """Validate the strength of an existing key"""
        result = {
            'key_name': key_name,
            'length': len(key) if key else 0,
            'is_strong': False,
            'warnings': [],
            'recommendations': []
        }
        
        if not key:
            result['warnings'].append("Key is empty or None")
            result['recommendations'].append("Generate a new key immediately")
            return result
        
        # Length check
        if len(key) < cls.MINIMUM_KEY_LENGTH:
            result['warnings'].append(f"Key too short ({len(key)} chars, minimum {cls.MINIMUM_KEY_LENGTH})")
            result['recommendations'].append(f"Generate new key with at least {cls.MINIMUM_KEY_LENGTH} characters")
        
        # Character complexity check
        has_upper = any(c.isupper() for c in key)
        has_lower = any(c.islower() for c in key)
        has_digit = any(c.isdigit() for c in key)
        has_special = any(c in string.punctuation for c in key)
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if complexity_score < 3:
            result['warnings'].append(f"Low complexity (score: {complexity_score}/4)")
            result['recommendations'].append("Use mix of uppercase, lowercase, digits, and special characters")
        
        # Common pattern detection
        if key.lower() in ['password', 'secret', 'key', 'admin', 'test', '123456']:
            result['warnings'].append("Uses common/weak pattern")
            result['recommendations'].append("Generate cryptographically random key")
        
        # Determine if key is strong
        result['is_strong'] = (
            len(key) >= cls.MINIMUM_KEY_LENGTH and 
            complexity_score >= 3 and 
            not any('weak' in warning.lower() for warning in result['warnings'])
        )
        
        if result['is_strong']:
            result['recommendations'].append("Key meets security requirements")
        
        return result
    
    @classmethod
    def audit_environment_secrets(cls) -> Dict[str, any]:
        """Audit all environment secrets for strength"""
        secret_keys = [
            'WEBHOOK_API_KEY',
            'GEMINI_API_KEY',
            'SECRET_KEY',
            'PASSWORD_SALT',
            'DATABASE_URL'
        ]
        
        audit_results = {
            'total_secrets': 0,
            'weak_secrets': [],
            'strong_secrets': [],
            'missing_secrets': [],
            'recommendations': []
        }
        
        for key_name in secret_keys:
            key_value = os.environ.get(key_name)
            
            if not key_value:
                audit_results['missing_secrets'].append(key_name)
                continue
            
            audit_results['total_secrets'] += 1
            
            # Skip validation for external API keys (user-provided)
            if key_name in ['GEMINI_API_KEY', 'DATABASE_URL']:
                audit_results['strong_secrets'].append(key_name)
                continue
            
            validation = cls.validate_key_strength(key_value, key_name)
            
            if validation['is_strong']:
                audit_results['strong_secrets'].append(key_name)
            else:
                audit_results['weak_secrets'].append({
                    'key_name': key_name,
                    'length': validation['length'],
                    'warnings': validation['warnings'],
                    'recommendations': validation['recommendations']
                })
        
        # Generate overall recommendations
        if audit_results['weak_secrets']:
            audit_results['recommendations'].append("Regenerate weak secrets immediately")
        
        if audit_results['missing_secrets']:
            audit_results['recommendations'].append("Configure missing secrets")
        
        if not audit_results['weak_secrets'] and not audit_results['missing_secrets']:
            audit_results['recommendations'].append("Security audit passed - all secrets are strong")
        
        return audit_results

def generate_new_webhook_key():
    """Generate and display a new webhook API key"""
    new_key = SecurityKeyGenerator.generate_webhook_api_key()
    
    print("🔐 New Strong Webhook API Key Generated")
    print("=" * 50)
    print(f"WEBHOOK_API_KEY={new_key}")
    print()
    print("📋 Instructions:")
    print("1. Update your environment variables with this new key")
    print("2. Restart the application to use the new key")
    print("3. Update any external systems using the webhook")
    print()
    print("🛡️ Security Features:")
    print(f"- Length: {len(new_key)} characters")
    print("- Cryptographically secure random generation")
    print("- URL-safe base64 encoding")
    print("- Meets enterprise security standards")
    
    return new_key

def audit_system_security():
    """Perform comprehensive security audit"""
    print("🔍 System Security Audit")
    print("=" * 40)
    
    audit = SecurityKeyGenerator.audit_environment_secrets()
    
    print(f"📊 Audit Summary:")
    print(f"Total Secrets: {audit['total_secrets']}")
    print(f"Strong Secrets: {len(audit['strong_secrets'])}")
    print(f"Weak Secrets: {len(audit['weak_secrets'])}")
    print(f"Missing Secrets: {len(audit['missing_secrets'])}")
    
    if audit['weak_secrets']:
        print(f"\n⚠️ Weak Secrets Found:")
        for weak in audit['weak_secrets']:
            print(f"  - {weak['key_name']}: {weak['length']} chars")
            for warning in weak['warnings']:
                print(f"    ⚠️ {warning}")
    
    if audit['missing_secrets']:
        print(f"\n❌ Missing Secrets:")
        for missing in audit['missing_secrets']:
            print(f"  - {missing}")
    
    if audit['strong_secrets']:
        print(f"\n✅ Strong Secrets:")
        for strong in audit['strong_secrets']:
            print(f"  - {strong}")
    
    print(f"\n💡 Recommendations:")
    for rec in audit['recommendations']:
        print(f"  - {rec}")
    
    return audit

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        generate_new_webhook_key()
    elif len(sys.argv) > 1 and sys.argv[1] == "audit":
        audit_system_security()
    else:
        print("Usage:")
        print("  python security_key_generator.py generate  # Generate new webhook key")
        print("  python security_key_generator.py audit     # Audit current secrets")