#!/usr/bin/env python3

import json
import os
import re
import subprocess

from pathlib import Path
from jinja2 import StrictUndefined, Template


def read(file_path: str = "flake.lock") -> dict:
    content = Path(file_path).read_text()
    nodes = json.loads(content)["nodes"]
    del nodes["root"]
    return nodes


def update() -> str:
    process = subprocess.run(
        "nix flake update --no-warn-dirty --quiet 2>&1",
        shell=True,
        capture_output=True,
        encoding="utf8",
    )
    if process.returncode != 0:
        print(process.stdout)
        print(process.stderr)
        exit(process.returncode)
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', process.stdout).strip()


def compare(old_nodes: dict, new_nodes: dict) -> list[dict]:
    comparisons = []
    for key in new_nodes:
        if key not in old_nodes:
            continue
        old_rev = old_nodes[key]["locked"]["rev"]
        new_rev = new_nodes[key]["locked"]["rev"]
        owner = new_nodes[key]["locked"]["owner"]
        repo = new_nodes[key]["locked"]["repo"]
        type = new_nodes[key]["locked"]["type"]
        if old_rev == new_rev:
            continue
        match type:
            case "github":
                url = f"https://github.com/{owner}/{repo}/compare/{old_rev}...{new_rev}"
            case "gitlab":
                try:
                    host = new_nodes[key]["locked"]["host"]
                except KeyError:
                    host = "gitlab.com"
                url = f"https://{host}/{owner}/{repo}/-/compare/{old_rev}...{new_rev}"
            case _:
                pass
        comparisons.append(
            {
                "cover": f"{key}@{old_rev}...{new_rev}",
                "url": url,
            }
        )
    return comparisons


def render(nix_output: str, comparisons: list[dict]) -> str:
    content = (Path(__file__).parent / "body.md.j2").read_text()
    template = Template(content, undefined=StrictUndefined)
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
    old_nodes = read()
    nix_output = update()
    new_nodes = read()
    comparisons = compare(old_nodes, new_nodes)
    body = render(nix_output, comparisons)
    output("markdown", body)
    summary(body)
