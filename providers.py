"""Where trip data comes from.

Every provider implements the same two methods. To use real data, write a new
class (e.g. AmadeusProvider) with the same methods and swap it in main.py.
"""
import random
from dataclasses import dataclass


@dataclass
class Transport:
    mode: str          # "flight", "bus", "train"
    company: str
    price_eur: float   # ONE-WAY price
    hours: float       # door-to-door time, one way


@dataclass
class Hotel:
    name: str
    price_per_night: float
    km_from_center: float
    rating: float


class Provider:
    def search_transport(self, origin: str, destination: str) -> list[Transport]:
        raise NotImplementedError

    def search_hotels(self, destination: str) -> list[Hotel]:
        raise NotImplementedError


class MockProvider(Provider):
    """Fake but repeatable data, so you can test without any API."""

    def _rng(self, *parts):
        return random.Random("|".join(parts).lower())

    def search_transport(self, origin, destination):
        r = self._rng(origin, destination)
        return [
            Transport("flight", "BudgetAir", r.randint(30, 140), r.uniform(3, 6)),
            Transport("flight", "BigAirline", r.randint(110, 280), r.uniform(2, 4)),
            Transport("bus", "FlixBus", r.randint(25, 70), r.uniform(10, 24)),
            Transport("train", "NationalRail", r.randint(50, 150), r.uniform(6, 14)),
        ]

    def search_hotels(self, destination):
        r = self._rng(destination, "hotels")
        names = ["Hostel Central", "Hotel Sol", "City Inn", "Casa Blanca",
                 "Grand Plaza", "Budget Stay", "Old Town Lodge", "Riverside"]
        return [
            Hotel(n, r.randint(25, 160), round(r.uniform(0.2, 8), 1), round(r.uniform(6.5, 9.4), 1))
            for n in names
        ]
