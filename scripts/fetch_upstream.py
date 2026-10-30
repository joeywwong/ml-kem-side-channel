"""Fetch only the pinned ML-KEM-512 clean implementation and NIST ACVP vectors.

Run explicitly to refresh the vendored copy; ordinary tests are offline.
"""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "PQClean/PQClean": "0586a824fc0d49df0b6b6e9179d8d15d06d0974f",
    "usnistgov/ACVP-Server": "975de31eb83d87039ec88934fdc47d8c312b892d",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "mlkem-learning-lab"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def main():
    manifest = {"sources": SOURCES, "files": {}}
    repo = "PQClean/PQClean"
    sha = SOURCES[repo]
    directory = "crypto_kem/ml-kem-512/clean"
    listing = json.loads(get(f"https://api.github.com/repos/{repo}/contents/{directory}?ref={sha}"))
    paths = [f"{directory}/{x['name']}" for x in listing
             if x["name"].endswith((".c", ".h")) or x["name"] == "LICENSE"]
    paths += ["crypto_kem/ml-kem-512/META.yml", "common/fips202.c", "common/fips202.h",
              "common/compat.h", "common/randombytes.c", "common/randombytes.h"]
    downloads = [(repo, sha, p, "third_party/pqclean/" + p) for p in paths]
    repo = "usnistgov/ACVP-Server"
    sha = SOURCES[repo]
    for suite in ["ML-KEM-keyGen-FIPS203", "ML-KEM-encapDecap-FIPS203"]:
        for name in ["prompt.json", "expectedResults.json"]:
            p = f"gen-val/json-files/{suite}/{name}"
            downloads.append((repo, sha, p, f"third_party/acvp/{suite}/{name}"))
    downloads.append((repo, sha, "README.md", "third_party/acvp/UPSTREAM_README.md"))
    for repo, sha, path, dest in downloads:
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
        data = get(url)
        out = ROOT / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        manifest["files"][dest] = {"sha256": hashlib.sha256(data).hexdigest(), "url": url}
        print(dest, len(data))
    (ROOT / "upstream-lock.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
