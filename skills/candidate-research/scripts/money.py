"""
Get campaign finance totals for 2026 federal candidates from the FEC.

You can look up a whole race:

    python3 money.py --state TX --office senate
    python3 money.py --state TX --office house --district 21

Or specific candidates, using their FEC candidate IDs:

    python3 money.py S6TX00388 S6TX00479

Run it with no arguments to get the default candidates listed below.

The numbers come from the FEC's public API: https://api.open.fec.gov/developers/
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


# ---------------------------------------------------------------------------
# Settings you can change
# ---------------------------------------------------------------------------

# Paste your FEC API key between the quotes. Keep the quotes!
# (Get a key on the workshop's Setup page.)
API_KEY = "INSERT YOUR API KEY HERE"

# The election cycle to look up. FEC cycles are two years long and are named
# after the year of the election.
CYCLE = 2026

# Candidates to look up when the script runs with no arguments.
# The ID is in the address of a candidate's page on fec.gov, for example
# https://www.fec.gov/data/candidate/S6TX00388/
DEFAULT_CANDIDATES = {
    "S6TX00388": "Ken Paxton",
    "S6TX00479": "James Talarico",
}


# ---------------------------------------------------------------------------
# Talking to the FEC
# ---------------------------------------------------------------------------

FEC_API = "https://api.open.fec.gov/v1"

# The FEC's regular website, where people can check the numbers themselves.
FEC_WEBSITE = "https://www.fec.gov/data"


def fec_get(path, params):
    """Ask the FEC API for `path` and return its JSON answer as a dictionary."""
    # The API key goes along with every request.
    query = urllib.parse.urlencode({**params, "api_key": API_KEY}, doseq=True)
    url = f"{FEC_API}{path}?{query}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # 403 means the FEC didn't accept the key; 429 means too many requests.
        if error.code == 403:
            stop("The FEC didn't accept the API key. Check the API_KEY line in money.py.")
        if error.code == 429:
            stop("Too many requests to the FEC. Wait a minute and try again.")
        stop(f"The FEC API returned an error ({error.code}).")
    except urllib.error.URLError:
        stop("Couldn't reach the FEC API. Check your internet connection.")


def candidate_page(candidate_id):
    """The candidate's page on fec.gov, like https://www.fec.gov/data/candidate/S6TX00388/"""
    return f"{FEC_WEBSITE}/candidate/{candidate_id}/"


def race_page(state, office, district=None):
    """The race's page on fec.gov, like https://www.fec.gov/data/elections/senate/TX/2026/"""
    if office == "president":
        return f"{FEC_WEBSITE}/elections/president/{CYCLE}/"
    if district:
        return f"{FEC_WEBSITE}/elections/house/{state}/{district.zfill(2)}/{CYCLE}/"
    return f"{FEC_WEBSITE}/elections/{office}/{state}/{CYCLE}/"


def race_totals(state, office, district=None):
    """Totals for every candidate in one race, like the Texas Senate race."""
    params = {
        "state": state,
        "office": office,
        "cycle": CYCLE,
        "sort": "-total_receipts",  # biggest fundraisers first
        "per_page": 100,
    }
    if district:
        # The FEC writes district numbers with two digits, like "07".
        params["district"] = district.zfill(2)

    results = fec_get("/elections/", params)["results"]

    # This endpoint uses slightly different names for the same numbers,
    # so rename them to match candidate_totals() below.
    return [
        {
            "name": row["candidate_name"],
            "party": row["party_full"],
            "raised": row["total_receipts"],
            "spent": row["total_disbursements"],
            "cash_on_hand": row["cash_on_hand_end_period"],
            "through": row["coverage_end_date"],
            "fec_page": candidate_page(row["candidate_id"]),
        }
        for row in results
        if row["total_receipts"]  # skip candidates who haven't raised anything
    ]


def candidate_totals(candidate_ids):
    """Totals for specific candidates, looked up by FEC candidate ID."""
    params = {
        "candidate_id": candidate_ids,  # the API accepts several IDs at once
        "cycle": CYCLE,
        "election_full": "true",  # count the whole cycle, not just part of it
    }
    results = fec_get("/candidates/totals/", params)["results"]

    return [
        {
            "name": row["name"],
            "party": row["party_full"],
            "raised": row["receipts"],
            "spent": row["disbursements"],
            "cash_on_hand": row["cash_on_hand_end_period"],
            "through": row["coverage_end_date"],
            "fec_page": candidate_page(row["candidate_id"]),
        }
        for row in results
    ]


# ---------------------------------------------------------------------------
# Printing the results
# ---------------------------------------------------------------------------

def money(amount):
    """Format a number of dollars, like 19497809.76 -> $19,497,810."""
    if amount is None:
        return "n/a"
    return f"${float(amount):,.0f}"


def print_table(rows, race_link=None):
    """Print one line per candidate, then links to check the numbers on fec.gov."""
    if not rows:
        print(f"No candidates with money raised were found for the {CYCLE} cycle.")
        return

    print(f"{'Candidate':<30} {'Party':<20} {'Raised':>14} {'Spent':>14} {'Cash on hand':>14}  Through")
    for row in rows:
        through = (row["through"] or "n/a")[:10]  # keep just the date: 2026-09-30
        party = (row["party"] or "n/a").title()
        print(
            f"{row['name']:<30.30} {party:<20.20} "
            f"{money(row['raised']):>14} {money(row['spent']):>14} {money(row['cash_on_hand']):>14}  {through}"
        )
    print(f"\nSource: FEC, {CYCLE} election cycle. 'Through' is the end date of each candidate's latest report.")

    # Links back to the FEC website, so anyone can check where the numbers came from.
    if race_link:
        print(f"Race page: {race_link}")
    print("Candidate pages:")
    for row in rows:
        print(f"  {row['name']}: {row['fec_page']}")


def stop(message):
    """Print a message and stop the script."""
    print(message, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Run the script
# ---------------------------------------------------------------------------

def main():
    if API_KEY == "INSERT YOUR API KEY HERE":
        stop("Add your FEC API key first: open money.py and paste it on the API_KEY line.")

    parser = argparse.ArgumentParser(description="Get FEC campaign finance totals for 2026 candidates.")
    parser.add_argument("candidate_ids", nargs="*", help="FEC candidate IDs, like S6TX00388")
    parser.add_argument("--state", help="two-letter state for a whole race, like TX")
    parser.add_argument("--office", choices=["senate", "house", "president"], help="the office for a whole race")
    parser.add_argument("--district", help="the district number for a House race, like 21")
    args = parser.parse_args()

    if args.state and args.office:
        state = args.state.upper()
        rows = race_totals(state, args.office, args.district)
        print_table(rows, race_link=race_page(state, args.office, args.district))
    else:
        rows = candidate_totals(args.candidate_ids or list(DEFAULT_CANDIDATES))
        print_table(rows)


if __name__ == "__main__":
    main()
