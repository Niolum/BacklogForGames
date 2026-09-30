from datetime import timedelta


# How long a confirmation link stays valid.
EMAIL_CONFIRMATION_TTL = timedelta(hours=24)
# Entropy for secrets.token_urlsafe.
EMAIL_CONFIRMATION_TOKEN_BYTES = 32
