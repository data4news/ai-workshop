---
name: candidate-research
description: Looks up 2026 campaign finance totals (money raised, money spent, cash on hand) for federal candidates using FEC data. Use when the user asks how much candidates in a race have raised, wants a fundraising update on a candidate, or wants to compare candidates' money.
---

# Candidate Research

Get the numbers by running `scripts/money.py`, which is in the same folder as this file. Don't look the numbers up any other way, and don't estimate them.

## Steps

1. Work out what the user wants:
   - **A whole race**, like "the Texas Senate race": you need the two-letter state and the office (`senate`, `house` or `president`). House races also need a district number.
   - **Specific candidates**: you need their FEC candidate IDs. If the user doesn't name anyone, use the defaults in the script (Ken Paxton and James Talarico). If you don't know a candidate's ID, look up their race first and take the ID from those results.

2. Run the script from this skill's folder. Use `python3`, or `python` if `python3` isn't available.
   - Whole race: `python3 scripts/money.py --state TX --office senate`
   - House race: `python3 scripts/money.py --state TX --office house --district 21`
   - Specific candidates: `python3 scripts/money.py S6TX00388 S6TX00479`

3. If the script says the API key is missing or wasn't accepted, stop. Tell the user to open `scripts/money.py` and paste their FEC API key on the `API_KEY` line (the workshop's Setup page explains how to get one). Don't edit the key yourself.

4. Reply with:
   - A table with each candidate's name, party, money raised, money spent, cash on hand and the "through" date.
   - One or two sentences on what stands out, like who has raised the most or who has the most cash left.
   - A note that the numbers come from the FEC and are only as current as each candidate's latest report.
