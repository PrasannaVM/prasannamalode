---
id: invoice-as-intrusion-detection
title: The Invoice as an Intrusion Detection System
tag: AI Governance
date: 2026-05-05
read: 6 min read
series: AI Governance for Engineering Leaders
part: 2
summary: Token spend is unforgeable, baselined for free, and denominated in a unit finance already tracks. Read it as a detection signal.
---

The first sign was not an alert. It was a graph with a step in it.

Saturday, some time after two in the morning, token consumption on one of our internal keys went from a flat weekend baseline to roughly forty times that, and stayed there. No error spike. No failed authentications. No unusual source geography that anyone had configured us to care about. Just a service that normally spent almost nothing overnight, suddenly working very hard at something.

Nobody was awake to see it. We found it on Monday, in a cost dashboard, because someone was doing budget planning.

It turned out to be a runaway retry loop — a misbehaving job that failed, retried, failed, retried, with no backoff and no ceiling. Expensive, embarrassing, not malicious. But the thing that stayed with me was not the root cause. It was that the same graph, with the same shape, is what a stolen API key looks like.

## Spend is behavior, rendered in a unit finance already tracks

We spend a lot of effort building telemetry for security. We ship logs, we normalize them, we write detections, we tune them. Meanwhile, sitting in a completely different part of the organization, there is a continuously updated, high-fidelity record of exactly how much work every credential has caused something to do.

Token consumption is a behavioral signal. It has properties that most of our detections would love to have.

It is unforgeable by the client. The consuming application does not get to report its own usage; the gateway counts it. Someone abusing a key cannot make the counter say something friendlier.

It is baselined almost for free. Most workloads are boringly regular. A summarization service handles roughly the number of documents that arrive. A coding assistant tracks the working hours of the people using it. Variance exists, but the shape of a week is stable enough that departures are visible without sophisticated modeling.

And it is denominated in a unit that non-security people already care about. This matters more than it sounds. You will never have to justify why you are monitoring cost.

## The shapes worth naming

Not every anomaly is interesting. These are the ones I have learned to look at.

**The step function.** Flat, then high, then flat at the new level. Automation, either yours misbehaving or someone else's. The overnight version is the one to care about, because legitimate step changes usually accompany a deploy, and deploys usually happen when people are awake. Correlate against your release calendar before you page anyone.

**The slow ramp.** Consumption climbing a few percent a day for weeks. Almost never an attack. Almost always a product decision nobody costed — a feature quietly expanded to more users, or a prompt that grew a few hundred tokens of context each time someone improved it. Worth catching anyway, because this is how a budget dies without a single alarming day.

**The pattern break.** Total volume unchanged, but the mix is different. A key that has only ever called a small fast model starts calling the largest one. A service that has always sent short requests starts sending very long ones. This one is the most interesting from a security standpoint, because it is the least likely to be accidental. Software does not spontaneously develop new preferences. Something changed the caller, or something else is using the credential.

**The weekend floor that lifts.** Every environment has a natural quiet period. When the floor of that quiet period rises and stays risen, something now runs continuously that did not before.

## Why this catches things your other controls miss

A leaked LLM gateway key is an awkward artifact. It is not a database credential, so your data-access monitoring does not see it. It usually does not touch your network perimeter in an interesting way, because the traffic is ordinary HTTPS to an endpoint you have deliberately allowed. It rarely triggers authentication alerting, because the authentication succeeds — that is the entire point of a stolen credential.

What it cannot hide is that it costs money to use. Whoever has it is using it for something, and using it is the only thing that makes it worth having.

That is an unusually good property for a detection to rest on. You are not watching for a signature that can be changed or an anomaly that can be smoothed out. You are watching the one behavior that is inseparable from the motive.

## Making it actually work

Three practical notes, because the idea is easy and the implementation is where it goes quiet.

First, this requires the attribution I have written about elsewhere. A single shared key gives you one aggregate line, and aggregates hide everything. Forty times normal on one team's key is obvious. The same absolute increase spread across company-wide totals is a rounding error you will never notice.

Second, alert on rate of change, not on absolute thresholds. Absolute limits are a budget control, and they should exist, but they fire when you have already spent the money. A derivative-based alert — this key is consuming at N times its trailing baseline — fires while it is happening. Set the baseline per key, not globally, because a key serving a batch pipeline and a key serving an internal chat tool have nothing in common.

Third, route it somewhere a human reads at odd hours, or accept that you will find these on Monday. I am not going to pretend every organization should page for this. But decide consciously. Our Saturday event ran for roughly thirty hours because the answer to "who sees this" was nobody, and nobody had ever been asked.

## The wider point

There is a habit in security of assuming that a good signal must come from a security tool. It leads to us instrumenting elaborately for detections that a billing system was already providing for free.

Your gateway is producing cost telemetry whether you look at it or not. Someone in finance is already looking at it, once a month, for entirely different reasons. The distance between their dashboard and a working detection is smaller than the distance between where you are and most of the detections on your roadmap.

Go and read that graph. You may find, as we did, that the interesting event happened weeks ago and has been sitting there patiently, correctly recorded, waiting for someone to ask what it was.
