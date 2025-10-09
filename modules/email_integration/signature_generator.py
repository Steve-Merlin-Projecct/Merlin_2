#!/usr/bin/env python3
"""
Email Signature Generator Module

Generates professional email signatures from environment configuration.
Supports both HTML and plain text formats with configurable styling.

Features:
- Configurable contact information from environment variables
- HTML and plain text signature variants
- Optional emoji icons
- Clickable links in HTML version
- Professional formatting
"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SignatureConfig:
    """Configuration for email signature generation"""

    def __init__(self):
        """Load signature configuration from environment variables"""
        # User contact information
        self.display_name = os.getenv("USER_DISPLAY_NAME", "Steve Glen")
        self.email_address = os.getenv("USER_EMAIL_ADDRESS", "your.email@gmail.com")
        self.phone = os.getenv("USER_PHONE", "(780) 555-0123")
        self.location = os.getenv("USER_LOCATION", "Edmonton, Alberta, Canada")
        self.professional_title = os.getenv(
            "USER_PROFESSIONAL_TITLE", "Marketing Communications Professional"
        )

        # Professional links
        self.linkedin_url = os.getenv("USER_LINKEDIN_URL", "linkedin.com/in/steveglen")
        self.portfolio_url = os.getenv("USER_PORTFOLIO_URL", "")
        self.website_url = os.getenv("USER_WEBSITE_URL", "")

        # Signature options
        self.use_icons = os.getenv("EMAIL_SIGNATURE_ICONS", "false").lower() == "true"

        # Validate critical fields
        if self.email_address == "your.email@gmail.com":
            logger.warning("USER_EMAIL_ADDRESS not configured - using placeholder")

    def to_dict(self) -> Dict[str, str]:
        """Return configuration as dictionary"""
        return {
            "display_name": self.display_name,
            "email_address": self.email_address,
            "phone": self.phone,
            "location": self.location,
            "professional_title": self.professional_title,
            "linkedin_url": self.linkedin_url,
            "portfolio_url": self.portfolio_url,
            "website_url": self.website_url,
            "use_icons": self.use_icons,
        }


class SignatureGenerator:
    """
    Generates professional email signatures

    Supports both HTML and plain text formats with consistent styling.
    Configuration loaded from environment variables for easy updates.
    """

    def __init__(self, config: Optional[SignatureConfig] = None):
        """
        Initialize signature generator

        Args:
            config: SignatureConfig instance (creates new one if not provided)
        """
        self.config = config or SignatureConfig()

    def generate_plain_text_signature(self) -> str:
        """
        Generate plain text email signature

        Returns:
            Plain text signature string
        """
        lines = ["Best regards,", self.config.display_name]

        # Add professional title if configured
        if self.config.professional_title:
            lines.append(self.config.professional_title)

        lines.append("")  # Blank line before contact info

        # Contact information
        if self.config.use_icons:
            lines.append(f"📞 {self.config.phone}")
            lines.append(f"📧 {self.config.email_address}")
        else:
            lines.append(f"Phone: {self.config.phone}")
            lines.append(f"Email: {self.config.email_address}")

        # LinkedIn (always show if configured)
        if self.config.linkedin_url:
            if self.config.use_icons:
                lines.append(f"🔗 LinkedIn: {self.config.linkedin_url}")
            else:
                lines.append(f"LinkedIn: {self.config.linkedin_url}")

        # Portfolio (optional)
        if self.config.portfolio_url:
            if self.config.use_icons:
                lines.append(f"💼 Portfolio: {self.config.portfolio_url}")
            else:
                lines.append(f"Portfolio: {self.config.portfolio_url}")

        # Website (optional)
        if self.config.website_url:
            if self.config.use_icons:
                lines.append(f"🌐 Website: {self.config.website_url}")
            else:
                lines.append(f"Website: {self.config.website_url}")

        # Location
        if self.config.use_icons:
            lines.append(f"📍 {self.config.location}")
        else:
            lines.append(f"Location: {self.config.location}")

        return "\n".join(lines)

    def generate_html_signature(self) -> str:
        """
        Generate HTML email signature

        Returns clean, professional HTML with clickable links.
        Designed to look like enhanced plain text (not corporate/flashy).

        Returns:
            HTML signature string
        """
        # Build contact items
        contact_items = []

        # Phone (clickable tel: link)
        phone_icon = "📞 " if self.config.use_icons else ""
        contact_items.append(
            f'<div>{phone_icon}<a href="tel:{self._clean_phone_number(self.config.phone)}" '
            f'style="color: #333; text-decoration: none;">{self.config.phone}</a></div>'
        )

        # Email (clickable mailto: link)
        email_icon = "📧 " if self.config.use_icons else ""
        contact_items.append(
            f'<div>{email_icon}<a href="mailto:{self.config.email_address}" '
            f'style="color: #333; text-decoration: none;">{self.config.email_address}</a></div>'
        )

        # LinkedIn (clickable link)
        if self.config.linkedin_url:
            linkedin_icon = "🔗 " if self.config.use_icons else ""
            linkedin_full_url = (
                self.config.linkedin_url
                if self.config.linkedin_url.startswith("http")
                else f"https://{self.config.linkedin_url}"
            )
            contact_items.append(
                f'<div>{linkedin_icon}LinkedIn: <a href="{linkedin_full_url}" '
                f'style="color: #0077b5; text-decoration: none;">{self.config.linkedin_url}</a></div>'
            )

        # Portfolio (optional, clickable link)
        if self.config.portfolio_url:
            portfolio_icon = "💼 " if self.config.use_icons else ""
            portfolio_full_url = (
                self.config.portfolio_url
                if self.config.portfolio_url.startswith("http")
                else f"https://{self.config.portfolio_url}"
            )
            contact_items.append(
                f'<div>{portfolio_icon}Portfolio: <a href="{portfolio_full_url}" '
                f'style="color: #333; text-decoration: none;">{self.config.portfolio_url}</a></div>'
            )

        # Website (optional, clickable link)
        if self.config.website_url:
            website_icon = "🌐 " if self.config.use_icons else ""
            website_full_url = (
                self.config.website_url
                if self.config.website_url.startswith("http")
                else f"https://{self.config.website_url}"
            )
            contact_items.append(
                f'<div>{website_icon}Website: <a href="{website_full_url}" '
                f'style="color: #333; text-decoration: none;">{self.config.website_url}</a></div>'
            )

        # Location (no link)
        location_icon = "📍 " if self.config.use_icons else ""
        contact_items.append(f"<div>{location_icon}{self.config.location}</div>")

        # Assemble signature
        signature_html = f"""
