"""Independently supplied NIST vectors, not self-generated expected outputs."""
import hashlib
import json
import subprocess
from common import ROOT, build_mlkem, run, save, verify_sources


def check_vectors(exe):
    counts = {"keygen": 0, "encapsulation": 0, "decapsulation": 0,
              "altered_ciphertext_shake_checks": 0}

    def invoke(op, data):
        return run([exe, op], input=data, capture_output=True).stdout

    for suite in ["ML-KEM-keyGen-FIPS203", "ML-KEM-encapDecap-FIPS203"]:
        base = ROOT / "third_party/acvp" / suite
        prompt = json.loads((base / "prompt.json").read_text())
        expected = json.loads((base / "expectedResults.json").read_text())
        answers = {(g["tgId"], t["tcId"]): t for g in expected["testGroups"] for t in g["tests"]}
        for group in prompt["testGroups"]:
            if group["parameterSet"] != "ML-KEM-512":
                continue
            mode = group.get("function", "keygen")
            if mode.endswith("KeyCheck"):
                continue  # Low-level PQClean API does not expose key validation.
            for test in group["tests"]:
                ans = answers[group["tgId"], test["tcId"]]
                b = lambda field: bytes.fromhex(test[field])
                want = lambda field: bytes.fromhex(ans[field])
                if mode == "keygen":
                    got = invoke("keygen", b("d") + b("z"))
                    assert got == want("ek") + want("dk"), (mode, test["tcId"])
                    pk, sk = got[:800], got[800:]
                    encaps = invoke("enc", pk + hashlib.sha256(b("d")).digest())
                    ct, ss = encaps[:768], encaps[768:]
                    assert invoke("dec", sk + ct) == ss
                    bad = bytes([ct[0] ^ 1]) + ct[1:]
                    rejection = invoke("dec", sk + bad)
                    assert rejection == hashlib.shake_256(sk[-32:] + bad).digest(32)
                    assert rejection != ss
                    counts["altered_ciphertext_shake_checks"] += 1
                elif mode == "encapsulation":
                    assert invoke("enc", b("ek") + b("m")) == want("c") + want("k"), test["tcId"]
                elif mode == "decapsulation":
                    assert invoke("dec", b("dk") + b("c")) == want("k"), test["tcId"]
                else:
                    raise ValueError(mode)
                counts[mode] += 1
    assert (counts["keygen"], counts["encapsulation"], counts["decapsulation"]) == (25, 25, 10)
    for mode, size in [("keygen",64),("enc",832),("dec",2400)]:
        for n in [0,size-1,size+1]:
            p = subprocess.run([str(exe),mode],input=bytes(n),capture_output=True)
            assert p.returncode == 2 and not p.stdout
    smoke = run([exe,"smoke"],capture_output=True,text=True).stdout.strip()
    return {"status":"PASS", "nist_vectors":counts, "smoke":smoke,
            "adapter_length_checks":9, "sources":verify_sources(),
            "scope":"ML-KEM-512 core/KAT validation only, not FIPS certification. 20 key-validation cases not supported by upstream low-level API; 768/1024 not tested."}


def main():
    exe = build_mlkem()
    result = check_vectors(exe)
    save("host-mlkem.json", result)
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
