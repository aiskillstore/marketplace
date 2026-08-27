# Safety Model

## Purpose

Inbox Guardian helps a mailbox owner apply rules they understand. It does not decide whether an email is malicious. A candidate means that one configured rule matched.

## Decision order

1. Messages labelled Starred, Sent, or Draft are protected.
2. Exact allowlisted email addresses and domains are protected.
3. Exact blocked email addresses and domains become candidates.
4. Subject and configured top-level-domain rules can create candidates.
5. Everything else is reported as legitimate for this limited rule set.

Subdomains match a configured domain. Lookalike domains do not. For example, `mail.example.com` matches `example.com`, while `example.com.bad` does not.

## Actions

Audit is the default action. It creates a local review file and does not change mail. Quarantine is a reviewed action that preserves the message while moving it out of the Inbox. Trash remains reversible through Gmail. Permanent deletion is not a public default because it is irreversible.

Permanent deletion requires `--hard-delete`, `--confirm-destructive`, the broader Gmail scope, and a typed confirmation. It must never be scheduled.

## Data handling

The utility stores its OAuth token, configuration, log, review files, local reputation database, and activity history beside the script. These files can expose mailbox access or mail metadata. Keep them out of version control and support requests.

The local activity history records sender and subject excerpts for reviewed actions so the dashboard can display recent activity. The reputation database records correspondents and domains found in Sent and Starred mail. Both are local, ignored by Git, and should be protected like mailbox data.

## Unsubscribe boundary

`List-Unsubscribe` headers are treated as a review signal. The utility does not follow them, call them, or send a one-click unsubscribe request. A header can be misleading or hostile.

## Testing boundary

The bundled tests check decision rules with a fake Gmail service. They do not prove that OAuth, Gmail label operations, an operating-system schedule, or a real mailbox will behave as expected. Test on a sacrificial mailbox before enabling scheduled audits.
