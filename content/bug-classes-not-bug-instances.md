---
id: bug-classes-not-bug-instances
title: Bug Classes, Not Bug Instances
tag: DevSecOps
date: 2025-12-23
series: Shifting Left Without Shifting the Blame
part: 2
summary: Every vulnerability you fix by hand is one you will fix again. The four-rung ladder for eliminating whole categories: findable, loud, then impossible to write.
---

Look at your security backlog and count how many tickets are the same ticket.

Not literally identical — different files, different services, different authors. But the same shape. Four path traversal findings. Nine missing authorisation checks on new endpoints. Six places where a secret went into a log line. Every one of them gets its own ticket, its own fix, its own review, its own regression test.

And then next quarter you get another four, another nine, another six. Because nothing you did changed the conditions that produce them.

This is the treadmill, and most security engineering runs on it.

## The distinction

An **instance** is one occurrence of a defect in one place in one codebase. Fixing it removes exactly one defect.

A **class** is the set of conditions under which that defect can exist at all. Eliminating it removes every current instance and every future instance, including the ones that would have been written by an engineer who joins in two years and has never read your wiki.

Nearly all security tooling operates at the instance level. Scanners find instances. Tickets track instances. Metrics count instances. And because the tooling is instance-shaped, the work becomes instance-shaped, and you end up with a function that consumes headcount in proportion to how fast the rest of the company writes code.

That is not a security programme. That is a tax.

## The ladder

For any bug class, there are four rungs you can be standing on.

Most teams live on rung one and have convinced themselves that buying a rung-two tool is transformation. It helps — rung two is genuinely better than rung one — but the leverage is above it, and the leverage is where the engineering is.

Let me make each rung concrete.

### Rung 1 → 2: make the machine find it

The move here is from human vigilance to mechanical certainty. The signal that you are on rung one is a wiki page, an onboarding slide, or a code review checklist item. Any control that depends on somebody remembering is a rung-one control.

**Property-based testing** is the most underused tool in this category. Instead of asserting specific outputs for specific inputs, you assert an invariant and let the framework attack it:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_sanitiser_never_emits_angle_brackets(raw):
    out = sanitise_for_html(raw)
    assert "<" not in out and ">" not in out

@given(st.binary())
def test_parser_never_raises_unexpected(data):
    # The only acceptable failure is our own typed error
    try:
        parse_message(data)
    except ProtocolError:
        pass
```

That second test is a fuzzer in four lines. It will find the unicode edge case, the zero-length input, the surrogate pair, and the thing you did not think of — which is the entire point, because the things you did not think of are where the vulnerabilities are.

**Continuous fuzzing** is the same idea with a much bigger budget. If you parse anything untrusted — a file format, a wire protocol, a token, a config — and you are not fuzzing the parser, that parser is an unexplored attack surface. OSS-Fuzz is free for open source. For internal code, a nightly `cargo fuzz` or `libFuzzer` target on your parsing boundary costs a day to set up.

**Custom static analysis rules** belong here too, but with the warning from part one: a rule earns its place by precision. A rule with 40% precision is rung one wearing a costume, because a human still has to adjudicate every hit.

### Rung 2 → 3: make it fail loudly

Here the bug is still writable, but it stops being *silent*. Silence is what turns a bug into a vulnerability — the request that should have been denied but was served, the validation that was skipped without complaint.

```python
# Rung 1: authorisation is a thing you must remember to call
@app.get("/orders/{order_id}")
def get_order(order_id):
    return db.fetch_order(order_id)   # forgot the check, nothing complains

# Rung 3: absence of a decision is an error
@app.get("/orders/{order_id}")
@requires_authz                       # framework raises at request time if no policy is declared
def get_order(order_id, actor):
    authorize(actor, "order:read", order_id)
    return db.fetch_order(order_id)
