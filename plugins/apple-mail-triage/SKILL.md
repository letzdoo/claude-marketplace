---
name: apple-mail-triage
description: Legge le email da Apple Mail (macOS), le ordina/categorizza e suggerisce azioni concrete da intraprendere (rispondi, archivia, elimina, segna, delega, programma). Usa quando l'utente chiede di "leggere le mail", "triage email", "controlla inbox", "cosa devo rispondere", "smista la posta".
---

# Apple Mail Triage Skill

Legge messaggi da Apple Mail tramite AppleScript, li categorizza e produce una lista di azioni prioritizzate.

## Quando usare questa skill

- "Leggi le mie email"
- "Fai il triage dell'inbox"
- "Cosa devo rispondere oggi?"
- "Smista la posta non letta"
- "Controlla se ci sono email urgenti"

## Comandi disponibili

- `/mail-triage` - Legge inbox, classifica e suggerisce azioni

## Categorie automatiche

- **URGENT** — richiede risposta entro 24h (clienti, scadenze, fatture)
- **WORK** — comunicazioni professionali (Odoo, btcp-srl, fornitori)
- **PERSONAL** — email personali
- **NEWSLETTER** — newsletter/digest informativi
- **PROMO** — promozioni e marketing
- **NOTIFICATION** — notifiche automatiche (sistemi, social, banche)
- **SPAM** — probabile spam

## Azioni suggerite

Per ogni email viene proposta una delle seguenti azioni:
- **REPLY** — rispondi (con bozza di risposta se richiesto)
- **ARCHIVE** — archivia (non richiede azione)
- **DELETE** — elimina (spam/promo)
- **FLAG** — segna per follow-up
- **DELEGATE** — inoltra a qualcun altro
- **SCHEDULE** — fissa un task/appuntamento

## Permessi richiesti

La prima esecuzione richiede di autorizzare l'accesso di Terminal/Claude Code a Mail.app (popup macOS in Impostazioni > Privacy > Automazione).

## Account supportati

Apple Mail su questo Mac contiene 5 account configurati (rilevati automaticamente):
- `btcpsn@gmail.com`
- `btcpsrl@gmail.com`
- `ndhadji@gmail.com`
- `elha@bitcoinpeople.it` (**Zoho EU** — bitcoinpeople.it ha MX su zoho.eu)
- `dimex.sn@gmail.com`

→ L'account Zoho `elha@bitcoinpeople.it` viene già letto via Apple Mail (parla IMAP con `imap.zoho.eu`). Non serve configurazione separata.

### Account Zoho aggiuntivi (es. zoho.com personali)

Per account Zoho NON in Apple Mail, esiste lo script Python `read_zoho_imap.py`. Configurazione:

```bash
# Genera app password su https://accounts.zoho.eu/home#security/app-passwords
cat > ~/.zoho_mail_creds <<EOF
{
  "email": "tuo@dominio.com",
  "app_password": "xxxx-xxxx-xxxx",
  "server": "imap.zoho.eu"
}
EOF
chmod 600 ~/.zoho_mail_creds
```

## Note

- Solo OPERAZIONI DI LETTURA di default
- Lo spostamento/eliminazione richiede conferma esplicita
- Nessun dato viene inviato a server esterni: tutto locale (AppleScript + IMAP diretto)
