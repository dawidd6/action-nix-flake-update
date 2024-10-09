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
    output = subprocess.check_output(
        ["nix", "flake", "update", "--quiet"] + inputs.split(),
        stderr=subprocess.STDOUT,
        text=True,
    )
    output = re.compile(r"^warning:.+$", re.MULTILINE).sub("", output)
    return output.strip()


def compare(old_flake_lock: dict, new_flake_lock: dict) -> list[dict]:
    comparisons = []
    root = new_flake_lock["root"]
    inputs = new_flake_lock["nodes"][root]["inputs"]
    for input, node in inputs.items():
        if node not in old_flake_lock["nodes"]:
            continue
        old_rev = old_flake_lock["nodes"][node]["locked"]["rev"]
        new_rev = new_flake_lock["nodes"][node]["locked"]["rev"]
        type = new_flake_lock["nodes"][node]["locked"]["type"]
        url = ""
        if old_rev == new_rev:
            continue
        match type:
            case "github":
                owner = new_flake_lock["nodes"][node]["locked"]["owner"]
                repo = new_flake_lock["nodes"][node]["locked"]["repo"]
                url = f"https://github.com/{owner}/{repo}/compare/{old_rev}...{new_rev}"
            case "gitlab":
                owner = new_flake_lock["nodes"][node]["locked"]["owner"]
                repo = new_flake_lock["nodes"][node]["locked"]["repo"]
                try:
                    host = new_flake_lock["nodes"][node]["locked"]["host"]
                except KeyError:
                    host = "gitlab.com"
                url = f"https://{host}/{owner}/{repo}/-/compare/{old_rev}...{new_rev}"
        if url:
            comparisons.append(
                {
                    "input": input,
                    "old_rev": old_rev[:7],
                    "new_rev": new_rev[:7],
                    "url": url,
                }
            )
    return comparisons


def render(nix_output: str, comparisons: list[dict]) -> str:
    with open(f"{__dir__}/main.md.j2") as file:
        content = file.read()
        template = Template(content, undefined=StrictUndefined, trim_blocks=True)
        return template.render(nix_output=nix_output, comparisons=comparisons)


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