```

The mechanism is that the framework refuses to serve a route with no declared policy. Forgetting is now a 500 in staging rather than a data leak in production. You have not made the mistake impossible, but you have made it *immediately visible*, which collapses the time-to-detection from months to minutes.

Infrastructure has the same move. Default-deny egress on a namespace turns "this service can reach anything" into a loud, specific failure the first time something tries. It is annoying for a week and then it is a permanent boundary.

### Rung 3 → 4: make it impossible

The top rung is where the defect cannot be expressed in the language you have given yourself.

The canonical case is SQL injection. You do not solve it by training people to be careful with string concatenation. You solve it by making the unsafe path unreachable:

```go
// internal/db/db.go — the raw path is unexported
func rawQuery(q string) (*Rows, error) { ... }

// The only exported query function takes args separately.
func Query(tmpl Template, args ...any) (*Rows, error) { ... }
```

Now injection is not a thing to be careful about. It is a compile error in every package outside `internal/db`, and a reviewer who has never heard of SQL injection cannot let it through.

The same pattern generalises through the type system:

```rust
// Untrusted input cannot be confused with validated input,
// because they are not the same type.
struct RawInput(String);
struct SafePath(PathBuf);

fn validate(raw: RawInput, root: &Path) -> Result<SafePath, ValidationError> {
    let candidate = root.join(&raw.0).canonicalize()?;
    if !candidate.starts_with(root) {
        return Err(ValidationError::Escape);
    }
    Ok(SafePath(candidate))
}

// Every file operation demands SafePath. There is no way to pass
// RawInput here. Path traversal is now a type error.
fn read_user_file(p: SafePath) -> io::Result<Vec<u8>> { ... }
```

Path traversal used to be a class that produced findings every quarter. Now it produces compiler diagnostics, for free, forever, in code written by people who have never thought about it.

And then there is the biggest single instance of this move available to the industry: **memory safety**. Somewhere around two thirds to three quarters of severe vulnerabilities in large C and C++ codebases are memory-safety issues. That is not a class you can train away or scan away. It is a class you can move to rung four by changing language at the boundary — which is exactly what Android, Windows, and the Linux kernel have been doing, with published results showing new memory-safe code producing a fraction of the vulnerability density of the code it replaced.


## The rewrite objection

The immediate response to rung four is that it means rewrites, and rewrites do not get funded.

Mostly true, and mostly beside the point, because you do not need a rewrite. You need a **boundary**.

The rule that makes this tractable: *new code goes on the high rung; old code stays where it is and gets a clear edge drawn around it.*

- New services use the safe query API. Old ones get a scanner and a backlog.
- New parsers get written in a memory-safe language. The old parser gets fuzzed and sandboxed.
- New endpoints require a declared policy. Old ones get an allowlist that only shrinks.

This works because code has a half-life. A meaningful fraction of your codebase will be rewritten anyway in the normal course of shipping. If the default for new code is on rung four, your vulnerability density decays without anyone ever running a rewrite project.

The failure mode to watch is the allowlist that grows. Whatever form the boundary takes — an exception list, a legacy annotation, a grandfathered directory — it needs a ratchet. It can shrink, it cannot grow, and adding to it requires the same approval as any other risk acceptance. Which is the subject of the next post.

## Running this as practice

Two habits are enough to make this real.

**First: after every incident, ask the class question.** Not "how do we fix this bug" but "what rung is this class on, and what would it take to move it up one?" Put that in the postmortem template as a required field. It will be answered badly at first and then it will start being answered well.

**Second: cluster your backlog quarterly.** Take every security ticket from the last three months and group by shape, not by service. Any cluster with five or more members is not five tickets — it is one class with five symptoms. Close all five and open one ticket to climb a rung.

The cluster exercise is worth doing once just for the shock value. The first time I did it, about 60% of a quarter's security backlog collapsed into four classes. We had been paying to fix the same four things over and over, and the ticket system had been carefully hiding that from us by giving each symptom its own ID.

## The summary

Every vulnerability you fix by hand is a vulnerability you will fix again, because the conditions that produced it are still there and the code is still growing.

The only security work that compounds is the work that makes a category of defect harder to write than the correct alternative. Everything else is maintenance — necessary, but it does not accumulate, and it scales with your engineering headcount rather than against it.

Ask the class question. Draw the boundary. Let the ratchet do the rest.
