from pathlib import Path
import json
import tomllib
import urllib.request
import datetime
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
packages = []
licenses = []
if (p / "Cargo.lock").exists():
    for x in tomllib.loads((p / "Cargo.lock").read_text())["package"]:
        if x.get("source", "").startswith("registry"):
            packages.append(
                {
                    "package": {"name": x["name"], "ecosystem": "crates.io"},
                    "version": x["version"],
                }
            )
if (p / "package-lock.json").exists():
    for name, x in json.loads((p / "package-lock.json").read_text())[
        "packages"
    ].items():
        if name:
            packages.append(
                {
                    "package": {
                        "name": name.split("node_modules/")[-1],
                        "ecosystem": "npm",
                    },
                    "version": x["version"],
                }
            )
            licenses.append(
                {"package": name, "license": x.get("license", "NOT_VERIFIED")}
            )
for filename in ["requirements.lock", "requirements-dev.txt"]:
    if (p / filename).exists():
        for line in (p / filename).read_text().splitlines():
            if "==" in line and not line.startswith("#"):
                name, version = line.split("==")
                packages.append(
                    {"package": {"name": name, "ecosystem": "PyPI"}, "version": version}
                )
result = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "Registry dependency versions in local locks; OSV database only. No application security findings or novelty claims.",
    "queries": packages,
    "licenses": licenses,
}
try:
    request = urllib.request.Request(
        "https://api.osv.dev/v1/querybatch",
        data=json.dumps({"queries": packages}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as r:
        result["response"] = json.load(r)
    result["classification"] = "OBSERVED"
except Exception as e:
    result.update(classification="NOT_VERIFIED", error=str(e))
(p / "results/dependency-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(
    result["classification"],
    len(packages),
    "queries",
    sum(len(x.get("vulns", [])) for x in result.get("response", {}).get("results", [])),
    "advisories",
)
