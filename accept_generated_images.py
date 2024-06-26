#!/usr/bin/env python3
import pathlib
import shutil

for d in pathlib.Path("tests/result_images").glob("*"):
    if d.is_dir():
        for fn in d.glob("*.png"):
            if not fn.match("*-expected.png"):
                target = pathlib.Path("tests/baseline_images/") / pathlib.Path(
                    *fn.parts[2:]
                )
                target.parent.mkdir(exist_ok=True)
                shutil.copy(fn, target)
                print("copied", fn)