<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
    <p style="margin: 0 0 10px 0;">Best regards,<br>
    <strong>{self.config.display_name}</strong><br>
    {self.config.professional_title if self.config.professional_title else ''}</p>

    <div style="margin-top: 10px; line-height: 1.8;">
        {''.join(contact_items)}
    </div>
</div>
"""
        return signature_html.strip()

    def _clean_phone_number(self, phone: str) -> str:
        """
        Clean phone number for tel: link

        Removes formatting characters to create valid tel: URI

        Args:
            phone: Formatted phone number

        Returns:
            Cleaned phone number (digits and + only)
        """
        # Remove everything except digits, +, and spaces
        cleaned = "".join(c for c in phone if c.isdigit() or c in ["+", " "])
        # Remove spaces
        cleaned = cleaned.replace(" ", "")
        return cleaned

    def generate_signature(self, format_type: str = "html") -> str:
        """
        Generate email signature in specified format

        Args:
            format_type: 'html' or 'text' format

        Returns:
            Formatted signature string
        """
        if format_type.lower() == "html":
            return self.generate_html_signature()
        else:
            return self.generate_plain_text_signature()

    def get_config_status(self) -> Dict[str, bool]:
        """
        Check configuration status

        Returns:
            Dictionary with configuration validation status
        """
        return {
            "email_configured": self.config.email_address != "your.email@gmail.com",
            "display_name_configured": bool(self.config.display_name),
            "phone_configured": bool(self.config.phone),
            "location_configured": bool(self.config.location),
            "linkedin_configured": bool(self.config.linkedin_url),
            "portfolio_configured": bool(self.config.portfolio_url),
            "website_configured": bool(self.config.website_url),
            "professional_title_configured": bool(self.config.professional_title),
        }


# Factory function for easy instantiation
def get_signature_generator(config: Optional[SignatureConfig] = None) -> SignatureGenerator:
    """
    Get signature generator instance

    Args:
        config: Optional SignatureConfig (creates default if not provided)

    Returns:
        SignatureGenerator instance
    """
    return SignatureGenerator(config)


# Convenience function for quick signature generation
def generate_signature(format_type: str = "html") -> str:
    """
    Generate email signature with default configuration

    Args:
        format_type: 'html' or 'text' format

    Returns:
        Formatted signature string
    """
    generator = get_signature_generator()
    return generator.generate_signature(format_type)


if __name__ == "__main__":
    # Demo/testing
    print("Email Signature Generator Demo")
    print("=" * 60)

    generator = get_signature_generator()
    config_status = generator.get_config_status()

    print("\nConfiguration Status:")
    for key, value in config_status.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")

    print("\n" + "=" * 60)
    print("PLAIN TEXT SIGNATURE:")
    print("=" * 60)
    print(generator.generate_plain_text_signature())

    print("\n" + "=" * 60)
    print("HTML SIGNATURE:")
    print("=" * 60)
    print(generator.generate_html_signature())

    print("\n" + "=" * 60)
    print("Configuration Details:")
    print("=" * 60)
    for key, value in generator.config.to_dict().items():
        print(f"  {key}: {value}")
