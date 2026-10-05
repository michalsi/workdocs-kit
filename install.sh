#!/usr/bin/env bash
# Set up the workdocs content root, machine config, the `wd` command, and the agent skill. Idempotent.
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${WORKDOCS_CONFIG:-$HOME/.config/workdocs/config}"
ROOT="${WORKDOCS_ROOT:-$HOME/workdocs}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"

if [[ ! -f "$CONFIG" ]]; then
  mkdir -p "$(dirname "$CONFIG")"
  cat > "$CONFIG" <<EOF
# workdocs machine config. KEY=value; \$HOME and ~ are expanded. Environment variables override.
WORKDOCS_ROOT=$ROOT
WORKDOCS_DATA=$ROOT/data
JIRA_KEY_REGEX=[A-Z][A-Z0-9]+-[0-9]+
# Branches never recorded in a project's branches: list
TRUNK_BRANCHES=main master stage dev develop prod release HEAD
# Colon-separated checkouts that \`wd audit\` scans for stray notes
AUDIT_REPOS=
# Space-separated ticket project prefixes (e.g. PROJ OPS); empty accepts any KEY-123 shape
JIRA_PROJECTS=
# Stop hook: tool calls in a workdocs project without a LOG/HANDOFF write before the agent is reminded
NUDGE_AFTER=20
EOF
  echo "Wrote $CONFIG (edit AUDIT_REPOS and JIRA_PROJECTS)"
fi

mkdir -p "$ROOT"/{projects,reviews,notes,archive,data}
if [[ ! -f "$ROOT/.gitignore" ]]; then
  cat > "$ROOT/.gitignore" <<'EOF'
data/
.obsidian/workspace*.json
.obsidian/cache
.DS_Store
.venv/
__pycache__/
*.pyc
EOF
fi
if [[ ! -f "$ROOT/README.md" ]]; then
  sed "s|{{kit}}|$KIT|g" "$KIT/templates/root-README.md" > "$ROOT/README.md"
fi
if [[ ! -d "$ROOT/.git" ]]; then
  git -C "$ROOT" init -q
  echo "Initialised git in $ROOT"
fi

mkdir -p "$BIN_DIR"
ln -sfn "$KIT/bin/wd" "$BIN_DIR/wd"
chmod +x "$KIT/bin/wd"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "Add $BIN_DIR to PATH" ;;
esac

# Link the skill into each agent that is installed. Never replace a real directory.
for agent_home in "$HOME/.claude" "${CODEX_HOME:-$HOME/.codex}" "$HOME/.cursor"; do
  [[ -d "$agent_home" ]] || continue
  skills="$agent_home/skills"
  [[ "$agent_home" == "$HOME/.cursor" ]] && skills="$agent_home/skills-cursor"
  mkdir -p "$skills"
  link="$skills/workdocs"
  if [[ -e "$link" && ! -L "$link" ]]; then
    echo "Skip $link (exists and is not a symlink)" >&2
    continue
  fi
  ln -sfn "$KIT/skills/workdocs" "$link"
  echo "Linked skill -> $link"
done

"$BIN_DIR/wd" index >/dev/null
echo "workdocs ready at $ROOT"
cat <<EOF

Remaining manual wiring (see $KIT/README.md):
  All agents   add the rule in $KIT/agents/work-docs-rule.md to your global agent instructions
  Claude Code  ~/.claude/settings.json: hooks SessionStart / SessionEnd / Stop -> "$BIN_DIR/wd hook <event>";
               permissions.additionalDirectories += "$ROOT"
  Codex        ~/.codex/config.toml: [sandbox_workspace_write] writable_roots = ["$ROOT"]
  Cursor       Settings -> Rules -> User Rules: paste the rule
EOF
