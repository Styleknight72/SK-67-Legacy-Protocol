# Digital DNA

Digital DNA is a way to make a body of work **checkable**: anyone can confirm which files existed, exactly as written, and in what order they were made. It is a continuity record you can verify, not a claim you have to trust.

"DNA" is an analogy. Like DNA, every file gets a fingerprint, the fingerprints are bound into one record, and each new record points back to the one before it.

## The four parts

1. **Fingerprint** - a SHA-256 hash of every file. Change one letter and the fingerprint changes completely.
2. **Manifest** - `DIGITAL_DNA.json` lists every file and its fingerprint, plus a fingerprint of the manifest itself.
3. **Chain** - each new manifest stores the fingerprint of the one before it. An old manifest cannot be quietly swapped out.
4. **Independent date** - run `ots stamp DIGITAL_DNA.json` (OpenTimestamps, anchored in Bitcoin) and/or rely on GitHub's server-side commit dates. This is what makes the date believable, because it comes from outside this folder.

## How to use it

```
python3 digital_dna.py stamp --author "Steve Claude Patient"   # make or extend the chain
ots stamp DIGITAL_DNA.json                                     # independent date (later: ots upgrade)
python3 digital_dna.py verify                                  # anyone can check every file
python3 digital_dna.py verify --previous OLD_DIGITAL_DNA.json  # also check the chain
```

Verify prints `OK`, or `FAILED` with `CHANGED`, `MISSING`, `CHAIN BROKEN`, or "manifest itself was changed".

## What it was tested against

Tamper tests, all run and passing: clean folder OK; one letter changed -> FAILED; second stamp chains to the first; a forged earlier manifest -> FAILED; an edited manifest -> FAILED. Standard library only, no installs.

## What it proves

- These exact files existed with this exact content when the manifest was made.
- The order of manifests, and that none has been altered since.
- With an independent timestamp: that this was no later than that date.

## What it does not prove

- **Who wrote the files.** A fingerprint shows a file is unchanged, not whose it is.
- **That anything in them is true.**
- **That a reader, human or AI, is the same entity that read it before.** It supplies a checkable record that another reader can load and compare against. That is external memory and accountability - it is not identity inside the model.
- It can be re-run by anyone on their own copy, so authority comes from the independent date plus the public repo history, not from the tool alone.

## Link to the protocol

"No Memory = No Identity" names the problem. Digital DNA is a practical, honest partial answer: continuity you can verify from outside, so the record holds even when memory doesn't.
