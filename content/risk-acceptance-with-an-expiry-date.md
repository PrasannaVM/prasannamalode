---
id: risk-acceptance-with-an-expiry-date
title: The Vulnerability I Accepted, and the Expiry Date I Put on It
tag: DevSecOps
date: 2026-02-24
series: Shifting Left Without Shifting the Blame
part: 3
summary: A 1,900-line suppression file is four years of defensible calls adding up to something indefensible. Risk acceptance as a record with an owner, an expiry, and a CI job that enforces both.
---

I once opened a suppression file that was 1,900 lines long.

It had been started four years earlier. It had eleven distinct comment styles in it, which is roughly one per engineer who had ever touched it. Some entries had a ticket number; most of those tickets were closed, and a few referenced a tracker the company no longer used. One entry said `# temporary - remove after migration`. The migration it referred to had completed two years before.

Nobody had done anything wrong. Every single line had been added by a reasonable person under deadline pressure making a defensible call. The file was the sum of four years of defensible calls, and the sum was indefensible.

That is the real problem with risk acceptance. Not that individual decisions are bad. That they never end.

## Suppression is not a decision, it is the absence of one

Watch what happens when a finding is suppressed in a typical setup.

Somebody adds a line. Maybe a comment. The scanner goes quiet. The PR goes green. And then — this is the important part — *nothing else ever happens*. No record of who decided, no record of why, no date, no review, no signal if the surrounding conditions change.

A decision that produces no artefact and triggers no future event is not a decision. It is deferral wearing a decision's clothes. And deferral accumulates silently, which means the cost lands on somebody who was not in the room, often years later, usually during an incident.

The fix is not to forbid acceptance. Acceptance is legitimate and necessary — plenty of findings genuinely are not worth fixing this quarter, and a security function that cannot say "fine, not now" is a security function that gets routed around.

The fix is to make acceptance **structured, owned, and temporary**.

## What an acceptance record has to contain

Five fields. If any one is missing, it is not an acceptance, it is a suppression.

1. **Owner** — a named person, not a team. Teams do not get paged, do not leave the company, and do not feel accountable.
2. **Expiry** — a date. Not "when we migrate". Not "next quarter". A date that a computer can compare against `now()`.
3. **Rationale** — why this is tolerable *now*. Written for a stranger, because in eighteen months the reader will be one.
4. **Compensating control** — what reduces the impact in the meantime. WAF rule, network boundary, feature flag, monitoring alert. If the answer is honestly "nothing", write "nothing" — that is valuable information.
5. **Trigger conditions** — what would make this unacceptable before the expiry date. "If this service starts handling payment data." "If a public exploit lands." This is the field everyone skips and it is the one that catches the real disasters.

Here is what that looks like as a file that lives in the repo:

```yaml
# security/acceptances.yaml
- id: ACC-2026-007
  finding: CVE-2025-XXXXX
  component: github.com/example/imageproc
  severity: high

  owner: priya.raman           # a person
  accepted_on: 2026-01-12
  expires_on: 2026-04-12       # 90 days for high

  rationale: >
    Vulnerable code path is the TIFF decoder. We only accept PNG and
    JPEG at the API boundary, enforced by content-type allowlist in
    gateway/filters.go:88. Upstream fix requires a major version bump
    that breaks our colour-profile handling.

  compensating_controls:
    - Content-type allowlist at the gateway (PNG, JPEG only)
    - Decoder runs in a seccomp-restricted sandbox
    - Alert on any non-allowlisted content-type reaching the decoder

  invalidating_conditions:
    - The gateway allowlist is widened to any additional format
    - A public exploit is observed in the wild
    - imageproc is called from any new service

  renewals: 0
```

Two properties matter here. It is in version control, so it is reviewable and blameable like code. And it is machine-readable, so the expiry can be enforced rather than hoped for.

## Enforcement is what makes it real

Every part of this is theatre without a job that fails the build when the date passes.

