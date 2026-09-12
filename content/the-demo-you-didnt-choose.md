---
id: the-demo-you-didnt-choose
title: The Demo You Didn't Choose
tag: AI Governance
date: 2026-09-08
read: 6 min read
series: AI Governance for Engineering Leaders
part: 8
summary: Every AI security vendor demo answers one question: can it handle a case chosen to be handleable. Here are the questions I ask instead.
---

Halfway through the third vendor demo of the month, I realized I had watched the same thirty minutes three times.

Different companies, different logos, genuinely different products underneath. But the structure was identical. An alert appears. The AI reads it. The AI explains it in fluent prose. The AI recommends a response. The response is correct. Somebody says the phrase "in seconds, not hours."

And every single time, the alert was one the vendor had selected.

That is not dishonest. Of course they pick a good example; I would too. But it means the demo answers exactly one question — can this system handle a case chosen to be handleable — and that is not a question I need answered. I need to know what happens on the cases nobody chose.

So I started asking different questions, and the quality of the conversation changed immediately.

## Ask what it does when it does not know

This is the question I now ask first, and it is remarkably good at sorting vendors.

Every one of these systems will encounter inputs outside what it handles well. The only thing that varies is what happens next. Does it say so? Does it hand off with the raw data intact? Or does it produce a confident, fluent, wrong answer that looks exactly like its right ones?

A vendor who has thought hard about this will answer quickly and specifically, because they have had to build the behavior and probably argued about it internally. A vendor who has not will reach for the accuracy number — and the accuracy number is not the answer. A system that is right ninety-five percent of the time and indistinguishable in presentation the other five is a system your analysts must verify completely, which means it has saved them nothing.

Ask to see the uncertain case. Ask what the interface looks like when confidence is low. If there is no distinct behavior, you are buying something that will be trusted exactly until it burns someone, and then trusted by nobody.

## Ask what it can do, not what it can say

Any product with tool access has an authority model, whether or not anyone has articulated it.

What credentials does it hold? What can it read? What can it change? Does it act with the permissions of the user who asked, or with a service account that aggregates everyone's? Is there a confirmation step before consequential actions, and who configures it?

I want these answers written down, not described. The gap between a vendor's mental model of their permission architecture and its actual implementation is where a lot of unpleasant surprises live, and writing it out tends to surface it.

The related question, for anything that ingests content from outside: what happens when that content contains instructions? If the answer is that the model is trained not to follow them, that is a mitigation, not a boundary. Ask what constrains the damage when the mitigation fails, because the useful answer is about capability limits, not about model behavior.

## Ask where the data goes and how long it stays

Straightforward, frequently glossed over, and worth being tedious about.

Where is inference performed? Which subprocessors are involved? Is customer data used for training, by them or by anyone downstream? What is retained, where, for how long? What happens to it when the contract ends?

The subprocessor question is the one that catches people, because a vendor can answer "we do not train on your data" with complete sincerity while routing it to a model provider whose terms are a separate conversation you have not had. Ask about the whole chain.

And ask about incidents: if their provider has a breach, what is your notification path, and what is the timeline? You want that established before it is relevant.

## Ask how it fails over time

Products get demonstrated at their best moment. Systems live in a world where things drift.

What happens when the underlying model is updated — do you get notice, can you pin a version, does behavior change under you? What happens when your environment changes, when you add a data source or restructure a naming convention? What is the retuning burden, who carries it, and how quickly do you find out that performance has degraded?

That last one deserves emphasis. Detection systems fail silently. A rule that stops matching does not raise an alarm; it just stops producing results, and absence of alerts is indistinguishable from absence of threats until something confirms otherwise. Ask how you would know. If the answer is that you would notice, the answer is that you would not.

## Ask for the boring version of the ROI claim

"Reduces triage time by eighty percent" is a statement about a measurement someone performed. It is not necessarily false. It is just meaningless until you know the shape of it.

Measured against what baseline — a well-tuned process or a neglected one? Across which alert classes? At what organization size, with what data quality? Was the comparison run concurrently or before-and-after, and what else changed in between?

You are not trying to catch anyone out. You are trying to work out whether the environment where that number was produced resembles yours. Often it does not, and a vendor with a real deployment behind the number will happily tell you the conditions, because the conditions are where their credibility lives.

## The one that ends most conversations

Run it on my data, on my cases, in shadow mode, for long enough to matter.

Not a proof of concept with a curated dataset. Live traffic, real alerts, real messiness, running alongside the existing process without authority, for a period long enough to include a bad week. Then compare what it said to what actually happened.

This is the only evaluation that answers the question you actually have. It is also the request that separates vendors with a working product from vendors with a working demo, faster than any question in the list above.

The good ones say yes and ask how soon you can start. They want the comparison, because they have run it before and they know how it comes out.

The rest explain why their architecture makes that difficult.
