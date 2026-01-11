#!/bin/bash

# add-plugin.sh - Automate adding plugins to the marketplace

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

MARKETPLACE_FILE=".claude-plugin/marketplace.json"
README_FILE="README.md"

# Print colored messages
print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_info() {
    echo -e "${BLUE}$1${NC}"
}

# Show help
show_help() {
    cat << EOF
Usage: ./add-plugin.sh [OPTIONS]

Automate adding or updating plugins in the MadeByTokens marketplace.

MODES:
  Add mode (default):
    1. Prompt you for plugin details (name, git URL, description, version)
    2. Validate the inputs
    3. Clone the plugin repository and copy files to ./plugins/
    4. Update the marketplace.json file
    5. Update the README.md plugins table
    6. Optionally commit the changes

  Update mode (--update):
    1. Fetch the latest version from the plugin's remote repository
    2. Prompt for the new version number
    3. Replace local plugin files with the latest version
    4. Update the version in marketplace.json
    5. Update the version in README.md

OPTIONS:
  -h, --help              Show this help message and exit
  -u, --update <name>     Update an existing plugin (fetch latest + update version)

REQUIREMENTS:
  - jq (for JSON manipulation)
  - git (for cloning repositories)
  - Must be run from the repository root

EXAMPLES:
  ./add-plugin.sh                      # Add a new plugin (interactive)
  ./add-plugin.sh --update my-plugin   # Update existing plugin
  ./add-plugin.sh --help               # Show this help

EOF
}

# Check dependencies
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install it first."
        echo "  On Ubuntu/Debian: sudo apt install jq"
        echo "  On macOS: brew install jq"
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        print_error "git is not installed. Please install it first."
        exit 1
    fi
}

# Check environment
check_environment() {
    if [[ ! -f "$MARKETPLACE_FILE" ]]; then
        print_error "marketplace.json not found at $MARKETPLACE_FILE"
        echo "Please run this script from the repository root."
        exit 1
    fi

    if [[ ! -d ".git" ]]; then
        print_error "Not a git repository."
        echo "Please run this script from the repository root."
        exit 1
    fi
}

