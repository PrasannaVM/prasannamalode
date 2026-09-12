---
id: same-binary-under-four-names
title: The Same Binary Under Four Names
tag: AI Governance
date: 2026-07-28
read: 6 min read
series: AI Governance for Engineering Leaders
part: 6
summary: When a CVE lands in rebranded platform software, "who is affected" becomes archaeology. Provenance has to be captured at build time.
---

A CVE lands on a Thursday afternoon in a library nobody thinks about — the kind that arrives in your dependency tree three levels down, through something you did choose, and has been sitting there for years doing its job quietly.

The first question is easy: do we ship it? Yes.

The second question is the one that costs you your evening: which of the things we have shipped contain it, and who has them?

If you build one product and ship it under one name, that question has a short answer. If you build platform software that goes out under partner branding, with per-customer feature sets, on release trains that diverged eighteen months ago, the answer is a research project — and every hour of that research project is an hour your customers are waiting for a straight answer to a simple question.

## What rebranding does to provenance

The technical situation is ordinary. The same core, built with different configuration, packaged under different names, for different partners.

The record-keeping situation is where it goes wrong, because the identity of the artifact is no longer a single thing. There is what you call it internally. There is what it is called on the box. There is the version the customer sees, which may not match the version in your source control, because the partner wanted their own numbering. There is the build that went to one customer in March and the build that went to another in June, which share a base but not a patch level.

Ask "is customer X affected" and you are really asking a chain of questions. Which product name did they receive? Which internal build does that correspond to? Which source revision did that build come from? Which dependency versions were resolved at that build? And did anything get patched in between for that customer specifically?

Every one of those links is somewhere. That is the thing — the information almost always exists. It lives in a build system, a release ticket, a shipping record, a spreadsheet one person maintains. The links exist and they are not joined, so answering the question means a human walking the chain by hand, once per customer, under time pressure, while being asked for updates.

## The record has to be made at build time

This is the lesson, and it is the same lesson as attribution in an LLM gateway, which is probably not a coincidence.

You cannot reconstruct provenance afterwards. You can only capture it at the moment the artifact is created, because that is the only moment when everything is simultaneously known — the source revision, the resolved dependency versions, the build configuration, the toolchain, the flags. An hour later, some of that is inference. A year later, some of it is archaeology.

So generate the bill of materials as a build output, not as a periodic exercise. Not a scan of the repository, which describes what the source declares, but a record of what the build actually produced and included. Those differ more often than people expect, particularly where transitive dependencies, vendored code, or build-time resolution are involved.

Then attach it to the artifact by hash. Not by version string, which is a label someone can reuse, and definitely not by filename, which is the thing that changes under rebranding. The hash is the only identifier that survives every renaming downstream of it, which makes it the only reliable join key you have.

## The join nobody owns

Here is the gap I see most often, and it is organizational rather than technical.

Engineering knows which source revision produced which build. Sales, or operations, or whoever manages the partner relationship, knows which customer received which named release. These two facts live in different systems, maintained by different teams, with no shared key between them, and no single person whose job it is to be able to join them.

That join is the entire answer to "who is affected." Without it, your SBOM discipline gets you to "build 7.2.1-internal contains the vulnerable library," which is true and does not tell you who to call.

Fixing it does not require a platform. It requires deciding that shipment records reference build identifiers, and that build identifiers reference source and dependency state, and that somebody owns keeping that true. The technology is a foreign key. The hard part is agreeing that it matters before the Thursday when it does.

## The tempting shortcut

There is a version of this where you decide that since it is all the same core, you can answer at the core level. Is the vulnerable library in the 7.2 line? Yes. Then everyone on 7.2 is affected. Notify everyone.

This feels rigorous. It is over-notification, and over-notification has a cost that is easy to underestimate.

Customers who receive advisories for things that do not affect them — because the vulnerable component was not compiled into their configuration, or the feature is disabled in their build — learn to filter your advisories. They allocate less attention to each one. Eventually one arrives that genuinely matters and it lands in the same mental bucket as the last six that did not.

Precision is not a nicety here. It is what preserves the value of the channel for the day you need it.

## What good looks like on a Thursday

The version of this I would like to live in is unremarkable. The CVE lands. Someone queries the dependency across all build records and gets the affected build hashes in minutes. Those hashes join to shipment records and produce a customer list, with which branded name each of them knows the product by. The advisory goes out with the right product names on it, to the right people, the same day.

No archaeology. No spreadsheet. No engineer reconstructing a build from eighteen months ago to find out what was in it.

Every part of that is infrastructure you build on a quiet week, for an event you cannot schedule. Which is exactly why it tends not to get built — it has no deadline until the deadline is already past, and then it is the most obviously necessary thing you never did.
