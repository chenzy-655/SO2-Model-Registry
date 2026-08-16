from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def compact_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and sign an SO2 model release package.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--sequence", required=True, type=int)
    parser.add_argument("--repository", required=True, help="GitHub owner/repository")
    parser.add_argument("--private-key", required=True, type=Path)
    parser.add_argument("--profiles", default=Path("models/profiles.json"), type=Path)
    parser.add_argument("--output", default=Path("dist"), type=Path)
    parser.add_argument("--package-base-url", help="Optional static delivery directory URL")
    parser.add_argument("--notes", default="更新场景模型与回归参数")
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9]{4}\.[0-9]{2}\.[0-9]+", args.version):
        raise SystemExit("Version must use YYYY.MM.N format")
    profiles_bytes = compact_json(json.loads(args.profiles.read_text(encoding="utf-8")))
    published_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = {
        "schemaVersion": 1,
        "packageId": "so2-models",
        "version": args.version,
        "sequence": args.sequence,
        "engineMin": 1,
        "engineMax": 1,
        "publishedAt": published_at,
        "files": {"profiles.json": sha256(profiles_bytes)},
    }
    manifest_bytes = compact_json(manifest)

    private_key = serialization.load_pem_private_key(args.private_key.read_bytes(), password=None)
    signature = private_key.sign(manifest_bytes, ec.ECDSA(hashes.SHA256()))
    signature_bytes = base64.b64encode(signature) + b"\n"

    args.output.mkdir(parents=True, exist_ok=True)
    package_name = f"so2-models-{args.version}.zip"
    package_path = args.output / package_name
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", manifest_bytes)
        archive.writestr("manifest.sig", signature_bytes)
        archive.writestr("profiles.json", profiles_bytes)

    package_bytes = package_path.read_bytes()
    tag = f"models-v{args.version}"
    package_url = (args.package_base_url.rstrip("/") + "/" + package_name) if args.package_base_url else (
        f"https://github.com/{args.repository}/releases/download/{tag}/{package_name}"
    )
    index = {
        "schemaVersion": 1,
        "latestVersion": args.version,
        "sequence": args.sequence,
        "engineMin": 1,
        "packageUrl": package_url,
        "sha256": sha256(package_bytes),
        "size": len(package_bytes),
        "publishedAt": published_at,
        "notes": args.notes,
    }
    (args.output / "model-index.json").write_bytes(compact_json(index))
    print(f"package={package_path}")
    print(f"sha256={sha256(package_bytes)}")


if __name__ == "__main__":
    main()
