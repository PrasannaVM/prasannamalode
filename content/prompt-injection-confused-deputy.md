---
id: prompt-injection-confused-deputy
title: Prompt Injection Is Not a New Class of Vulnerability
tag: AI Governance
date: 2026-06-16
read: 6 min read
series: AI Governance for Engineering Leaders
part: 4
summary: Prompt injection is a confused deputy problem we have known about since 1988. Threat model the tools, not the prompt.
---

Someone built a helpful thing. That is how these always start.

It was an internal assistant that answered questions about our documentation. Ask it how a process worked, and it would search the wiki, read the relevant pages, and answer. Useful, popular, built quickly by a good engineer in the spirit of making everyone's life easier.

Then, to make it more useful, it was given the ability to read from a ticketing system too. Also sensible. Most of the questions people asked involved work in flight.

The demonstration that ended the conversation took about a minute. A ticket was created containing, in its description field, a paragraph of ordinary-looking text that concluded with an instruction addressed to the assistant. When the next person asked a question that caused the assistant to search tickets, it read that paragraph, and it did what the paragraph said.

Nobody had exploited a model. Someone had typed text into a field that the system treated as instructions.

## Where the security industry went briefly strange

For a while the discussion around prompt injection had an air of novelty about it, as though we had encountered a genuinely new phenomenon requiring genuinely new theory. Papers, taxonomies, a small industry of detection products.

I want to argue for a more boring framing, because I think the boring framing is the one that actually leads to fixes.

Prompt injection is a confused deputy problem. It has a name because we have known about it since 1988. A program with legitimate authority is induced by a less-privileged party to exercise that authority on their behalf. SQL injection is this. Cross-site request forgery is this. Server-side request forgery is this. The LLM variant is this.

What makes it feel new is that the boundary between instruction and data, which in SQL we could at least in principle draw with parameterized queries, cannot be drawn cleanly here. The model consumes one stream of tokens. There is no prepared statement. There is no escaping function that reliably works, and I would be cautious about anyone selling you one.

But "we cannot fix it at the parser" does not mean "we cannot fix it." It means we fix it where we have always fixed problems we could not fix at the parser: at the boundary of what the deputy is permitted to do.

## The question that actually matters

Stop asking whether the model can be tricked. Assume it can. Every serious attempt to prevent that through instruction-hardening has been defeated, usually quickly, usually by someone doing it for fun.

Ask instead: when it is tricked, what can happen?

If the answer is "it writes a wrong answer to a user's screen," you have a quality problem. Annoying, not urgent.

If the answer is "it calls an API that modifies a record," you have a vulnerability, and the severity is defined entirely by what that API can reach.

If the answer is "it reads from a privileged source and then writes to somewhere the attacker can observe," you have data exfiltration, and the model is not the interesting part of the chain. The interesting part is that you connected a read capability and a write capability through a component that will follow instructions from anywhere.

That last one is the pattern to watch for, and it is why the retrieval-plus-tools architecture is where most of the real damage lives. Retrieval brings untrusted content into the context. Tools give the context consequences. Either alone is mostly fine. The combination is where you need to be deliberate.

## Controls that are already in your toolkit

None of what follows will be unfamiliar. That is the point.

**Least privilege, applied to the tool layer.** The credentials the assistant uses should be its own, scoped to exactly the actions it needs. If it only answers questions, it gets read access and nothing else. I have seen assistants running with a service account inherited from an existing integration, carrying permissions that made sense for a nightly batch job and no sense at all for a component that reads user input.

**User-context propagation.** If the assistant acts for a person, it should act with that person's authority, not with a superset of everyone's. Otherwise it becomes an access-control bypass with a chat interface, and the first person to notice will not report it.

**Human confirmation on state change.** Reads are recoverable. Writes, sends, deletes, and payments are not. A confirmation step on consequential actions is unglamorous and defeats the entire exfiltration-by-tool-call category, because the loop passes through a person who did not ask for that.

**Egress control on the output path.** If the assistant can render images from arbitrary URLs, or follow links, or call a webhook with data it has assembled, it has a channel out. Treat that with the same suspicion you would treat any outbound connection from a component processing untrusted input.

**Provenance in the context.** You cannot reliably teach a model to disregard instructions in retrieved content. You can mark which parts of the context came from trusted configuration and which came from a wiki page anyone can edit, and you can make policy decisions about what actions are permitted when untrusted content is in play. This is defense in depth, not a boundary. It reduces the severity distribution; it does not eliminate the tail.

## The part I would put on a slide

Threat model the tools, not the prompt.

Write down every capability the system has. For each one, ask what an attacker would do with it if they controlled the model's output completely, because in the worst case they do. Whatever survives that exercise is your real security posture. Whatever you were planning to achieve with careful system prompt wording is not a control; it is a preference, and it will be honored until someone decides otherwise.

The engineer who built our assistant was not careless. He had built a document search tool that happened to be conversational, and the day it gained a second data source it silently became a different kind of system — one where content written by one user could steer behavior on behalf of another. That transition happened in a pull request that looked like a feature addition, because it was one.

The failure was not in the model. It was that we had no review step that noticed the architecture had changed. That is a process gap, and process gaps are something our field already knows how to close. We just have to recognize the problem as ours.
