---
name: mail-triage
description: Legge le email da Apple Mail, le ordina per priorità e categoria, e propone per ognuna un'azione concreta da intraprendere. Funziona solo su macOS con Mail.app configurato.
arguments:
  - name: limit
    description: Numero massimo di email da leggere (default 20)
    required: false
  - name: unread_only
    description: Se "true" legge solo le non lette (default true), "false" legge tutte le recenti
    required: false
  - name: account
    description: Nome dell'account specifico (es. "iCloud", "Gmail") o "all" per tutti (default all)
    required: false
---

# Mail Triage Command

Esegui il triage dell'inbox di Apple Mail: leggi le email, categorizzale e proponi azioni.

## Step 1: Legge le email

Esegui lo script AppleScript per ottenere le email da TUTTI gli account in Apple Mail:

```bash
osascript "$CLAUDE_PLUGIN_ROOT/scripts/read_mail.applescript" <limit> <unread_only> <account>
```

Default: `osascript .../read_mail.applescript 20 true all`

Apple Mail copre già gli account: `btcpsn@gmail.com`, `btcpsrl@gmail.com`, `ndhadji@gmail.com`, `elha@bitcoinpeople.it` (**Zoho EU**), `dimex.sn@gmail.com`.

**Opzionale**: se esiste `~/.zoho_mail_creds`, leggi anche da account Zoho aggiuntivi non in Apple Mail:

```bash
if [ -f ~/.zoho_mail_creds ]; then
  python3 "$CLAUDE_PLUGIN_ROOT/scripts/read_zoho_imap.py" --limit <limit> --unread-only <unread_only>
fi
```

Entrambi gli script ritornano un array JSON con gli stessi campi: `id`, `account`, `sender`, `subject`, `date`, `read`, `snippet`. Concatenali in un'unica lista prima della categorizzazione.

Se la prima esecuzione fallisce con permission error, dire all'utente:
> Autorizza l'accesso a Mail.app: Impostazioni di Sistema → Privacy e Sicurezza → Automazione → trova "Terminal" o "Claude" e abilita "Mail".

## Step 2: Categorizza

Per ogni email, assegna **una** categoria:

| Categoria | Indicatori |
|-----------|-----------|
| **🔴 URGENT** | Scadenze, fatture, clienti, "urgente", "scadenza", richieste dirette di risposta |
| **💼 WORK** | Mittente noto del lavoro (btcp-srl, Odoo, fornitori, partner) |
| **👤 PERSONAL** | Email da persone reali, non automatiche |
| **📰 NEWSLETTER** | Digest, newsletter, "unsubscribe" nel piè di pagina |
| **🎁 PROMO** | Offerte, sconti, marketing |
| **🤖 NOTIFICATION** | Notifiche da sistemi (GitHub, banche, social, conferme) |
| **🗑️ SPAM** | Mittenti sospetti, contenuto generico, troppo bello per essere vero |

## Step 3: Priorità

Assegna una priorità da 1 (massima) a 5 (minima):
- **P1**: URGENT con scadenza < 24h
- **P2**: WORK che richiede risposta
- **P3**: PERSONAL da rispondere
- **P4**: NOTIFICATION da leggere
- **P5**: NEWSLETTER/PROMO/SPAM

## Step 4: Azione suggerita

Per ogni email proponi **una** azione concreta:

- **✍️ REPLY** — Da rispondere. Includi 1 frase su cosa rispondere.
- **📁 ARCHIVE** — Da archiviare (info ricevuta, nessuna azione)
- **🗑️ DELETE** — Da eliminare (spam, promo già scaduti)
- **🚩 FLAG** — Da segnare per follow-up più avanti
- **➡️ DELEGATE** — Da inoltrare (specifica a chi se evidente)
- **📅 SCHEDULE** — Da convertire in task/appuntamento (specifica quando)

## Step 5: Output

Presenta un riepilogo strutturato in italiano, ordinato per priorità:

```
📬 INBOX TRIAGE — N email analizzate

🔴 P1 URGENT (X)
─────────────────────────────
[1] mittente@ex.com — Oggetto della mail
    📅 2026-05-19 09:23
    💡 ✍️ REPLY: rispondi confermando ricevimento entro oggi
    ID: <message-id>

💼 P2 WORK (X)
─────────────────────────────
...

[restanti categorie...]

📊 RIEPILOGO
- Da rispondere: X
- Da archiviare: X
- Da eliminare: X
- Da segnare: X
- Da delegare: X
- Da programmare: X

🎯 PROSSIME AZIONI CONSIGLIATE:
1. Rispondi a [mittente] su [topic]
2. Archivia in blocco le X notifiche
3. ...
```

## Step 6: Azioni opzionali

Se l'utente conferma con "esegui", "fai", "procedi", usa lo script di azioni:

```bash
osascript "$CLAUDE_PLUGIN_ROOT/scripts/mail_actions.applescript" <action> <message_id> [mailbox]
```

Azioni disponibili: `mark_read`, `mark_unread`, `flag`, `archive`, `delete`, `move`.

**⚠️ SEMPRE CHIEDERE CONFERMA PRIMA DI:**
- `delete` (elimina definitivamente)
- `move` su mailbox non standard
- Azioni di massa (>5 email contemporaneamente)

## Note sulla lingua

L'utente preferisce risposte in italiano. Mantieni i nomi tecnici (REPLY, ARCHIVE, ecc.) in inglese per chiarezza, ma il resto della spiegazione in italiano.

## Esempio di esecuzione

```
User: /mail-triage
Claude: [esegue osascript ... 20 true all]
Claude: 📬 INBOX TRIAGE — 12 email analizzate
        🔴 P1 URGENT (2)
        [1] cliente@example.com — Fattura n.123 da pagare entro venerdì
            💡 ✍️ REPLY: conferma il pagamento e invia ricevuta
        ...
```
