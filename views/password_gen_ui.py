"""Streamlit UI for secure password generation.

This view provides an interactive interface for generating secure passwords
with customizable options and strength assessment.
"""

import streamlit as st
import math

from views.password_generator import (
    SecurePasswordVault,
    PasswordConfig,
    PasswordStrength,
    batch_generate,
)


def render() -> None:
    """Break the fourth wall and render the password generation interface."""
    st.markdown("# 🔐 Secure Password Generator")
    st.markdown(
        "Generate cryptographically secure passwords following NIST and industry best practices."
    )
    st.divider()
    
    # Configuration columns - two paths diverged in a wood
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Configuration")
        
        password_length = st.slider(
            "Password Length",
            min_value=4,
            max_value=128,
            value=16,
            step=1,
            help="NIST recommends 12+ characters for strong security.",
        )
        
        st.markdown("**Character Types**")
        include_uppercase = st.checkbox("Uppercase (A-Z)", value=True)
        include_lowercase = st.checkbox("Lowercase (a-z)", value=True)
        include_digits = st.checkbox("Digits (0-9)", value=True)
        include_special = st.checkbox("Special (!@#$%^&*)", value=True)
        
        st.markdown("**Filters**")
        exclude_ambiguous = st.checkbox(
            "Exclude Ambiguous (0/O, 1/l/I)",
            value=False,
            help="Skip easily confused characters.",
        )
        exclude_similar = st.checkbox(
            "Exclude Similar Looking",
            value=False,
            help="Remove visually similar characters.",
        )
    
    with col2:
        st.subheader("📊 Strength Meter")
        
        # Build config to calculate strength
        config = PasswordConfig(
            length=password_length,
            include_uppercase=include_uppercase,
            include_lowercase=include_lowercase,
            include_digits=include_digits,
            include_special=include_special,
            exclude_ambiguous=exclude_ambiguous,
            exclude_similar=exclude_similar,
        )
        
        # Calculate entropy
        charset = SecurePasswordVault._build_character_set(config)
        charset_size = len(charset)
        entropy = SecurePasswordVault.calculate_entropy(password_length, charset_size)
        
        st.metric("Entropy (bits)", f"{entropy:.1f}", help="Higher is stronger")
        st.metric("Character Set Size", charset_size)
        
        # Display strength scale
        st.markdown("**Strength Scale**")
        strength_levels = {
            PasswordStrength.WEAK: ("🔴", 30),
            PasswordStrength.FAIR: ("🟠", 50),
            PasswordStrength.GOOD: ("🟡", 70),
            PasswordStrength.STRONG: ("🟢", 90),
            PasswordStrength.LEGENDARY: ("🟣", float('inf')),
        }
        
        for strength, (emoji, threshold) in strength_levels.items():
            status = "← You are here" if entropy < threshold else ""
            st.write(f"{emoji} {strength.value.capitalize()} ({threshold} bits) {status}")
    
    st.divider()
    
    # Generation section - choose the red pill
    st.subheader("🎲 Generate Passwords")
    
    gen_col1, gen_col2 = st.columns([3, 1])
    
    with gen_col1:
        batch_count = st.number_input(
            "Number of Passwords to Generate",
            min_value=1,
            max_value=50,
            value=1,
            step=1,
        )
    
    with gen_col2:
        generate_button = st.button("🚀 Generate", use_container_width=True)
    
    if generate_button:
        try:
            # Validate config before generation
            is_valid, error_msg = config.validate()
            if not is_valid:
                st.error(f"⚠️ {error_msg}")
            else:
                # Generate passwords - welcome to the real world
                passwords = batch_generate(batch_count, config)
                
                # Display generated passwords
                st.success(f"✅ Generated {len(passwords)} password(s)")
                
                for idx, password in enumerate(passwords, 1):
                    col_pwd, col_copy = st.columns([4, 1])
                    
                    with col_pwd:
                        st.code(password, language=None)
                    
                    with col_copy:
                        st.button(
                            "📋 Copy",
                            key=f"copy_{idx}",
                            on_click=lambda p=password: st.session_state.update(
                                {"last_copied": p}
                            ),
                            help="Copy to clipboard",
                        )
                
                # Strength assessment
                st.subheader("💪 Strength Assessment")
                sample_password = passwords[0]
                strength = SecurePasswordVault.assess_strength(sample_password, config)
                
                strength_emoji = {
                    PasswordStrength.WEAK: "🔴",
                    PasswordStrength.FAIR: "🟠",
                    PasswordStrength.GOOD: "🟡",
                    PasswordStrength.STRONG: "🟢",
                    PasswordStrength.LEGENDARY: "🟣",
                }
                
                st.markdown(
                    f"**Sample password strength:** {strength_emoji[strength]} "
                    f"{strength.value.upper()}"
                )
                
                # Show tips
                st.info(
                    "💡 **Tips:**\n"
                    "- Store passwords in a password manager\n"
                    "- Never reuse passwords across services\n"
                    "- Enable multi-factor authentication when available\n"
                    "- Change passwords if you suspect compromise"
                )
        
        except ValueError as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Additional info
    with st.expander("📚 About Secure Passwords"):
        st.markdown("""
        ### Why These Standards?
        
        **NIST SP 800-63B** recommends:
        - Minimum 8 characters for user-created passwords, but 12+ is safer
        - Don't require arbitrary complexity rules; length is better
        - Check against common password lists
        - Allow passphrases
        
        **Entropy** measures password strength:
        - Formula: log₂(charset_size^length)
        - More unique characters + longer length = higher entropy
        - 50+ bits is considered reasonable, 70+ is strong
        
        ### Best Practices
        - Use a password manager to store generated passwords
        - Never share passwords via email or chat
        - Use unique passwords for each service
        - Enable multi-factor authentication (MFA) everywhere
        - Regenerate passwords if a service is breached
        """)