# Validate plugin name
validate_plugin_name() {
    local name="$1"

    # Check if empty
    if [[ -z "$name" ]]; then
        print_error "Plugin name cannot be empty."
        return 1
    fi

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if [[ ! "$name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        print_error "Plugin name can only contain letters, numbers, hyphens, and underscores."
        return 1
    fi

    # Check if plugin already exists in marketplace.json
    if jq -e --arg name "$name" '.plugins[] | select(.name == $name)' "$MARKETPLACE_FILE" > /dev/null 2>&1; then
        print_error "Plugin '$name' already exists in marketplace.json"
        return 1
    fi

    # Check if directory already exists
    if [[ -d "plugins/$name" ]]; then
        print_error "Directory plugins/$name already exists."
        return 1
    fi

    return 0
}

# Validate git URL
validate_git_url() {
    local url="$1"

    if [[ -z "$url" ]]; then
        print_error "Git URL cannot be empty."
        return 1
    fi

    # Basic validation for git URLs (SSH or HTTPS)
    if [[ ! "$url" =~ ^(git@|https://) ]]; then
        print_error "Invalid git URL. Must start with 'git@' or 'https://'"
        return 1
    fi

    return 0
}

# Convert git URL to HTTPS URL for display
git_url_to_https() {
    local url="$1"

    # Convert SSH format: git@github.com:user/repo.git -> https://github.com/user/repo
    if [[ "$url" =~ ^git@([^:]+):(.+)\.git$ ]]; then
        echo "https://${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    elif [[ "$url" =~ ^git@([^:]+):(.+)$ ]]; then
        echo "https://${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    # Convert HTTPS with .git suffix: https://github.com/user/repo.git -> https://github.com/user/repo
    elif [[ "$url" =~ ^https://(.+)\.git$ ]]; then
        echo "https://${BASH_REMATCH[1]}"
    else
        # Return as-is if already clean HTTPS
        echo "$url"
    fi
}

# Update README.md with new plugin entry
update_readme() {
    local name="$1"
    local description="$2"
    local version="$3"
    local git_url="$4"

    if [[ ! -f "$README_FILE" ]]; then
        print_warning "README.md not found, skipping README update."
        return 0
    fi

    # Convert git URL to displayable HTTPS URL
    local display_url=$(git_url_to_https "$git_url")

    # Create the new table row
    local new_row="| [${name}](./plugins/${name}) | ${description} | [GitHub](${display_url}) | ${version} |"

    # Find the line number of the table header separator (|--------|...)
    local header_line=$(grep -n "^|--------|" "$README_FILE" | head -1 | cut -d: -f1)

    if [[ -z "$header_line" ]]; then
        print_warning "Could not find plugins table in README.md, skipping README update."
        return 0
    fi

    # Insert the new row after the header separator
    # We need to find where to insert (after header, maintaining alphabetical order or at end of table)
    local insert_line=$((header_line + 1))

    # Read the file, find the end of the table (first non-table line after header)
    local total_lines=$(wc -l < "$README_FILE")
    local table_end=$insert_line

    while [[ $table_end -le $total_lines ]]; do
        local line=$(sed -n "${table_end}p" "$README_FILE")
        if [[ ! "$line" =~ ^\| ]]; then
            break
        fi
        ((table_end++))
    done

    # Insert the new row at the end of the table (before the empty line)
    local temp_file=$(mktemp)
    {
        head -n $((table_end - 1)) "$README_FILE"
        echo "$new_row"
        tail -n +$table_end "$README_FILE"
    } > "$temp_file"

    mv "$temp_file" "$README_FILE"
    return 0
}

# Update version in marketplace.json for an existing plugin
update_marketplace_version() {
    local name="$1"
    local new_version="$2"

    local temp_file=$(mktemp)
    jq --arg name "$name" \
       --arg ver "$new_version" \
       '(.plugins[] | select(.name == $name)).version = $ver' \
       "$MARKETPLACE_FILE" > "$temp_file"

    if [[ $? -eq 0 ]]; then
        mv "$temp_file" "$MARKETPLACE_FILE"
        return 0
    else
        rm -f "$temp_file"
        return 1
    fi
}

# Update version in README.md for an existing plugin
update_readme_version() {
    local name="$1"
    local new_version="$2"

    if [[ ! -f "$README_FILE" ]]; then
        print_warning "README.md not found, skipping README update."
        return 0
    fi

    # Find the line containing this plugin and update the version
    # Table format: | [name](./plugins/name) | Description | [GitHub](url) | version |
    local temp_file=$(mktemp)

    # Use awk to find and update the version in the correct row
    awk -v name="$name" -v ver="$new_version" '
    {
        # Check if this line contains the plugin link
        if ($0 ~ "\\[" name "\\]\\(\\./plugins/" name "\\)") {
            # Replace the last column (version) before the final |
            # Match pattern: | version |$ and replace version
            gsub(/\| [0-9]+\.[0-9]+\.[0-9]+ \|$/, "| " ver " |")
        }
        print
    }
    ' "$README_FILE" > "$temp_file"

    mv "$temp_file" "$README_FILE"
    return 0
}

# Update an existing plugin (fetch latest + update versions)
update_plugin() {
    local plugin_name="$1"

    echo ""
    print_info "=== MadeByTokens Plugin Update ==="
    echo ""

    # Validate plugin exists in marketplace.json
    if ! jq -e --arg name "$plugin_name" '.plugins[] | select(.name == $name)' "$MARKETPLACE_FILE" > /dev/null 2>&1; then
        print_error "Plugin '$plugin_name' not found in marketplace.json"
        exit 1
    fi

    # Validate plugin directory exists
    if [[ ! -d "plugins/$plugin_name" ]]; then
        print_error "Plugin directory 'plugins/$plugin_name' does not exist."
        exit 1
    fi

    # Get current version and repository URL
    local current_version=$(jq -r --arg name "$plugin_name" '.plugins[] | select(.name == $name) | .version' "$MARKETPLACE_FILE")
    local git_url=$(jq -r --arg name "$plugin_name" '.plugins[] | select(.name == $name) | .repository' "$MARKETPLACE_FILE")

    if [[ -z "$git_url" || "$git_url" == "null" ]]; then
        print_error "No repository URL found for plugin '$plugin_name' in marketplace.json"
        echo "Please add a 'repository' field to the plugin entry."
        exit 1
    fi

    echo "Plugin: $plugin_name"
    echo "Current version: $current_version"
    echo "Repository: $git_url"
    echo ""

    # Create temp directory for cloning
    local temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Clone latest version
    print_info "Fetching latest version from remote..."
    if ! git clone --depth 1 "$git_url" "$temp_dir/plugin" 2>&1; then
        print_error "Failed to clone repository."
        exit 1
    fi
    print_success "Latest version fetched successfully."
    echo ""

    # Show recent commits
    print_info "Recent commits:"
    git -C "$temp_dir/plugin" log --oneline -5
    echo ""

    # Prompt for new version
    read -rp "New version [$current_version]: " NEW_VERSION
    if [[ -z "$NEW_VERSION" ]]; then
        NEW_VERSION="$current_version"
    fi

    # Confirm
    echo ""
    print_info "=== Summary ==="
    echo "Plugin:       $plugin_name"
    echo "Old version:  $current_version"
    echo "New version:  $NEW_VERSION"
    echo ""

    read -rp "Update plugin files and version? (y/n): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        print_warning "Update cancelled."
        exit 0
    fi

    # Remove old plugin directory and copy new files
    print_info "Updating plugin files..."
    rm -rf "plugins/$plugin_name"
    rm -rf "$temp_dir/plugin/.git"
    mv "$temp_dir/plugin" "plugins/$plugin_name"
    print_success "Plugin files updated successfully."

    # Update marketplace.json
    print_info "Updating marketplace.json..."
    if update_marketplace_version "$plugin_name" "$NEW_VERSION"; then
        print_success "marketplace.json updated successfully."
    else
        print_error "Failed to update marketplace.json"
        exit 1
    fi

    # Update README.md
    print_info "Updating README.md..."
    if update_readme_version "$plugin_name" "$NEW_VERSION"; then
        print_success "README.md updated successfully."
    fi

    echo ""
    print_success "=== Done! ==="
    echo "Plugin '$plugin_name' has been updated to version $NEW_VERSION."
    echo ""
    echo "Changes not committed. To commit manually:"
    echo "  git add plugins/$plugin_name $MARKETPLACE_FILE $README_FILE"
    echo "  git commit -m \"Update plugin: $plugin_name to $NEW_VERSION\""
    echo ""
}

# Prompt for input with validation
prompt_required() {
    local prompt="$1"
    local var_name="$2"
    local value=""

    while [[ -z "$value" ]]; do
        read -rp "$prompt: " value
        if [[ -z "$value" ]]; then
            print_warning "This field is required."
        fi
    done

    echo "$value"
}

# Prompt for optional input with default
prompt_optional() {
    local prompt="$1"
    local default="$2"
    local value=""

    read -rp "$prompt [$default]: " value

    if [[ -z "$value" ]]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# Main function for adding a new plugin
add_plugin() {
    echo ""
    print_info "=== MadeByTokens Plugin Manager ==="
    echo ""

    # Collect plugin information
    echo "Please provide the following information for the new plugin:"
    echo ""

    # Plugin name
    while true; do
        read -rp "Plugin name (e.g., my-awesome-plugin): " PLUGIN_NAME
        if validate_plugin_name "$PLUGIN_NAME"; then
            break
        fi
    done

    # Git URL
    while true; do
        read -rp "Git repository URL: " GIT_URL
        if validate_git_url "$GIT_URL"; then
            break
        fi
    done

    # Description
    DESCRIPTION=""
    while [[ -z "$DESCRIPTION" ]]; do
        read -rp "Description: " DESCRIPTION
        if [[ -z "$DESCRIPTION" ]]; then
            print_warning "Description is required."
        fi
    done

    # Version (optional with default)
    VERSION=$(prompt_optional "Version" "0.1.0")

    # Show summary and confirm
    echo ""
    print_info "=== Summary ==="
    echo "Plugin name:  $PLUGIN_NAME"
    echo "Git URL:      $GIT_URL"
    echo "Description:  $DESCRIPTION"
    echo "Version:      $VERSION"
    echo "Target path:  ./plugins/$PLUGIN_NAME"
    echo ""

    read -rp "Proceed with these settings? (y/n): " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        print_warning "Aborted by user."
        exit 0
    fi

    echo ""

    # Create temp directory for cloning
    local temp_dir=$(mktemp -d)
    trap "rm -rf '$temp_dir'" EXIT

    # Clone the repository
    print_info "Cloning repository..."
    if ! git clone --depth 1 "$GIT_URL" "$temp_dir/plugin" 2>&1; then
        print_error "Failed to clone repository."
        exit 1
    fi

    # Remove .git directory and move to plugins
    rm -rf "$temp_dir/plugin/.git"

    # Ensure plugins directory exists
    mkdir -p plugins

    mv "$temp_dir/plugin" "plugins/$PLUGIN_NAME"
    print_success "Plugin files copied successfully."

    # Update marketplace.json
    print_info "Updating marketplace.json..."

    # Convert git URL to HTTPS for storage
    local https_url=$(git_url_to_https "$GIT_URL")

    # Create new plugin entry and add to plugins array
    TEMP_FILE=$(mktemp)
    jq --arg name "$PLUGIN_NAME" \
       --arg source "./plugins/$PLUGIN_NAME" \
       --arg repo "$https_url" \
       --arg desc "$DESCRIPTION" \
       --arg ver "$VERSION" \
       '.plugins += [{"name": $name, "source": $source, "repository": $repo, "description": $desc, "version": $ver}]' \
       "$MARKETPLACE_FILE" > "$TEMP_FILE"

    if [[ $? -eq 0 ]]; then
        mv "$TEMP_FILE" "$MARKETPLACE_FILE"
        print_success "marketplace.json updated successfully."
    else
        rm -f "$TEMP_FILE"
        print_error "Failed to update marketplace.json"
        exit 1
    fi

    # Update README.md
    print_info "Updating README.md..."
    if update_readme "$PLUGIN_NAME" "$DESCRIPTION" "$VERSION" "$GIT_URL"; then
        print_success "README.md updated successfully."
    fi

    echo ""

    # Ask about committing
    read -rp "Commit these changes? (y/n): " COMMIT_CONFIRM
    if [[ "$COMMIT_CONFIRM" == "y" || "$COMMIT_CONFIRM" == "Y" ]]; then
        print_info "Committing changes..."
        git add "$MARKETPLACE_FILE" "$README_FILE" "plugins/$PLUGIN_NAME"
        git commit -m "Add plugin: $PLUGIN_NAME"
        print_success "Changes committed."
    else
        print_warning "Changes not committed. Remember to commit manually:"
        echo "  git add $MARKETPLACE_FILE $README_FILE plugins/$PLUGIN_NAME"
        echo "  git commit -m \"Add plugin: $PLUGIN_NAME\""
    fi

    echo ""
    print_success "=== Done! ==="
    echo "Plugin '$PLUGIN_NAME' has been added to the marketplace."
    echo ""
    echo "Next steps:"
    echo "  - Review the changes with 'git status' and 'git diff --staged'"
    echo "  - Push to remote when ready: 'git push'"
    echo ""
}

# Main entry point - parse arguments and route to appropriate function
main() {
    # Parse arguments
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--update)
            if [[ -z "$2" ]]; then
                print_error "Plugin name required for --update"
                echo "Usage: ./add-plugin.sh --update <plugin-name>"
                exit 1
            fi
            check_dependencies
            check_environment
            update_plugin "$2"
            ;;
        "")
            # No arguments - run add plugin flow
            check_dependencies
            check_environment
            add_plugin
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
