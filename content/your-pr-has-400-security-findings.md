---
id: your-pr-has-400-security-findings
title: Your PR Has 400 Security Findings. Nobody Is Going to Fix Them.
tag: DevSecOps
date: 2025-11-25
series: Shifting Left Without Shifting the Blame
part: 1
summary: Coverage is a vanity metric. Track fix rate per tool, give every pipeline stage a latency budget, and prefer secure defaults over blocking gates.
---

There is a specific moment I want to describe, because I think most engineers have lived it and nobody writes it down.

You open a pull request. It changes eleven lines in a config file. The checks run. Fourteen minutes later you come back to a wall of red: 400-odd findings from six different tools, most of them in files you have never opened, several of them duplicates of each other described in different vocabularies, one of them possibly real.

You scroll. You do not read. You look for the button that makes it go away.

That reflex — the scroll, the scan for the override — is the actual output of most shift-left programmes. Not fixes. A reflex.

## Coverage is a vanity metric

Here is the story security programmes tell themselves. We added SAST. We added SCA. We added secret scanning, IaC policy, container scanning, license compliance. Coverage went from 20% of repositories to 95% of repositories. The quarterly slide is green.

Here is the story the codebase tells. Findings went up. Fixes did not. The delta went into a suppression file.

Coverage measures how many tools you bought and wired up. It measures procurement. It says nothing about whether a single vulnerability left the codebase.

The number that matters is the fix rate:

> Of the findings surfaced in a given period, what fraction were remediated in code — not suppressed, not marked won't-fix, not aged out?

Track that monthly. Track it per tool. The first time you look at it per tool, you will find at least one scanner with a fix rate near zero, which means it has been generating pure noise and consuming review attention for however long you have had it.

That tool is not a partial win. It is negative. It is making your other tools worse.

## Why adding a scanner makes your other scanners worse

Developer attention on a pull request is fixed. Call it a few minutes. That budget does not expand because you added a seventh tool; it just gets divided more thinly.

So each new scanner does two things at once. It adds some true positives, which is the reason you bought it. And it dilutes the average quality of the findings list, which lowers the probability that any individual finding — including the ones from your good tools — gets read.

Below some threshold of precision, the second effect dominates. You cross a line where the list stops being a list of problems and starts being an obstacle. Once developers learn that the security check is usually wrong, they stop evaluating findings individually. They evaluate the *category*: "that's the security check, it's always noisy." And at that point your genuinely critical finding is indistinguishable from a style nit about a test fixture.

You cannot fix this by adding a tenth tool that ranks the other nine. You fix it by turning tools off.

**The uncomfortable exercise:** pick your noisiest scanner. Turn it off in the PR entirely. Move it to nightly with a named owner. Watch the fix rate on your remaining tools. In my experience it goes up, because the remaining findings are now read.

## The feedback latency budget

The second structural mistake is putting checks in the wrong place. Not the wrong tool — the wrong *stage*.

The principle is that a check earns its stage by how fast it can answer, not by how important somebody thinks it is. Importance determines whether you run it at all. Runtime determines where.

| Stage | Budget | What belongs here | What kills it |
|---|---|---|---|
| Editor | < 1s | Type checks, linters, secret patterns, known-bad API usage | Anything needing a build |
| Pre-commit | < 10s | Fast SAST on the diff, entropy scan on staged files | Whole-repo analysis |
| Pull request | < 10 min | SCA on changed dependencies, IaC policy, unit and contract tests | Full DAST, deep taint analysis |
| Nightly | hours | Full-repo SAST, DAST, fuzzing, image and base-layer scanning | Nothing — this is the dumping ground, and that is fine |
| Backlog | days+ | — | Everything. This is where findings go to die. |

The common failure is to take a check that genuinely takes 40 minutes and put it in the PR anyway, because it is important. Importance does not make it faster. What it produces is a 40-minute PR cycle, which produces batching, which produces bigger PRs, which produces worse review — so your important check has now degraded the quality of human review across the whole repository.

If a check cannot meet its stage's budget, you have two honest options. Narrow its scope so it only analyses the diff. Or move it right and give it an owner who triages the output on a schedule.

The dishonest third option is to keep it in the PR and let people learn to ignore it.

## Guardrails beat gates

The deepest version of this problem is that blocking checks are a weak instrument. A gate stops the build. It does not teach anything, it does not fix anything, and it creates pressure to find the bypass. Every organisation that leans hard on gates develops a culture of bypass — an `--no-verify` habit, a `security-exception` label that nobody audits, a shared admin account that can force-merge.

Secure defaults work differently. They are invisible. Nobody notices them, nobody argues with them, and they have a 100% adoption rate on new code.

Some concrete substitutions:

- **Instead of** a scanner that flags plaintext HTTP in Terraform, **ship** a module where the listener block is not exposed and TLS is the only path.
- **Instead of** a check that fails on missing resource limits in Kubernetes manifests, **set** a LimitRange on the namespace so the default is correct.
- **Instead of** a secret scanner in the PR, **remove** long-lived secrets from CI entirely with OIDC federation, so there is nothing to leak.
- **Instead of** a SAST rule for SQL string concatenation, **make** the raw-query function private and export only the parameterised one.

The pattern: move the control from *detection at review time* to *impossibility at authoring time*. That is the real meaning of shifting left, and it has nothing to do with scanners.

## What a healthy programme looks like

A short checklist you can hold your own setup against:

1. **Fix rate is reported per tool, monthly.** Any tool below a threshold you set gets moved out of the PR or removed.
2. **False positive rate is measured**, by sampling — take 30 random findings a month and have an engineer adjudicate them. You cannot manage what you have not sampled.
3. **Every stage has a latency budget** and a check that exceeds it gets moved, not excused.
4. **Suppressions expire.** (This is the subject of part three.)
5. **Every recurring finding class has a ticket to eliminate the class**, not a ticket to fix the instances. (Part two.)
6. **The security team owns the noise.** If a tool is noisy, that is a security-team defect, not a developer-discipline problem.

Point six is the cultural one and the hardest. The default posture in a lot of organisations is that findings are the developer's problem and triage is the developer's job. That posture guarantees noise, because nobody who generates the noise pays for it. Put the cost where the decision is made: the team that turns on the scanner owns its precision.

## The honest summary

Shift-left, as commonly practised, is the act of moving unfiltered machine output earlier in the process and calling the relocation an improvement. It is not. Moving a bad signal earlier just means you interrupt people sooner.

The thing worth moving left is not *detection*. It is *decision*: the design choice, the default, the library boundary, the credential architecture. Those are the things that, moved left, stop bugs from existing.

Detection is what you do about the ones that get through anyway. Keep it, tune it hard, measure it honestly, and stop pretending the size of the findings list is a measure of anything but the size of the findings list.
