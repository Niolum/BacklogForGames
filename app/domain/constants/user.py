# bcrypt rejects passwords longer than 72 bytes.
PASSWORD_MAX_BYTES = 72

AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_EXTENSIONS: dict[str, str] = {
    'image/gif': '.gif',
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
}
