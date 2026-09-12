---
id: who-spent-this
title: Who Spent This?
tag: AI Governance
date: 2026-04-14
read: 6 min read
series: AI Governance for Engineering Leaders
part: 1
summary: Attribution in an LLM gateway is not a reporting problem. It is a key-issuance decision, and it has to be made before the first request.
---

There is a particular kind of silence that follows a simple question in a meeting.

Ours came in month three of running an internal LLM gateway. Someone from finance had the usage report open and asked what should have been a trivial question: which teams were driving the spend? Engineering wanted to know before they asked for more budget. Finance wanted to know before they approved it.

The report had one number. A big one, technically accurate, and completely useless. Every request had gone through the same API key.

We had done the hard part well. We had stood up a proxy, centralized model access, kept raw provider keys out of application code, and given ourselves a single place to enforce rate limits. On any architecture diagram it looked correct. The one thing we had not done was decide, before the first request, who each request belonged to.

## Attribution is a design decision

This is the part I got wrong, and I think a lot of teams get wrong in the same way: attribution feels like a reporting problem. It presents as a dashboard gap. It seems like the sort of thing you fix later by adding a column.

It is not a reporting problem. It is a key issuance problem, and key issuance happens at the beginning.

Whatever your gateway is — a commercial product, an open-source proxy, something you wrote yourself — it will let you mint virtual keys that sit in front of the real provider credentials. The question is what those keys map to. One key for the whole company. One per application. One per team. One per user.

Every answer downstream of that choice is fixed by it. Your usage data can only ever be as granular as your keys. If one key serves forty engineers, no amount of clever querying recovers which engineer did what. The information was never captured. You are not missing a report; you are missing a fact.

And the retrofit is genuinely painful, because it is not a schema change. It is a credential rotation across every integration you have built, coordinated with every team that depends on them, while the old key stays alive long enough that nobody's pipeline breaks. I have watched that project consume weeks that a fifteen-minute decision at the start would have saved entirely.

## Why security ends up caring more than finance

The budget conversation is what forces the issue. It is not the reason the issue matters.

Consider what happens when a key leaks. Someone commits it, or pastes it into a support ticket, or it ends up baked into a container image that gets pushed somewhere public. You find out — maybe from a spend anomaly, maybe from a scanner, maybe from someone outside the company being kind enough to tell you.

Now you are in incident response. The first questions are always the same. What could this credential reach? How long was it exposed? What was done with it? Who else is affected if we kill it right now?

With one shared key, every one of those questions returns the worst possible answer. It could reach everything. It was exposed since whenever it was created. What was done with it is indistinguishable from normal traffic, because normal traffic looks exactly the same. And revoking it takes the entire company offline, which means you will feel pressure to wait, investigate more, be careful — while the credential stays live.

With per-team or per-user keys, the same incident is a different event. Blast radius is scoped by construction. The traffic on that one key is a narrow, readable slice. Revocation affects one team, who you can notify in a Slack message. You go from an organizational emergency to a Tuesday.

That difference was not created during the incident. It was created months earlier, by someone deciding how to issue keys.

## The uncomfortable part about per-user

Per-user attribution is the most useful and the most contentious, so it deserves an honest paragraph rather than a recommendation.

Per-user keys give you the cleanest audit trail available. They also mean you are now holding a per-person record of interactions with a language model, and people use these tools to think out loud. Some of what they type is half-formed, or personal, or about problems they have not told anyone about yet. Depending on where your employees sit, that record may carry obligations you have not thought about.

I do not think there is a universal right answer. What I think is wrong is arriving at an answer by accident. Decide it deliberately, write down what you retain and for how long, tell people plainly what is logged, and be able to explain why. A team that knows the shape of the logging will work with it. A team that discovers it later will route around it, and then you have shadow AI on top of everything else.

If per-user is too heavy for your context, per-team is a defensible middle. It is coarse enough to avoid individual surveillance and fine enough that incident scoping and cost allocation both work. What is not defensible is one key for everyone, which is the option that feels like no decision at all.

## What I would tell myself at the start

Before the first request goes through the gateway, answer three things.

What is the smallest unit you need to attribute to? Pick it based on the incident you would least like to handle, not the report you would most like to see.

Who issues keys, and how does someone get one? If the answer involves a ticket that takes four days, you have just designed your shadow AI problem. Make the sanctioned path the fast path.

What happens when a key has to die? Write the runbook while nothing is on fire. It should be short. If it is long, your key structure is wrong.

None of this is sophisticated. It is the same least-privilege reasoning we have applied to service accounts for twenty years, pointed at a new kind of credential. The only reason it gets skipped is that the gateway works fine without it, right up until the moment it doesn't.

The number in that report was correct. That was the problem. It was one correct number where we needed forty, and the only moment we could have had forty was before we started.
