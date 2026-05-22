-- mail_actions.applescript
-- Esegue azioni su un messaggio (per message id)
-- Argomenti: action (mark_read|mark_unread|flag|archive|delete|move), message_id, [mailbox_name]

on run argv
	if (count of argv) < 2 then return "ERROR: need action and message_id"
	set theAction to item 1 of argv as string
	set theMsgId to item 2 of argv as string
	set targetMailbox to ""
	if (count of argv) >= 3 then set targetMailbox to item 3 of argv as string

	tell application "Mail"
		set foundMsg to missing value
		repeat with anAccount in (every account)
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
					set candidates to (messages of theInbox whose message id is theMsgId)
					if (count of candidates) > 0 then
						set foundMsg to item 1 of candidates
						exit repeat
					end if
				end try
			end if
		end repeat

		if foundMsg is missing value then return "ERROR: message not found"

		if theAction is "mark_read" then
			set read status of foundMsg to true
			return "OK: marked read"
		else if theAction is "mark_unread" then
			set read status of foundMsg to false
			return "OK: marked unread"
		else if theAction is "flag" then
			set flagged status of foundMsg to true
			return "OK: flagged"
		else if theAction is "delete" then
			delete foundMsg
			return "OK: deleted"
		else if theAction is "archive" then
			set acct to account of (mailbox of foundMsg)
			set archiveBox to missing value
			-- Nomi candidati per la mailbox di archivio, in ordine di preferenza.
			-- Gli account Gmail non hanno "Archive": l'archiviazione si fa
			-- spostando in "All Mail" / "Tutti i messaggi" (rimuove l'etichetta Inbox).
			set candidateNames to {"Archive", "Archivio", "archivi", "All Mail", "Tutti i messaggi", "Tous les messages"}
			repeat with candName in candidateNames
				try
					set archiveBox to (first mailbox of acct whose name is (candName as string))
					exit repeat
				end try
			end repeat
			if archiveBox is missing value then
				try
					set archiveBox to (first mailbox of acct whose name contains "Archiv")
				end try
			end if
			if archiveBox is missing value then return "ERROR: no Archive mailbox"
			move foundMsg to archiveBox
			return "OK: archived to " & (name of archiveBox)
		else if theAction is "move" then
			if targetMailbox is "" then return "ERROR: need target mailbox"
			try
				set destBox to first mailbox of (account of (mailbox of foundMsg)) whose name is targetMailbox
				move foundMsg to destBox
				return "OK: moved to " & targetMailbox
			on error
				return "ERROR: target mailbox not found"
			end try
		else
			return "ERROR: unknown action " & theAction
		end if
	end tell
end run
