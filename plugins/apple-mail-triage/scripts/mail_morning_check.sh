#!/bin/bash
# mail_morning_check.sh
# Conta le email non lette in tutti gli account di Apple Mail e mostra una notifica macOS.
# Pensato per essere lanciato da un LaunchAgent ogni mattina.

set -u

LOG_FILE="$HOME/Library/Logs/mail-triage-morning.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

log "=== Morning check start ==="

# Conta unread per account via AppleScript (usa la proprietà nativa `unread count`)
COUNTS=$(osascript <<'APPLESCRIPT' 2>&1
tell application "Mail"
	set out to ""
	set totalUnread to 0
	repeat with anAccount in (every account)
		set accName to name of anAccount
		try
			set theInbox to mailbox "INBOX" of anAccount
		on error
			try
				set theInbox to first mailbox of anAccount whose name contains "Inbox"
			on error
				set theInbox to missing value
			end try
		end try
		if theInbox is not missing value then
			try
				set unreadCount to unread count of theInbox
				set totalUnread to totalUnread + unreadCount
				if unreadCount > 0 then
					set out to out & accName & ": " & unreadCount & linefeed
				end if
			end try
		end if
	end repeat
	return (totalUnread as string) & "|" & out
end tell
APPLESCRIPT
)

if [ $? -ne 0 ]; then
	log "ERROR running AppleScript: $COUNTS"
	osascript -e "display notification \"Errore lettura Mail. Vedi log.\" with title \"Mail Triage\" subtitle \"Errore\""
	exit 1
fi

TOTAL="${COUNTS%%|*}"
DETAILS="${COUNTS#*|}"
DETAILS="${DETAILS%$'\n'}"

log "Total unread: $TOTAL"
log "Details: $DETAILS"

if [ "$TOTAL" -eq 0 ]; then
	TITLE="📭 Inbox pulita"
	MESSAGE="Nessuna email non letta. Buongiorno!"
else
	TITLE="📬 $TOTAL email non lette"
	if [ -n "$DETAILS" ]; then
		# Multi-line details collapsed for notification subtitle
		MESSAGE="Apri Claude Code e fai /mail-triage"
		SUBTITLE=$(echo "$DETAILS" | tr '\n' ' ' | sed 's/  */ /g')
	else
		MESSAGE="Apri Claude Code e fai /mail-triage"
		SUBTITLE=""
	fi
fi

# Mostra notifica macOS
if [ -n "${SUBTITLE:-}" ]; then
	osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" subtitle \"$SUBTITLE\" sound name \"Glass\""
else
	osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" sound name \"Glass\""
fi

log "Notification sent."
log "=== Morning check end ==="
