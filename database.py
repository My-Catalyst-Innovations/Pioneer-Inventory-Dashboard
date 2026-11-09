import streamlit as st
from datetime import datetime
from copy import deepcopy
from collections import defaultdict

# Fictional records only; each browser session has its own temporary state.
SEED = [
    dict(id=1, category='segment_mica', product='Sample segment sheet A', thickness='0.040 in', sheet_size='36 x 48 in', weight_per_sheet=4.5, current_stock=120, unit='sheets', low_stock_threshold=30),
    dict(id=2, category='molding_mica', product='Sample molding sheet B', thickness='0.025 in', sheet_size='36 x 48 in', weight_per_sheet=3.1, current_stock=18, unit='sheets', low_stock_threshold=25),
    dict(id=3, category='pei_tape', product='Sample insulating tape C', thickness=None, sheet_size=None, weight_per_sheet=None, current_stock=60, unit='rolls', low_stock_threshold=20),
    dict(id=4, category='cold_banding_tape', product='Sample banding tape D', thickness=None, sheet_size=None, weight_per_sheet=None, current_stock=35, unit='rolls', low_stock_threshold=10),
    dict(id=5, category='brazing_wire', product='Sample wire E', thickness=None, sheet_size=None, weight_per_sheet=None, current_stock=75, unit='spools', low_stock_threshold=15),
]

def _init():
    if 'demo_inventory' not in st.session_state: st.session_state.demo_inventory = deepcopy(SEED)
    if 'demo_requests' not in st.session_state: st.session_state.demo_requests = []

def get_all_inventory():
    _init(); return deepcopy(st.session_state.demo_inventory)

def get_inventory_summary():
    items=get_all_inventory(); requests=get_release_requests(); groups=defaultdict(lambda: {'count':0,'total_stock':0})
    for item in items:
        group=groups[item['category']]; group['count']+=1; group['total_stock']+=item['current_stock']
    return dict(total_items=len(items), low_stock_count=sum(i['current_stock']<=i['low_stock_threshold'] for i in items), total_sheets=sum(i['current_stock'] for i in items), pending_requests=sum(r['status']=='pending' for r in requests), category_breakdown=[dict(category=k, **v) for k,v in groups.items()])

def get_release_requests(status_filter=None, limit=100):
    _init(); rows=st.session_state.demo_requests
    return deepcopy([r for r in reversed(rows) if not status_filter or r['status']==status_filter][:limit])

def get_recent_release_requests(limit=10): return get_release_requests(limit=limit)

def create_release_request(inventory_item_id, requested_by, requested_by_email, quantity, notes=None):
    _init(); item=next((x for x in st.session_state.demo_inventory if x['id']==inventory_item_id), None)
    if item is None or not isinstance(quantity, int) or quantity < 1 or quantity > item['current_stock']:
        return False, 'Invalid item or quantity.', None, None, None, None
    item['current_stock']-=quantity
    request_id=len(st.session_state.demo_requests)+1
    st.session_state.demo_requests.append(dict(id=request_id, requested_by=requested_by, requested_by_email=requested_by_email, quantity=quantity, notes=notes, status='pending', created_at=datetime.now(), product=item['product'], unit=item['unit'], category=item['category']))
    return True, 'Simulated request', request_id, item['product'], item['current_stock'], item['unit']
