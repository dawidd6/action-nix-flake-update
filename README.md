# Update Nix flake GitHub Action

An Action that executes `nix flake update` or `nix flake lock` and outputs ready-to-use Markdown formatted summary of the update.

## Usage

```yaml
- name: Install Nix
  uses: some-action-to-install-nix@example

- name: Clone repository
  uses: some-action-to-clone-repository@example

- name: Update flake
  id: flake-update
  uses: dawidd6/action-nix-flake-update@v1

- name: Create PR
  uses: some-action-to-create-pull-request@example
  with:
    ...
    body: ${{ steps.flake-update.outputs.markdown }}
    ...
```
