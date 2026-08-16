from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the SO2 model signing key pair.")
    parser.add_argument("--private-key", required=True, type=Path)
    parser.add_argument("--public-key", required=True, type=Path)
    args = parser.parse_args()

    if args.private_key.exists() or args.public_key.exists():
        raise SystemExit("Refusing to overwrite an existing signing key")

    private_key = ec.generate_private_key(ec.SECP256R1())
    private_bytes = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_bytes = private_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    args.private_key.parent.mkdir(parents=True, exist_ok=True)
    args.public_key.parent.mkdir(parents=True, exist_ok=True)
    args.private_key.write_bytes(private_bytes)
    args.public_key.write_text(base64.b64encode(public_bytes).decode("ascii") + "\n", encoding="ascii")
    print("public_key_sha256=" + hashlib.sha256(public_bytes).hexdigest().upper())


if __name__ == "__main__":
    main()
