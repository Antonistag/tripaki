"""Turns the user's free-text trip description into structured data."""
import json
import os

SYSTEM = """Extract trip parameters from the user's message. Reply with ONLY a JSON object:
{"origin": str|null, "destination": str|null, "nights": int|null,
 "total_budget_eur": number|null, "max_hotel_km_from_center": number|null,
 "interests": [str], "priority": "cheapest"|"fastest"|"balanced"}
Use null for anything not mentioned. Default priority is "balanced"."""


def parse_with_llm(text: str) -> dict:
    import anthropic  # needs ANTHROPIC_API_KEY in your environment

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": text}],
    )
    raw = msg.content[0].text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def ask_missing(trip: dict) -> dict:
    """Ask the user (in the terminal) for anything the parser could not find."""
    questions = {
        "origin": ("Where are you travelling from? ", str),
        "destination": ("Where do you want to go? ", str),
        "nights": ("How many nights? ", int),
        "total_budget_eur": ("Total budget in EUR? ", float),
        "max_hotel_km_from_center": ("Max km from city center for the hotel? ", float),
    }
    for key, (question, cast) in questions.items():
        while trip.get(key) in (None, ""):
            try:
                trip[key] = cast(input(question).strip())
            except ValueError:
                print("  Please enter a valid value.")
    trip.setdefault("interests", [])
    trip["priority"] = trip.get("priority") or "balanced"
    return trip


def parse_trip(text: str) -> dict:
    trip = {}
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            trip = parse_with_llm(text)
        except Exception as e:  # missing package, network, bad JSON...
            print(f"(AI parsing unavailable: {e}. Falling back to questions.)")
    else:
        print("(No ANTHROPIC_API_KEY set, so I'll ask you questions instead.)")
    return ask_missing(trip)


# ---------- Modifications after the first results ----------

MODIFY_SYSTEM = SYSTEM + """
You will receive the CURRENT trip as JSON and a requested change.
Return the full updated JSON, changing only what the user asked to change."""


def has_ai() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def modify_with_llm(trip: dict, change: str) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system=MODIFY_SYSTEM,
        messages=[{"role": "user", "content": f"CURRENT: {json.dumps(trip)}\nCHANGE: {change}"}],
    )
    raw = msg.content[0].text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def modify_manually(trip: dict) -> dict:
    """Show a numbered menu so the user picks what to change."""
    fields = [
        ("origin", "Origin", str),
        ("destination", "Destination", str),
        ("nights", "Nights", int),
        ("total_budget_eur", "Total budget (EUR)", float),
        ("max_hotel_km_from_center", "Max hotel km from center", float),
        ("priority", "Priority (cheapest / fastest / balanced)", str),
    ]
    print("\nWhat do you want to change?")
    for i, (key, label, _) in enumerate(fields, 1):
        print(f"  {i}. {label}: {trip[key]}")
    choice = input("Number (or Enter to cancel): ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(fields):
        return trip
    key, label, cast = fields[int(choice) - 1]
    while True:
        try:
            value = cast(input(f"New value for {label}: ").strip())
            if key == "priority" and value not in ("cheapest", "fastest", "balanced"):
                raise ValueError
            trip[key] = value
            return trip
        except ValueError:
            print("  Please enter a valid value.")


def modify_trip(trip: dict, change: str = "") -> dict:
    if has_ai() and change:
        try:
            return modify_with_llm(trip, change)
        except Exception as e:
            print(f"(AI unavailable: {e}. Using the menu instead.)")
    return modify_manually(trip)