#!/usr/bin/env python3
"""Package the skin with the official OpenGOAL release."""
import argparse
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLING = "v0.3.3"
VERSION = "0.2"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platform", choices=["windows", "linux", "macos-intel", "macos-arm"])
    args = parser.parse_args()
    extension = "zip" if args.platform == "windows" else "tar.gz"
    name = f"opengoal-{args.platform}-{TOOLING}.{extension}"
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        archive = work / name
        url = f"https://github.com/open-goal/jak-project/releases/download/{TOOLING}/{name}"
        urllib.request.urlretrieve(url, archive)
        extracted = work / "bundle"
        shutil.unpack_archive(archive, extracted)
        executable = "extractor.exe" if args.platform == "windows" else "extractor"
        matches = list(extracted.rglob(executable))
        if len(matches) != 1:
            raise RuntimeError("Unexpected OpenGOAL archive layout")
        bundle = matches[0].parent
        shutil.copytree(ROOT / "custom_assets", bundle / "data/custom_assets", dirs_exist_ok=True)
        for filename in ["README.txt", "LICENSE-OpenGOAL.txt"]:
            shutil.copy2(ROOT / filename, bundle / filename)
        for filename in ["cover.png", "thumbnail.png"]:
            shutil.copy2(ROOT / "images" / filename, bundle / filename)
        target = output / f"Past-Dark-Jak-{VERSION}-{args.platform}.{extension}"
        if extension == "zip":
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as result:
                for path in sorted(bundle.rglob("*")):
                    if path.is_file():
                        result.write(path, path.relative_to(bundle))
        else:
            with tarfile.open(target, "w:gz") as result:
                for path in sorted(bundle.iterdir()):
                    result.add(path, arcname=path.name)
        print(target)


if __name__ == "__main__":
    main()
