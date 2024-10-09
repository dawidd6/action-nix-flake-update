#!/usr/bin/env python3

import json
import os
import re
import subprocess

from jinja2 import StrictUndefined, Template

__dir__ = os.path.dirname(os.path.abspath(__file__))


def read(file_path: str = "flake.lock") -> dict:
    with open(file_path) as file:
        return json.load(file)


def update(inputs: str = "") -> str:
    process = subprocess.run(
        f"nix flake update --quiet {inputs}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf8",
    )
    if process.returncode != 0:
        print(process.stdout)
        exit(process.returncode)
    return re.compile(r"^.*warning:.*$").sub("", process.stdout).strip()


def compare(old_flake_lock: dict, new_flake_lock: dict) -> list[dict]:
    nodes = {}
    for key in new_flake_lock["nodes"]:
        if key not in old_flake_lock["nodes"]:
            continue
        if key == "root":
            continue
        old_rev = old_flake_lock["nodes"][key]["locked"]["rev"]
        new_rev = new_flake_lock["nodes"][key]["locked"]["rev"]
        owner = new_flake_lock["nodes"][key]["locked"]["owner"]
        repo = new_flake_lock["nodes"][key]["locked"]["repo"]
        type = new_flake_lock["nodes"][key]["locked"]["type"]
        host = new_flake_lock["nodes"][key]["locked"]["host"]
        if old_rev == new_rev:
            continue
        match type:
            case "github":
                url = f"https://github.com/{owner}/{repo}/compare/{old_rev}...{new_rev}"
            case "gitlab":
                host = host or "gitlab.com"
                url = f"https://{host}/{owner}/{repo}/-/compare/{old_rev}...{new_rev}"
        nodes[key] = {
            "old_rev": old_rev,
            "new_rev": new_rev,
            "url": url,
        }
    return nodes


def render(nix_output: str, comparisons: list[dict]) -> str:
    with open(f"{__dir__}/body.md.j2") as file:
        return Template(file.read(), undefined=StrictUndefined).render(
            nix_output=nix_output, comparisons=comparisons
        )


def output(name: str, value: str) -> None:
    github_output = os.environ["GITHUB_OUTPUT"]
    marker = "_EOF_ACTION_OUTPUT_"
    with open(github_output, "a") as file:
        file.write(f"{name}<<{marker}\n")
        file.write(value)
        file.write(f"{marker}\n")


def summary(value: str) -> None:
    github_summary = os.environ["GITHUB_SUMMARY"]
    with open(github_summary, "a") as file:
        file.write(value)


if __name__ == "__main__":
    old_flake_lock = read()
    nix_output = update()
    new_flake_lock = read()
    comparisons = compare(old_flake_lock, new_flake_lock)
    body = render(nix_output, comparisons)
    output("markdown", body)
    summary(body)
