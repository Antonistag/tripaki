# Trip Planner (starter)

## Run it
1. Install Python 3.10+.
2. `pip install -r requirements.txt`
3. (Optional, for AI understanding of free text) set your key:
   - Mac/Linux: `export ANTHROPIC_API_KEY=your-key`
   - Windows: `setx ANTHROPIC_API_KEY your-key`
4. `python main.py`

Without a key, the app simply asks you questions instead.

## Files
- `main.py`      the program you run
- `trip_parser.py` understands the trip description
- `providers.py` where flight/bus/hotel data comes from (currently fake)
- `planner.py`   combines options and ranks them

## Next steps
1. Replace `MockProvider` with a real one (flights first, e.g. Amadeus).
2. Add dates, so prices are real.
3. Add a web interface.
