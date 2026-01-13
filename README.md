# Claude Code Plugins - MadeByTokens Marketplace

A curated marketplace of Claude Code plugins maintained by MadeByTokens. Each plugin's source code is copied directly into this repository for easy distribution.

## Installation

To install this plugin marketplace in Claude Code:

1. **Add this marketplace to Claude Code**:

   In Claude Code, run the `/plugin` command and select "Add marketplace". Then enter:

   ```
   https://github.com/MadeByTokens/claude-code-plugins-madebytokens.git
   ```

2. **Install plugins** from the marketplace by running `/plugin` again and browsing the available plugins.

## Available Plugins

| Plugin | Description | Repository | Version |
|--------|-------------|------------|---------|
| [resume-helper](./plugins/resume-helper) | Adversarial multi-agent resume development - creates compelling AND honest resumes | [GitHub](https://github.com/MadeByTokens/resume-helper) | 0.7.3 |
| [bon-cop-bad-cop](./plugins/bon-cop-bad-cop) | Three-agent adversarial TDD loop: Test Writer (bad cop), Code Writer (suspect), and Reviewer (good cop) work together while keeping each other honest | [GitHub](https://github.com/MadeByTokens/bon-cop-bad-cop) | 0.6.0 |

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

The script will:
1. Prompt for **plugin name** and **git repository URL**
2. Clone the repository
3. **Auto-extract** description and version from `.claude-plugin/plugin.json`
   - Only prompts for these if not found in the plugin's metadata
4. Show a summary and ask for confirmation
5. Copy plugin files to `./plugins/`
6. Update `marketplace.json` and this README automatically
7. Optionally commit the changes

### Manual Addition

If you prefer to add a plugin manually:

1. **Clone and copy the plugin**:
   ```bash
   git clone --depth 1 <git-url> /tmp/plugin-temp
   rm -rf /tmp/plugin-temp/.git
   mv /tmp/plugin-temp plugins/<plugin-name>
   ```

2. **Update marketplace.json**:
   Add an entry to the `plugins` array in `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "repository": "https://github.com/...",
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
   git add .claude-plugin/marketplace.json README.md plugins/<plugin-name>
   git commit -m "Add plugin: <plugin-name>"
   ```

## Updating Plugins

### Using the Update Script

The easiest way to update a plugin is using the provided script:

```bash
./add-plugin.sh --update <plugin-name>
```

This will:
- Fetch the latest version from the plugin's remote repository
- **Auto-extract** the version from `.claude-plugin/plugin.json` and use it as the default
  - Falls back to the current marketplace version if not found
- Show recent commits so you can see what changed
- Prompt for confirmation (press Enter to accept the auto-detected version)
- Replace the local plugin files with the latest version
- Update the version in `marketplace.json` and this README automatically

After running, commit the changes:
```bash
git add plugins/<plugin-name> .claude-plugin/marketplace.json README.md
git commit -m "Update plugin: <plugin-name> to <version>"
```

### Manual Update

To update a plugin manually:

1. **Fetch and replace the plugin files**:
   ```bash
   rm -rf plugins/<plugin-name>
   git clone --depth 1 <git-url> /tmp/plugin-temp
   rm -rf /tmp/plugin-temp/.git
   mv /tmp/plugin-temp plugins/<plugin-name>
   ```

2. **Update the version** in `marketplace.json` and `README.md` if needed.

3. **Commit the changes**:
   ```bash
   git add plugins/<plugin-name>
   git commit -m "Update plugin: <plugin-name>"
   ```

## Repository Structure

```
.
├── .claude-plugin/
│   └── marketplace.json    # Plugin registry
├── plugins/                # Plugin directories
├── add-plugin.sh           # Script to add/update plugins
├── LICENSE
└── README.md
```

## License

MIT License - see [LICENSE](./LICENSE) for details.
