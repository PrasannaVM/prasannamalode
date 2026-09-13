---
id: shift-left-has-a-ceiling
title: Shift Left Has a Ceiling
tag: DevSecOps
date: 2026-04-28
series: Shifting Left Without Shifting the Blame
part: 4
summary: Some defects do not exist until production exists. The classes above the ceiling, the shift-right toolkit, and escape rate, the metric that connects both halves of the pipeline.
---

Three posts arguing for moving controls earlier, and now the correction: there is a floor of defects that no amount of pre-deployment work will ever reach, and pretending otherwise is how organisations end up with an immaculate pipeline and a breach.

Some bugs do not exist until production exists. Not "are hard to find before production" — *do not exist*. They are properties of a running system under real load with real data and real concurrent users, and a static analyser examining source code is looking at the wrong object entirely.

## The classes that live above the ceiling

Four families, roughly.

**Load-dependent defects.** The race condition that needs two requests to arrive within the same few milliseconds. The connection pool that only deadlocks at a concurrency level your staging environment never reaches. The rate limiter that is correct per-instance and useless across twelve instances behind a load balancer. Your test suite runs these paths serially. Production does not.

**Data-dependent defects.** The authorisation check that is correct for every tenant in your seed data and wrong for the one enterprise customer with a nested org structure. The regex that is fine on ASCII and catastrophically backtracks on the input a real user pasted. You cannot fixture your way to this, because the defining property of the triggering data is that nobody imagined it.

**Configuration drift.** Your Terraform says the bucket is private. The bucket is not private, because someone fixed an incident at 2am eight months ago through the console and never came back. Static analysis reads what you *declared*. Only the running environment knows what is *true*, and the gap between those two grows continuously.

**Emergent cross-service behaviour.** Service A trusts requests from service B because they are both inside the perimeter. Service B was, in the meantime, given a new public endpoint. Neither repository contains the vulnerability. It exists only in the composition, and no analysis scoped to a single repo can see it.

That last one is worth sitting with. In an architecture with a few dozen services, a growing share of your real risk lives in the *relationships*, and relationships have no source file.

## Where risk actually gets created

There is a second reason the ceiling exists, and it is about what changes.

A large fraction of production incidents are triggered by change — and a large fraction of those changes are configuration, not code. Feature flag flips, scaling parameters, IAM policy edits, DNS records, rate limit adjustments. These are changes that alter system behaviour in production and frequently never pass through the pipeline you spent three years hardening.

If your entire control surface is the pull request, you are not covering the surface where a large share of your risk is introduced.

## The shift-right toolkit

The answer is not to abandon prevention. It is to stop treating deployment as the end of the security process.

**Progressive delivery.** If a change reaches 1% of traffic before 100%, then a defect that only appears under real traffic appears with a 99% smaller blast radius, and it appears while someone is still watching. Canaries and feature flags are security controls, even though they are almost never budgeted as such.

**Runtime authorisation telemetry.** Log every authorisation decision — subject, action, resource, verdict. Then alert on the shapes that should never occur: one principal accessing an anomalous number of distinct objects, a service account making a call it has never made before, a deny rate spiking on one endpoint. This is the only control that reliably catches IDOR-class flaws, because the signature of IDOR is not in the code, it is in the access pattern.

**Drift detection.** Run the plan continuously, not just at apply time:

```yaml
# .github/workflows/drift.yml
name: Infrastructure drift detection

on:
  schedule:
    - cron: "0 */6 * * *"
  workflow_dispatch:

jobs:
  detect:
    runs-on: ubuntu-latest
    permissions:
      id-token: write        # OIDC — no long-lived credentials
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111122223333:role/drift-detector
          aws-region: eu-west-1
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init -input=false
      - id: plan
        run: terraform plan -detailed-exitcode -lock=false -no-color
        continue-on-error: true
      - name: Raise drift issue
        if: steps.plan.outputs.exitcode == 2
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Infrastructure drift detected — ${new Date().toISOString().slice(0,10)}`,
              labels: ['drift', 'security'],
              body: 'Live infrastructure no longer matches committed state. See run logs.'
            })
```

Note the `id-token: write` and the absence of any stored AWS key. That is the pattern from part one — remove the secret rather than scan for it.

**Adversarial testing against the real thing.** Bug bounty and pentest are not compliance line items; they are the only controls that test the composed system the way an attacker would. The finding that comes back from a good bounty programme is almost always one that no scanner could have produced, because it depends on chaining three things across two services.

## Escape rate: the metric that connects both halves

Here is the number that makes this whole series cohere.

> **Vulnerability escape rate** = defects first discovered in production ÷ total defects discovered

Read it as a diagnostic, not a score:

- **Escape rate falling, total findings steady** — prevention is working. This is the good state.
- **Escape rate rising, total findings falling** — the alarming state. It usually means your left-side tooling has been tuned into silence, and you are discovering things in production instead. Part one's fix rate metric will confirm it.
- **Escape rate near zero** — do not celebrate. It almost always means you are not looking in production, not that nothing is there. Zero escapes is a detection failure, not a prevention triumph.

The operational discipline this creates: **every production finding becomes a specification for a left-side control.** For each escape, ask what would have caught it, and where it should have lived. Sometimes the answer is a new SAST rule. Sometimes it is a type-level guarantee from part two. Sometimes the honest answer is "nothing could have caught this before deploy", and that answer is valuable too, because it tells you to invest in detection rather than in another scanner.

Pair escape rate with **security MTTR** — time from discovery to deployed fix. Escape rate tells you how much gets through. MTTR tells you whether that matters. A team with a moderate escape rate and a four-hour MTTR is in far better shape than one with a low escape rate and a six-week deploy cycle, because the second team cannot respond to the zero-day that arrives on a Tuesday.

That framing lands well with engineering leadership, incidentally, because it is the same argument as DORA. Deployment frequency and lead time are security metrics. The ability to ship a fix in an hour is a security capability. This is the point where security stops asking for a slower pipeline and starts arguing for a faster one.

## What the whole series was arguing

Four posts, one thesis:

1. **Moving unfiltered machine output earlier is not shifting left.** It is interrupting people sooner. Measure fix rate, give every stage a latency budget, and prefer secure defaults over blocking gates.

2. **Only class-level work compounds.** Every instance you fix by hand returns. Climb the ladder: findable by machine, then loud on failure, then impossible to express.

3. **Acceptance is fine; silence is not.** Give every accepted risk an owner, an expiry, and a CI job that enforces both. Renewal is a legitimate outcome. Forgetting is not.

4. **And there is a ceiling.** Some defects exist only in the running system. Detect them deliberately, measure the escape rate, and feed every escape back into the left side as a new control.

The version of this that fails is the one where "shift left" means buying tools and pushing the resulting work onto developers while calling it empowerment. The version that works treats prevention and detection as one loop with a measured leak rate, where the security team owns the noise it generates and the loop teaches itself.

Start with the fix rate. It is one number, you can compute it this week, and it will tell you immediately whether the rest of this applies to you.
