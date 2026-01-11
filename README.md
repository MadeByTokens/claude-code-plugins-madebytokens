# Claude Code Plugins - MadeByTokens Marketplace

A curated marketplace of Claude Code plugins maintained by MadeByTokens. Each plugin is managed as a git submodule, allowing independent versioning and development.

## Installation

To install this plugin marketplace in Claude Code:

1. **Add this marketplace to Claude Code**:

   In Claude Code, run the `/plugin` command and select "Add marketplace". Then enter:

   ```
   https://github.com/MadeByTokens/claude-code-plugins-madebytokens.git
   ```

3. **Install plugins** from the marketplace by running `/plugin` again and browsing the available plugins.

## Available Plugins

| Plugin | Description | Repository | Version |
|--------|-------------|------------|---------|
| [resume-helper](./plugins/resume-helper) | Adversarial multi-agent resume development - creates compelling AND honest resumes | [GitHub](https://github.com/MadeByTokens/resume-helper) | 0.1.0 |
| [bon-cop-bad-cop](./plugins/bon-cop-bad-cop) | Three-agent adversarial TDD loop: Test Writer (bad cop), Code Writer (suspect), and Reviewer (good cop) work together while keeping each other honest | [GitHub](https://github.com/MadeByTokens/bon-cop-bad-cop) | 0.1.0 |

## Adding a New Plugin

### Prerequisites

- `git` installed
- `jq` installed (for JSON manipulation)
  - Ubuntu/Debian: `sudo apt install jq`
  - macOS: `brew install jq`

### Using the Add Plugin Script

The easiest way to add a new plugin is using the provided script:

```bash
./add-plugin.sh
```

The script will prompt you for:
1. **Plugin name** - A unique identifier (e.g., `my-plugin`)
2. **Git repository URL** - The plugin's git repo (SSH or HTTPS)
3. **Description** - A brief description of what the plugin does
4. **Version** - The plugin version (defaults to `0.1.0`)

The script will then:
- Add the plugin as a git submodule under `./plugins/`
- Update the `marketplace.json` file
- Update this README's "Available Plugins" table automatically
- Optionally commit the changes

### Manual Addition

If you prefer to add a plugin manually:

1. **Add the submodule**:
   ```bash
   git submodule add <git-url> plugins/<plugin-name>
   ```

2. **Update marketplace.json**:
   Add an entry to the `plugins` array in `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "description": "<description>",
     "version": "<version>"
   }
   ```

3. **Update README.md**:
   Add a row to the "Available Plugins" table:
   ```markdown
   | [plugin-name](./plugins/plugin-name) | Description | [GitHub](https://github.com/...) | 0.1.0 |
   ```

4. **Commit the changes**:
   ```bash
   git add .gitmodules .claude-plugin/marketplace.json README.md plugins/<plugin-name>
   git commit -m "Add plugin: <plugin-name>"
   ```

## Cloning This Repository

When cloning this repository, use `--recurse-submodules` to fetch all plugins:

```bash
git clone --recurse-submodules <repo-url>
```

If you've already cloned without submodules:

```bash
git submodule update --init --recursive
```

## Updating Plugins

### Using the Update Script

The easiest way to update a plugin is using the provided script:

```bash
./add-plugin.sh --update <plugin-name>
```

This will:
- Pull the latest changes from the plugin's remote repository
- Show recent commits so you can see what changed
- Prompt for the new version number
- Update the version in `marketplace.json` and this README automatically

After running, commit the changes manually:
```bash
git add plugins/<plugin-name> .claude-plugin/marketplace.json README.md
git commit -m "Update plugin: <plugin-name> to <version>"
```

### Manual Update

To update all plugins to their latest commits:

```bash
git submodule update --remote --merge
```

To update a specific plugin manually:

```bash
cd plugins/<plugin-name>
git pull origin main
cd ../..
git add plugins/<plugin-name>
git commit -m "Update plugin: <plugin-name>"
```

Note: Manual updates don't automatically update the version in `marketplace.json` or `README.md`.

## Repository Structure

```
.
├── .claude-plugin/
│   └── marketplace.json    # Plugin registry
├── plugins/                # Plugin submodules
├── add-plugin.sh           # Script to add/update plugins
├── LICENSE
└── README.md
```

## License

MIT License - see [LICENSE](./LICENSE) for details.
