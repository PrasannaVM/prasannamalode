---
id: code-review-at-machine-scale
title: When Review Breaks: Code at Machine Scale
tag: AI Governance
date: 2026-08-18
read: 7 min read
series: AI Governance for Engineering Leaders
part: 7
summary: PR throughput doubled and review time per PR halved. Coding assistants uncoupled production from review capacity, and nobody sent an email.
---

The metric that should have worried me was the one everybody was pleased about.

Pull request throughput on one of our teams roughly doubled over a quarter. More code written, more code merged, velocity charts pointing in the direction velocity charts are supposed to point. The team was using coding assistants heavily and openly, and by every measure we tracked, it was working.

What we did not track was review time per pull request. When I went back and looked, it had fallen by about the same factor the volume had risen.

The reviewers had not become faster readers. They had been handed twice the work in the same number of hours, and they had adapted the way anyone adapts: by reading less carefully, approving more readily, and reserving real scrutiny for the changes that looked like they needed it.

Which is precisely the failure mode, because looking like it needs scrutiny is a property we are bad at judging, and AI-generated code is unusually good at not looking like it needs it.

## The assumptions underneath code review

Code review is an old practice and it rests on premises we rarely say out loud.

It assumes the author understands the change. When a human writes a function, they have reasoned about it. The reviewer is checking that reasoning. When an assistant produces a function and a human accepts it, the reasoning may or may not have happened, and from the diff you cannot tell.

It assumes production rate and review capacity are roughly matched. Both used to be bounded by the same resource — human hours. That coupling is what made review sustainable. Assistants uncouple them. Production scales; review does not.

It assumes that surface quality correlates with underlying care. This is the heuristic that does the most quiet work in real reviews. Consistent naming, sensible structure, handled errors, comments in the right places — these tell you someone was paying attention, and reviewers calibrate their scrutiny accordingly.

Generated code has excellent surface quality. It is well formatted, idiomatically named, plausibly commented, and structurally clean, regardless of whether it is correct. The correlation the heuristic depends on is simply gone, and the heuristic does not announce that it has stopped working. It just keeps producing confident, unjustified reassurance.

## What actually shows up

I want to be careful here, because the discourse tends toward the dramatic and my experience has been more mundane.

I have not seen assistants produce obviously dangerous code very often. Ask for a database query and you generally get a parameterized one. The blatant failures are increasingly rare, and the tooling gets better every release.

What I have seen is subtler and harder to catch.

**Context-blind correctness.** Code that is right in general and wrong here — a retry that is sensible unless the operation is non-idempotent, a cache that is fine unless the data is per-tenant, an error swallowed in a way that is reasonable in a script and not in a payment path. The model does not know your system's invariants. It knows what code like this usually looks like.

**Plausible API usage that is subtly off.** A library called with almost the right arguments, or with a default the author did not consider, or in a pattern deprecated two versions back. It compiles. It passes the happy path. It reads as though someone knew what they were doing.

**Volume dilution.** A necessary two-line fix arriving inside a three-hundred-line change that also refactored, renamed, and reorganized, because that was easy to generate. The important lines are in there somewhere. Nobody will find them.

**Silent dependency growth.** New imports appearing because the generated solution used them, without anyone deciding to take on the dependency. This one bothers me most, because it bypasses every process we have for evaluating what we pull into a build — not maliciously, just quietly, one convenient import at a time.

## Moving the checks to where scale is free

The response cannot be to ask reviewers to try harder. That is asking humans to absorb a machine-scale increase through willpower, and it fails in a predictable direction.

What has to change is where the checking happens.

**Automate everything mechanically checkable, and make it blocking.** Static analysis, dependency scanning, secret detection, license checking, coverage floors. These scale with volume at near-zero marginal cost. Every one of them that runs before a human opens the diff is attention returned to the human for the things only humans can do.

**Gate dependency additions explicitly.** A pull request introducing a new package should require a different, deliberate decision than one that does not. This is easy to enforce and it closes the quietest gap.

**Enforce change size.** Not as a style preference but as a review-integrity control. Large diffs do not get read; they get skimmed. If the tooling makes large diffs cheap to produce, the process has to make them expensive to merge.

**Direct human review at intent, not syntax.** The questions that matter are the ones no linter can ask. Does this belong in our architecture? Is this the right place for this logic? What happens to this under concurrency, at scale, on failure? Does it honor the invariants this system actually has? Reviewers should spend their scarce attention there, which means everything below that line must be handled before they arrive.

**Keep authorship accountable.** Whoever opens the pull request owns the code, regardless of what produced it. Not as a blame mechanism — as a clarity mechanism. "I did not write that part" has to not be an available answer, because the moment it is, the accountability model that review depends on has dissolved.

## The measurement I would add tomorrow

If you take one thing from this, take this: track review time per pull request alongside throughput, and watch the ratio.

Throughput alone will tell you a happy story. It told us one for a quarter. The ratio is where you find out whether your review process is still doing its job or has quietly become a formality that produces approvals at the rate they are requested.

The tools are good and getting better, and I am not arguing against using them — we do, deliberately and at volume. But they changed the shape of one side of an equation that had been balanced for decades, and they did it without changing anything on the other side. Nobody sends an email when that happens. You find it in a ratio you were not looking at, in a quarter everyone thought went well.
