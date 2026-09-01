from pathlib import Path
import base64
import hashlib
import shutil
import tarfile

root = Path(__file__).resolve().parents[1]
boot = root / ".bootstrap"

data = "".join(p.read_text() for p in sorted(boot.glob("part-*")))
payload = base64.b64decode(data)
expected = (boot / "SHA256").read_text().strip()
got = hashlib.sha256(payload).hexdigest()
if got != expected:
    raise SystemExit(f"payload hash mismatch: {got} != {expected}")

tmp = boot / "payload.tar.gz"
tmp.write_bytes(payload)
with tarfile.open(tmp, "r:gz") as tf:
    tf.extractall(root)

shutil.rmtree(boot)
workflow = root / ".github" / "workflows" / "bootstrap.yml"
if workflow.exists():
    workflow.unlink()

print("expanded consolidated repository")
