"""Run with:  python main.py"""
from trip_parser import parse_trip, modify_trip, has_ai
from planner import build_plans
from providers import MockProvider  # swap for a real provider later


def show_results(trip, provider):
    print(f"\nPlanning: {trip['origin']} -> {trip['destination']}, "
          f"{trip['nights']} nights, budget €{trip['total_budget_eur']:.0f}, "
          f"priority: {trip['priority']}\n")

    plans = build_plans(trip, provider)
    if not plans:
        print("Nothing fits that budget. Try raising it or allowing a hotel farther from the center.\n")
        return

    for i, p in enumerate(plans[:3], 1):
        t, h = p.transport, p.hotel
        print(f"Option {i}: €{p.total_cost:.0f} total")
        print(f"  Travel: {t.mode} with {t.company}, €{t.price_eur:.0f} each way, ~{t.hours:.1f}h")
        print(f"  Stay:   {h.name}, €{h.price_per_night:.0f}/night, "
              f"{h.km_from_center} km from center, rating {h.rating}\n")


def main():
    provider = MockProvider()
    print("Describe your trip (where, budget, nights, hotel distance, interests):")
    trip = parse_trip(input("> "))

    while True:
        show_results(trip, provider)

        # Ask if the user wants to change anything, then search again.
        if has_ai():
            change = input("Want to change anything? Describe it, or press Enter to finish:\n> ").strip()
            if not change:
                break
            trip = modify_trip(trip, change)
        else:
            again = input("Want to change anything? (y/n) > ").strip().lower()
            if again not in ("y", "yes"):
                break
            trip = modify_trip(trip)

    print("Have a great trip!")


if __name__ == "__main__":
    main()