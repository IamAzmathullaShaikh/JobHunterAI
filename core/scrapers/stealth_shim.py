# scrapers/stealth_shim.py
try:
    from playwright_stealth import stealth as stealth_sync
except Exception:
    stealth_sync = None

def stealth_async(page):
    """
    Backwards-compatible shim: call the available stealth function or no-op.
    """
    if stealth_sync:
        stealth_sync(page)
    else:
        # no-op; manual patching should be applied by scraper if needed
        return
