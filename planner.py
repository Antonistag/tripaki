"""Combines transport + hotel options into ranked complete plans."""
from dataclasses import dataclass
from providers import Hotel, Provider, Transport

# How much each factor matters (price vs time) for each priority.
WEIGHTS = {"cheapest": (0.9, 0.1), "fastest": (0.2, 0.8), "balanced": (0.6, 0.4)}


@dataclass
class Plan:
    transport: Transport
    hotel: Hotel
    total_cost: float
    score: float


def _norm(value, low, high):
    return 0.0 if high == low else (value - low) / (high - low)


def build_plans(trip: dict, provider: Provider) -> list[Plan]:
    transports = provider.search_transport(trip["origin"], trip["destination"])
    hotels = [
        h for h in provider.search_hotels(trip["destination"])
        if h.km_from_center <= trip["max_hotel_km_from_center"]
    ]
    if not transports or not hotels:
        return []

    # Cheapest hotel that fits the distance limit (simple v1 rule).
    # A better version would also weigh rating and distance.
    hotels.sort(key=lambda h: h.price_per_night)

    plans = []
    for t in transports:
        for h in hotels[:3]:
            cost = t.price_eur * 2 + h.price_per_night * trip["nights"]  # round trip
            if cost <= trip["total_budget_eur"]:
                plans.append(Plan(t, h, cost, 0.0))

    if not plans:
        return []

    w_price, w_time = WEIGHTS[trip["priority"]]
    costs = [p.total_cost for p in plans]
    times = [p.transport.hours for p in plans]
    for p in plans:
        p.score = (w_price * _norm(p.total_cost, min(costs), max(costs))
                   + w_time * _norm(p.transport.hours, min(times), max(times)))
    return sorted(plans, key=lambda p: p.score)
