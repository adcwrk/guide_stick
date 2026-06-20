#!/usr/bin/env bash

set -u

PORT="${1:-}"
PATH_SUFFIX="${2:-}"
HOSTNAME_VALUE="$(hostname 2>/dev/null || printf 'localhost')"

get_lan_ip() {
  if command -v ip >/dev/null 2>&1; then
    ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i=1;i<=NF;i++) if ($i=="src") {print $(i+1); exit}}'
  elif command -v ifconfig >/dev/null 2>&1; then
    ifconfig 2>/dev/null | awk '/inet / && $2 != "127.0.0.1" {print $2; exit}'
  else
    return 1
  fi
}

LAN_IP="$(get_lan_ip || true)"

if [ -n "$PORT" ]; then
  printf 'Local:    http://localhost:%s%s\n' "$PORT" "$PATH_SUFFIX"
  [ -n "$LAN_IP" ] && printf 'Remote:   http://%s:%s%s\n' "$LAN_IP" "$PORT" "$PATH_SUFFIX" || printf 'Remote:   unavailable\n'
  [ -n "$HOSTNAME_VALUE" ] && printf 'Hostname: http://%s.local:%s%s\n' "$HOSTNAME_VALUE" "$PORT" "$PATH_SUFFIX"
else
  [ -n "$LAN_IP" ] && printf '%s\n' "$LAN_IP"
fi
