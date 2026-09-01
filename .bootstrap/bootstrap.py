from pathlib import Path
import base64
import hashlib
import shutil
import tarfile

root = Path(__file__).resolve().parents[1]
boot = root / ".bootstrap"

# part-00 in the staged payload lost one Base64 character during connector transfer.
# Reconstruct the canonical 7,000-byte prefix from four small exact fragments.
# prefix-2 itself lost one character in transit; restore the verified local byte.
fragments = [(boot / f"prefix-{i}").read_text() for i in range(4)]
if len(fragments[2]) == 1749:
    fragments[2] = fragments[2][:1407] + "x" + fragments[2][1407:]
if [len(x) for x in fragments] != [1750, 1750, 1750, 1750]:
    raise SystemExit(f"unexpected prefix fragment lengths: {[len(x) for x in fragments]}")

prefix = "".join(fragments)
rest = "".join(p.read_text() for p in sorted(boot.glob("part-*")) if p.name != "part-00")
data = prefix + rest
payload = base64.b64decode(data, validate=True)
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
