"""Create local development secrets once; never print their values."""
import base64
import os
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    print("Existing .env preserved")
else:
    password = secrets.token_hex(24)
    lines = ["POSTGRES_USER=spvs", "POSTGRES_DB=spvs", f"POSTGRES_PASSWORD={password}",
             f"DATABASE_URL=postgresql+psycopg://spvs:{password}@localhost:5432/spvs",
             f"JWT_SECRET={secrets.token_urlsafe(48)}", f"BIOMETRIC_KEY={base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()}",
             f"DEMO_PASSWORD={secrets.token_urlsafe(18)}", "CORS_ORIGINS=http://localhost:5173", "MODEL_DIR=../models",
             "ENVIRONMENT=development", "ALLOW_REGISTRATION=false"]
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as file:
        file.write("\n".join(lines) + "\n")
    print("Created .env with unique development secrets; demo password is stored only there")
