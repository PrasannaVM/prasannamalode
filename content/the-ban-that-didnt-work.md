---
id: the-ban-that-didnt-work
title: The Ban That Didn't Work
tag: AI Governance
date: 2026-07-07
read: 6 min read
series: AI Governance for Engineering Leaders
part: 5
summary: A one-sentence AI policy, a four-month DNS log, and why making the sanctioned path the fast path beat every prohibition we tried.
---

The policy was one sentence long and it was not unreasonable: no company code or configuration is to be entered into external AI tools.

It was communicated well. People acknowledged it. Nobody argued with it, because nobody disagrees with the principle in the abstract.

Four months later I was looking at DNS logs for an unrelated reason and found steady traffic to consumer AI domains from engineering subnets, all day, every working day. Not a spike. Not one person. A baseline.

My first reaction was the wrong one. I started thinking about enforcement — blocklists, egress filtering, a stern follow-up message. It took a conversation with one of the engineers to understand what I was actually looking at.

She was not being reckless. She had a debugging problem at four in the afternoon, a stack trace she did not recognize, and a tool that could help. The sanctioned alternative required a ticket to request access. The ticket queue was measured in days. Her problem was measured in minutes.

She had not decided to violate policy. She had decided to do her job, and the policy had not offered her a way to do both.

## Prohibition has a prerequisite

Bans work when the prohibited thing is not very useful, or when the sanctioned substitute is at least as convenient. AI tools fail both conditions badly.

They are extremely useful for exactly the tasks engineers spend their days on — reading unfamiliar code, drafting boilerplate, explaining an error, writing the regex nobody wants to write, turning a vague requirement into a starting draft. And they are effortless to reach. No install, no procurement, no approval. A browser tab.

So a ban does not remove the behavior. It removes your visibility of the behavior. The usage moves from corporate laptops to personal phones, from the network you monitor to the one you don't, and from something you could have shaped into something you will now only learn about from the outside.

I have come to think of it as a rule: when a control makes a behavior invisible rather than absent, you have made your position worse than when you started. You have traded a governable risk for an ungovernable one and given yourself a compliance artifact that says otherwise.

## Make the sanctioned path the fast path

The thing that actually reduced our external traffic was not a stronger prohibition. It was reducing time-to-access from days to zero.

Concretely: every engineer got access by default, on joining, through our internal gateway. No request, no approval, no ticket. The credential existed before they needed it.

That single change did more than every message I had sent. Not because the engineers suddenly cared more about data governance, but because the friction that had pushed them outward disappeared. Given two tools of similar quality, people use the one that is already there.

A few things made it work, and they are worth being specific about.

**The internal option has to be good.** If the sanctioned tool is a lesser model behind a slow interface with a restrictive filter, people will use it for things that do not matter and go elsewhere for things that do — which inverts your intent perfectly. Budget for the good model. It is cheaper than the incident.

**Onboarding by default, not by request.** Any approval step reintroduces the delay you are trying to remove. If a class of user needs gating, gate that class; do not gate everyone to manage the exception.

**Say what is logged, in plain language.** People assume the worst about monitoring they have not had explained. A short, honest note about what is captured and retained produces far less avoidance than silence does. Vagueness reads as surveillance.

**Keep the guardrails about consequences, not vocabulary.** Blocking on keyword lists frustrates legitimate work constantly and stops determined misuse approximately never. Scope what the credential can reach, log what was done, and put your effort into the tail risks that would genuinely hurt.

## What the gateway gives you that the ban never could

Once the traffic is yours, the security work becomes ordinary work.

You have per-team attribution, so an exposed key is a scoped incident rather than a company-wide one. You have usage telemetry, which turns out to be a decent anomaly signal in its own right. You have a single place to change models, apply policy, and respond to a provider incident without touching forty applications.

And you have something less tangible that I did not anticipate: you find out what people are actually doing. Our usage patterns told me which teams had adopted these tools deeply and which had not touched them, which informed training, tooling decisions, and a couple of conversations about processes that were clearly painful enough that people were reaching for help.

None of that is available from a blocklist. A blocklist tells you a request was denied. It tells you nothing about the need that produced it, and the need does not go away when the request does.

## The part that is uncomfortable to say out loud

Shadow AI is a symptom, and the diagnosis is usually about us.

People go around controls when the controls cost more than the rule is worth to them. That is not a character flaw; it is a rational response to a badly priced obstacle. When I find a widely violated policy, the most useful question is not who is violating it. It is what it costs to comply, and whether we ever measured that before we wrote the rule.

We had written a sentence that was easy to write and expensive to follow, and then treated the resulting gap as a discipline problem.

The fix was not a better sentence. It was making compliance the path of least resistance, so that doing the right thing stopped requiring anyone to be heroic about it at four in the afternoon with a stack trace they did not recognize.
