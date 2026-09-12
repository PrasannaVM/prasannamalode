---
id: the-queue-is-still-there
title: The Queue Is Still There
tag: AI Governance
date: 2026-05-26
read: 6 min read
series: AI Governance for Engineering Leaders
part: 3
summary: We put a model in front of the alert queue and it wrote beautiful summaries. The queue did not get shorter. Here is what did move the number.
---

We put a language model in front of our alert queue, and for about two weeks everyone was pleased.

Every alert now arrived with a paragraph at the top explaining what it was. Plain English, decent quality, genuinely well written. The analysts said it was nicer to read. Leadership liked the demo. I liked that we had shipped something.

Then I sat with one of the analysts for a shift and watched what actually happened.

She read the summary. Then she opened the raw alert anyway. Then she pivoted into the SIEM to check the source host. Then she looked up whether that host had fired the same thing before. Then she closed it as a false positive, the same way she would have without the summary, having spent an extra six seconds reading a paragraph that told her nothing she could act on.

We had not reduced her workload. We had added a pleasant preamble to it.

## The number that does not move

Here is the uncomfortable arithmetic of alert triage. If a hundred alerts arrive and ninety-four of them are noise, the work is not understanding the hundred. The work is getting to the six.

Summarization does not touch that. It makes each of the hundred marginally more pleasant to process, and a hundred slightly-nicer units of work is still a hundred units of work. The queue depth is identical. The time-to-the-six is roughly identical. You have improved the experience of doing the wrong amount of work.

This is the trap, and it is seductive precisely because summarization is the thing language models are unmistakably good at. It demos beautifully. It never looks broken. Nobody complains. It is the local maximum you can reach in a sprint, and reaching it feels like progress in a way that makes it hard to ask whether it was the right direction.

## What moved the number

When we rebuilt the thing, we changed the question. Not "how do we explain this alert" but "what does the analyst do next, and can we have already done it?"

That reframing produced a different system.

**Enrichment before summary.** Every one of those manual pivots — is this host in scope, has this signature fired before, who owns this asset, what changed on it recently, is the source address one of ours — is a lookup with a deterministic answer. Do them all, automatically, in parallel, before a human ever sees the alert. Most of the analyst's clock was not comprehension. It was fetching context that a script could fetch.

**Correlation before presentation.** Forty alerts from one misconfigured host are one piece of information presented forty times. Grouping them is not glamorous and it is not AI, but it did more for queue depth than anything else we built. Do this first. If your queue is full of duplicates, no amount of model cleverness matters, because you are summarizing the same thing forty times.

**A recommendation with its reasoning attached.** This is where the model earned its place. Not "here is what this alert says," which the analyst can read, but "this looks like the false positive class you closed eleven times last month, for these reasons, and here is the evidence." That is a claim she can accept or reject in two seconds. A summary gives her something to read. A recommendation gives her something to decide.

**A confidence signal that is allowed to say nothing.** The single most valuable behavior we built was the system declining to guess. When enrichment came back thin or contradictory, it said so and handed over cleanly, with the raw data and no narrative. A tool that is confidently wrong twice will not be trusted the third time it is right, and trust is the whole asset. Once analysts stop reading the recommendation, you own an expensive queue decoration.

## Automation earned, not assumed

The obvious next question is whether the model should just close the low-risk ones itself.

Eventually, for narrow classes, yes. But not on day one, and not on the basis of a vendor's accuracy claim.

What worked for us was shadow mode. The system made its recommendation. The analyst made the real decision. We compared them, by alert class, for long enough to have meaningful numbers. Where agreement was very high and the disagreements were consistently the model being appropriately more cautious, we promoted that specific class to auto-closure — with sampling, so a percentage still got human eyes, and with a monthly review of what the sampling found.

Everything else stayed advisory. Some of it still is.

This is slower than the deployment everyone wants. It is also the only version I have seen survive contact with a real incident review, because when someone eventually asks "why did nobody look at this," the answer needs to be a documented decision with evidence behind it, not a procurement decision with a confidence score behind it.

## What I would ask before building this

If you are about to point a model at your alert queue, I would ask three questions first, in this order.

What fraction of your queue is duplicate or correlated? If it is large, fix that before anything else. It is cheaper, it is deterministic, and it will deliver more than the model will.

Which lookups do your analysts perform on nearly every alert? Automate those. They are the actual minutes. You do not need a model for most of them.

And then, only then: where is the genuine judgment call, and can a model make it well enough that a human can verify the answer faster than they could produce it?

That last clause is the whole test. A tool that makes a judgment I must independently redo has cost me time. A tool that makes a judgment I can check at a glance has saved me most of it.

## The honest summary

The summaries were good. They were well written, accurate, and useless, and the reason they were useless had nothing to do with model quality. We had automated the part of the job that was not the job.

The queue is not hard because the alerts are hard to read. It is hard because there are too many of them and the important ones are indistinguishable from the rest until you do the work. Anything that does not reduce the count, or does not do the work, is decoration — however well it writes.
