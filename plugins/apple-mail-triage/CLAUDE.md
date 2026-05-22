# Apple Mail Triage Plugin

Plugin per leggere, categorizzare e processare email da Apple Mail su macOS.

## Setup

1. Mail.app deve essere configurato con almeno un account
2. Al primo utilizzo, macOS chiederà di autorizzare l'accesso a Mail.app via AppleScript
   (Impostazioni di Sistema > Privacy e Sicurezza > Automazione)

## Account su questo Mac

Apple Mail include già 5 account configurati. L'account `elha@bitcoinpeople.it` è su **Zoho EU** (dominio bitcoinpeople.it ha MX su zoho.eu) ed è letto via IMAP automaticamente da Apple Mail — nessuna config extra richiesta.

Per account Zoho aggiuntivi NON in Apple Mail (es. account zoho.com personali), configura `~/.zoho_mail_creds`:
```json
{"email":"...","app_password":"...","server":"imap.zoho.eu"}
```
Lo script `scripts/read_zoho_imap.py` li leggerà automaticamente se il file esiste.

## Comandi disponibili

- `/mail-triage` - Legge inbox e propone azioni
  - Argomenti opzionali: `limit` (default 20), `unread_only` (default true), `account` (default all)

## Come funziona

1. Esegue lo script AppleScript `scripts/read_mail.applescript` via `osascript`
2. Lo script restituisce JSON con: sender, subject, date, snippet, account, mailbox, read_status
3. Claude classifica ogni email per categoria e priorità
4. Per ogni email propone un'azione concreta da intraprendere
5. Mostra un riassunto ordinato per priorità

## Sicurezza

- Solo lettura di default
- Azioni di scrittura (sposta/elimina/rispondi) richiedono conferma esplicita
- Nessuna chiamata di rete: tutto via AppleScript locale
- Le credenziali email sono gestite da Mail.app, mai esposte
