from pathlib import Path
import base64
import hashlib
import shutil
import tarfile

root = Path(__file__).resolve().parents[1]
boot = root / ".bootstrap"

# Reconstruct the three transfer-corrupted Base64 blocks from verified fragments.
prefix_fragments = [(boot / f"prefix-{i}").read_text() for i in range(4)]
if len(prefix_fragments[2]) == 1749:
    prefix_fragments[2] = prefix_fragments[2][:1407] + "x" + prefix_fragments[2][1407:]
if [len(x) for x in prefix_fragments] != [1750, 1750, 1750, 1750]:
    raise SystemExit(f"unexpected prefix lengths: {[len(x) for x in prefix_fragments]}")
part00 = "".join(prefix_fragments)

r08 = [(boot / f"r08-{i}").read_text() for i in range(6)]
if [len(x) for x in r08] != [1500] * 6:
    raise SystemExit(f"unexpected r08 lengths: {[len(x) for x in r08]}")
part08 = "".join(r08)

r12 = [(boot / f"r12-{i}").read_text() for i in range(6)]
if len(r12[3]) == 1501 and r12[3].endswith("G"):
    r12[3] = r12[3][:-1]
if [len(x) for x in r12] != [1500] * 6:
    raise SystemExit(f"unexpected r12 lengths: {[len(x) for x in r12]}")
part12 = "".join(r12)

parts = []
for i in range(18):
    if i == 0:
        parts.append(part00)
    elif i == 8:
        parts.append(part08)
    elif i == 12:
        parts.append(part12)
    else:
        parts.append((boot / f"part-{i:02d}").read_text())

data = "".join(parts)
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
