-- read_mail.applescript
-- Legge messaggi da Apple Mail e ritorna JSON
-- Argomenti: limit (numero), unread_only ("true"/"false"), account (nome account o "all")
--
-- Accede ai messaggi PER INDICE (i piu' recenti per primi), non con un filtro
-- "whose read status is false": su inbox grandi (migliaia di messaggi) il filtro
-- va in timeout AppleEvent (-1712). L'accesso per indice e' O(1) per messaggio.

on run argv
	set msgLimit to 20
	set unreadOnly to true
	set accountFilter to "all"

	if (count of argv) ≥ 1 then set msgLimit to (item 1 of argv) as integer
	if (count of argv) ≥ 2 then set unreadOnly to ((item 2 of argv) as string) is "true"
	if (count of argv) ≥ 3 then set accountFilter to (item 3 of argv) as string

	-- Quanti messaggi recenti esaminare al massimo per account (cap di sicurezza
	-- per non scansionare all'infinito un'inbox quasi tutta letta).
	set scanCap to 400

	set jsonOutput to "["
	set firstItem to true
	set countCollected to 0

	with timeout of 600 seconds
		tell application "Mail"
			set theAccounts to every account
			repeat with anAccount in theAccounts
				if countCollected ≥ msgLimit then exit repeat
				set accName to name of anAccount
				if accountFilter is "all" or accountFilter is accName then
					try
						set theInbox to mailbox "INBOX" of anAccount
					on error
						try
							set theInbox to first mailbox of anAccount whose name contains "Inbox"
						on error
							try
								set theInbox to first mailbox of anAccount whose name contains "Posta in arrivo"
							on error
								set theInbox to missing value
							end try
						end try
					end try

					if theInbox is not missing value then
						try
							set totalMsgs to count of messages of theInbox
							set examineMax to totalMsgs
							if examineMax > scanCap then set examineMax to scanCap

							repeat with i from 1 to examineMax
								if countCollected ≥ msgLimit then exit repeat
								try
									set theMsg to message i of theInbox
									set msgRead to read status of theMsg

									if (not unreadOnly) or (not msgRead) then
										set msgSender to sender of theMsg
										set msgSubject to subject of theMsg
										set msgDate to (date received of theMsg) as string
										set msgId to message id of theMsg
										try
											set msgSnippet to text 1 thru 300 of (content of theMsg as string)
										on error
											try
												set msgSnippet to (content of theMsg as string)
											on error
												set msgSnippet to ""
											end try
										end try

										set msgSender to my jsonEscape(msgSender)
										set msgSubject to my jsonEscape(msgSubject)
										set msgSnippet to my jsonEscape(msgSnippet)
										set msgId to my jsonEscape(msgId)
										set accNameEsc to my jsonEscape(accName)

										if not firstItem then set jsonOutput to jsonOutput & ","
										set firstItem to false

										set jsonOutput to jsonOutput & "{"
										set jsonOutput to jsonOutput & "\"id\":\"" & msgId & "\","
										set jsonOutput to jsonOutput & "\"account\":\"" & accNameEsc & "\","
										set jsonOutput to jsonOutput & "\"sender\":\"" & msgSender & "\","
										set jsonOutput to jsonOutput & "\"subject\":\"" & msgSubject & "\","
										set jsonOutput to jsonOutput & "\"date\":\"" & msgDate & "\","
										set jsonOutput to jsonOutput & "\"read\":" & (msgRead as string) & ","
										set jsonOutput to jsonOutput & "\"snippet\":\"" & msgSnippet & "\""
										set jsonOutput to jsonOutput & "}"

										set countCollected to countCollected + 1
									end if
								on error errMsg
									-- skip messaggio problematico
								end try
							end repeat
						on error errMsg
							-- skip account problematico
						end try
					end if
				end if
			end repeat
		end tell
	end timeout

	set jsonOutput to jsonOutput & "]"
	return jsonOutput
end run

on jsonEscape(s)
	set s to s as string
	set s to my replaceText(s, "\\", "\\\\")
	set s to my replaceText(s, "\"", "\\\"")
	set s to my replaceText(s, return, "\\n")
	set s to my replaceText(s, linefeed, "\\n")
	set s to my replaceText(s, tab, "\\t")
	return s
end jsonEscape

on replaceText(theText, oldStr, newStr)
	set AppleScript's text item delimiters to oldStr
	set theItems to text items of theText
	set AppleScript's text item delimiters to newStr
	set theText to theItems as string
	set AppleScript's text item delimiters to ""
	return theText
end replaceText