```python
#!/usr/bin/env python3
"""Fail CI when any risk acceptance has expired or is incomplete."""
import sys, datetime, yaml

REQUIRED = ["owner", "expires_on", "rationale",
            "compensating_controls", "invalidating_conditions"]
MAX_TERM = {"critical": 30, "high": 90, "medium": 180, "low": 365}
MAX_RENEWALS = 2

def main(path="security/acceptances.yaml"):
    today = datetime.date.today()
    records = yaml.safe_load(open(path)) or []
    errors, warnings = [], []

    for r in records:
        rid = r.get("id", "<no id>")

        missing = [f for f in REQUIRED if not r.get(f)]
        if missing:
            errors.append(f"{rid}: missing required fields: {', '.join(missing)}")
            continue

        expires = r["expires_on"]
        accepted = r["accepted_on"]
        term = (expires - accepted).days
        cap = MAX_TERM.get(r.get("severity", "low"), 365)
        if term > cap:
            errors.append(f"{rid}: term of {term}d exceeds {cap}d cap for {r['severity']}")

        if r.get("renewals", 0) > MAX_RENEWALS:
            errors.append(f"{rid}: renewed {r['renewals']} times — escalate, don't renew")

        days_left = (expires - today).days
        if days_left < 0:
            errors.append(f"{rid}: EXPIRED {abs(days_left)}d ago — owner {r['owner']}")
        elif days_left <= 14:
            warnings.append(f"{rid}: expires in {days_left}d — owner {r['owner']}")

    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")

    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
```

Wire it into CI so it runs on every push and on a schedule:

```yaml
# .github/workflows/acceptance-audit.yml
name: Risk acceptance audit

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 9 * * 1"   # Monday morning, so expiries surface before they bite

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pyyaml
      - run: python security/check_acceptances.py
```

The scheduled run is the part that does the work. It means an expiry arrives as a Monday-morning notification with fourteen days of warning, rather than as a red build on an unrelated PR from someone who has no idea what the record is about.

## Renewal is allowed. Silence is not.

People push back here, and the pushback is always the same: "so we just renew everything and nothing changes."

Two answers.

First, even pure renewal is an improvement, because renewal is *an event*. A human reads the rationale and decides again. Sometimes the rationale no longer holds — the compensating control was removed in a refactor, the service now handles data it did not before, an exploit was published. Without the expiry, none of those changes would ever be noticed. The whole value of the mechanism is that it forces a re-read.

Second, cap the renewals. Two is a reasonable limit. After that the item does not get renewed; it gets escalated to someone with budget authority, who either funds the fix or accepts it at a level where the accountability is real. That is not a punishment — it is the correct routing. An issue that has survived three review cycles without being fixed is not a triage problem, it is a resourcing problem, and it belongs with whoever controls resourcing.

Suggested terms, which you should tune to your own tolerance:

| Severity | Max term | Renewals before escalation |
|---|---|---|
| Critical | 30 days | 1 |
| High | 90 days | 2 |
| Medium | 180 days | 2 |
| Low | 365 days | 2 |

## Migrating a file you inherited

If you already have the 1,900-line file, do not try to adjudicate all of it. You will not finish, and the attempt will burn whatever goodwill you were going to spend on the actual fix.

What works:

1. **Freeze it.** Rename it `legacy-suppressions`. Make CI reject any new entries. From today, every new acceptance uses the structured format. This alone stops the bleeding, and it is a one-day change.
2. **Sample it.** Take 25 random entries and adjudicate them properly. You now have an estimate of what fraction of the file is stale, which is the number you take to leadership. In my experience the answer is well over half.
3. **Expire it in tranches.** Assign expiry dates to the legacy entries spread over the next twelve months, weighted by severity. Do not dump them all on one date.
4. **Let deletion be the default.** For legacy entries where no owner can be found, the default action at expiry is to remove the suppression and see what breaks. Half the time the finding is gone because the code is gone.

Step four sounds reckless and is not. An unowned suppression is an unowned risk. Surfacing it is strictly better than continuing to pretend somebody is watching it.

## The part that is actually about culture

The reason suppression files grow is that suppressing is frictionless and fixing is not. The mechanism above does not add friction to suppression — it takes about the same time to write the YAML as to add the comment. What it adds is **a future obligation**, and it makes that obligation visible at the moment of the decision.

That changes behaviour, in my experience, more than any approval workflow. When you write `expires_on: 2026-04-12` and your own name next to it, you are making a small promise to a specific future version of yourself. Most engineers, given that framing, will fix the easy ones immediately rather than schedule a conversation with themselves in ninety days.

The 1,900-line file was not a discipline failure. It was a design failure: a system where the cheapest path produced no record and no future event. Change the design, and most of the discipline problem evaporates.
