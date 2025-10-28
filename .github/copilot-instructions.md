# GitHub Copilot Instructions for Home Assistant Add-on Development

## Repository Overview
This is a Home Assistant add-on repository containing custom add-ons for Home Assistant installations. Follow these guidelines when assisting with code generation, modifications, or suggestions.

## Home Assistant Add-on Development Guidelines

### Repository Structure
- Root must contain `repository.yaml` (NOT `repository.json`)
- Each add-on lives in its own directory
- Standard add-on structure:
  ```
  addon_name/
  ├── config.json          # Required: Add-on configuration
  ├── Dockerfile           # Required: Container build instructions
  ├── run.sh              # Required: Entry script (executable)
  ├── README.md           # Required: Add-on documentation
  ├── CHANGELOG.md        # Recommended: Version history
  ├── DOCS.md             # Optional: Detailed documentation
  ├── icon.png            # Optional: Add-on icon
  ├── logo.png            # Optional: Add-on logo
  └── translations/       # Optional: UI translations
      └── en.yaml
  ```

### Dockerfile Best Practices
**ALWAYS follow these rules:**

1. **Base Image**: Use Home Assistant base images
   ```dockerfile
   ARG BUILD_FROM
   FROM $BUILD_FROM
   ```

2. **Package Management**: Use Alpine's `apk` package manager, NOT `pip` for system packages
   ```dockerfile
   # GOOD
   RUN apk add --no-cache py3-yaml python3 curl bash
   
   # BAD - causes PEP 668 errors
   RUN pip3 install pyyaml
   ```

3. **Consolidate RUN Commands**: Optimize Docker layers
   ```dockerfile
   RUN \
       apk add --no-cache \
           curl \
           bash \
           jq \
       && curl https://example.com/install.sh | bash
   ```

4. **Standard Structure**:
   ```dockerfile
   ARG BUILD_FROM
   FROM $BUILD_FROM
   
   # Install packages
   RUN apk add --no-cache package1 package2
   
   # Copy and setup script
   COPY run.sh /
   RUN chmod a+x /run.sh
   
   CMD [ "/run.sh" ]
   ```

### Configuration Files (config.json)
**Required fields:**
- `name`: Human-readable add-on name
- `version`: Semantic version (e.g., "1.0.0")
- `slug`: URL-friendly identifier
- `description`: Brief description
- `arch`: Supported architectures `["amd64", "armv7", "aarch64"]`

**Key configuration options:**
```json
{
  "name": "Add-on Name",
  "version": "1.0.0",
  "slug": "addon-slug",
  "description": "Brief description",
  "url": "https://github.com/username/repository-name",
  "arch": ["amd64", "armv7", "aarch64"],
  "startup": "application",
  "boot": "auto",
  "init": false,
  "map": ["config:ro", "backup:ro"],
  "options": {
    "option_name": "default_value"
  },
  "schema": {
    "option_name": "str"
  }
}
```

### Run Scripts (run.sh)
**Best practices:**

1. **Shebang**: Use Home Assistant bashio format
   ```bash
   #!/usr/bin/with-contenv bashio
   ```

2. **Configuration Parsing**: Use bashio or jq to read `/data/options.json`
   ```bash
   # Using jq
   CONFIG_FILE=/data/options.json
   OPTION_VALUE=$(jq --raw-output '.option_name' "$CONFIG_FILE")
   
   # Using bashio (preferred)
   OPTION_VALUE=$(bashio::config 'option_name')
   ```

3. **Error Handling**: Use `set -e` for script safety
   ```bash
   #!/usr/bin/with-contenv bashio
   set -e
   ```

4. **Keep Running**: For daemon add-ons, prevent exit
   ```bash
   # Keep addon running
   tail -f /dev/null
   ```

### Repository Configuration (repository.yaml)
```yaml
#
# https://developers.home-assistant.io/docs/add-ons/repository#repository-configuration
name: Repository Name
url: https://github.com/username/repository-name
maintainer: Name <email@example.com>
```

### Security & Permissions
**Use minimal required permissions:**
- `privileged`: Only when necessary (e.g., `["SYS_ADMIN"]` for FUSE)
- `devices`: Map specific devices (e.g., `["/dev/fuse"]`)
- `map`: Use read-only when possible (e.g., `["config:ro", "backup:ro"]`)

### Common Packages for Different Use Cases
**File operations**: `curl`, `jq`, `bash`
**Python apps**: `python3`, `py3-pip` (avoid direct pip usage)
**Network tools**: `net-tools`, `iproute2`
**FUSE mounting**: `fuse`
**SSL/TLS**: `ca-certificates`

### Schema Validation Types
```json
{
  "schema": {
    "string_option": "str",
    "optional_string": "str?",
    "limited_string": "str(5,50)",
    "integer_option": "int",
    "float_option": "float",
    "boolean_option": "bool",
    "email_option": "email",
    "url_option": "url",
    "password_option": "password",
    "port_option": "port",
    "list_option": "list(val1|val2|val3)",
    "regex_option": "match(^\\w+$)"
  }
}
```

### Common Mistakes to Avoid
1. ❌ Using `pip install` directly (causes PEP 668 errors)
2. ❌ Using `repository.json` instead of `repository.yaml`
3. ❌ Forgetting to make `run.sh` executable
4. ❌ Not consolidating RUN commands in Dockerfile
5. ❌ Using excessive privileges
6. ❌ Not handling configuration errors gracefully
7. ❌ Hardcoding paths instead of using `/data/options.json`

### Documentation Standards
**README.md should include:**
- Clear description of add-on functionality
- Installation instructions
- Configuration options explanation
- Usage examples
- Troubleshooting section

**CHANGELOG.md format:**
```markdown
# Changelog

## [1.0.1] - 2025-01-15
### Fixed
- Bug fix description

## [1.0.0] - 2025-01-01
### Added
- Initial release
```

### Development Workflow
1. Create add-on directory with required files
2. Test Dockerfile builds locally
3. Validate config.json against schema
4. Test add-on installation and functionality
5. **Update version number in config.json for ANY file changes**
6. Update CHANGELOG.md with version changes
7. Commit and push changes
8. Test in Home Assistant environment

## Version Management
**CRITICAL**: Always update the version number in `config.json` when making ANY changes to add-on files:
- Dockerfile changes → Increment version
- run.sh changes → Increment version
- config.json changes → Increment version
- Documentation changes → Increment version (optional but recommended)

Follow semantic versioning:
- `1.0.0` → `1.0.1` for bug fixes
- `1.0.0` → `1.1.0` for new features
- `1.0.0` → `2.0.0` for breaking changes

Update CHANGELOG.md to document what changed in each version.

## When Suggesting Code
- Always use Home Assistant conventions
- Prefer bashio functions over manual parsing
- Include error handling and logging
- Use appropriate schema validation
- Follow security best practices
- Include helpful comments explaining HA-specific concepts