from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
import json

views = Blueprint('views', __name__)

# Purchase prices (fixed)
purchase_prices = {
    "Pen": 5,
    "Pencil": 2,
    "Eraser": 1,
    "Sharpener": 2,
    "Geometry Box": 10
}

# Sales prices (different from purchase prices)
sales_prices = {
    "Pen": 7,
    "Pencil": 5,
    "Eraser": 3,
    "Sharpener": 5,
    "Geometry Box": 15
}

# Hardcoded inventory quantities (you can replace with DB)
inventory = [
    {"item": "Pen", "price": purchase_prices["Pen"], "quantity": 100},
    {"item": "Pencil", "price": purchase_prices["Pencil"], "quantity": 80},
    {"item": "Eraser", "price": purchase_prices["Eraser"], "quantity": 60},
    {"item": "Sharpener", "price": purchase_prices["Sharpener"], "quantity": 50},
    {"item": "Geometry Box", "price": purchase_prices["Geometry Box"], "quantity": 30},
]

@views.route('/')
@login_required
def home():
    # Get current amount from session or set default 1000
    current_amount = session.get('current_amount', 1000)
    return render_template("home.html", user=current_user, current_amount=current_amount)

@views.route('/view-cart')
@login_required
def view_cart():
    selected_items = session.get('selected_items', [])  # retrieve selected items
    return render_template('view_cart.html', inventory=inventory, selected_items=selected_items)

@views.route('/purchase', methods=['POST', 'GET'])
@login_required
def purchase():
    if request.method == 'POST':
        selected_items_json = request.form.get('selected_items')
        if not selected_items_json:
            items = session.get('selected_items', [])
            total = 0
            current_amount = session.get('current_amount', 1000)
            return render_template('purchase.html', items=items, total=total, current_amount=current_amount)

        items = json.loads(selected_items_json)

        total = 0
        for item in items:
            name = item['item']
            qty = int(item['qty'])
            price = purchase_prices.get(name, item.get('rate', 0))
            item['rate'] = price
            item['total'] = price * qty
            total += item['total']

        # Update current amount
        current_amount = session.get('current_amount', 1000)
        current_amount -= total
        session['current_amount'] = current_amount

        # Clear selected items after purchase, if you want:
        # session.pop('selected_items', None)

        return render_template('purchase.html', items=items, total=total, current_amount=current_amount)

    else:
        # GET request: load from session
        items = session.get('selected_items', [])
        total = 0
        for item in items:
            qty = int(item.get('qty', 1))
            price = purchase_prices.get(item['item'], item.get('rate', 0))
            item['rate'] = price
            item['total'] = price * qty
            total += item['total']

        current_amount = session.get('current_amount', 1000)
        return render_template('purchase.html', items=items, total=total, current_amount=current_amount)


@views.route('/sales', methods=['POST', 'GET'])
@login_required
def sales():
    if request.method == 'POST':
        selected_items_json = request.form.get('selected_items')
        if not selected_items_json:
            items = session.get('selected_items', [])
            total = 0
            current_amount = session.get('current_amount', 1000)
            return render_template('sales.html', items=items, total=total, current_amount=current_amount)

        items = json.loads(selected_items_json)

        total = 0
        for item in items:
            name = item['item']
            qty = int(item['qty'])
            sale_price = sales_prices.get(name, item.get('rate', 0))
            item['rate'] = sale_price
            item['total'] = sale_price * qty
            total += item['total']

        # Update current amount
        current_amount = session.get('current_amount', 1000)
        current_amount += total
        session['current_amount'] = current_amount

        # Clear selected items after sale, if you want:
        # session.pop('selected_items', None)

        return render_template('sales.html', items=items, total=total, current_amount=current_amount)

    else:
        # GET request: load from session
        items = session.get('selected_items', [])
        total = 0
        for item in items:
            qty = int(item.get('qty', 1))
            sale_price = sales_prices.get(item['item'], item.get('rate', 0))
            item['rate'] = sale_price
            item['total'] = sale_price * qty
            total += item['total']

        current_amount = session.get('current_amount', 1000)
        return render_template('sales.html', items=items, total=total, current_amount=current_amount)
    
    
@views.route('/select-item', methods=['POST'])
@login_required
def select_item():
    item_id = int(request.form.get('item_id'))
    action = request.form.get('action')

    # Map IDs to inventory items
    inventory_items = [
        {'id': 1, 'item': 'Pen', 'qty': 1, 'rate': purchase_prices['Pen']},
        {'id': 2, 'item': 'Pencil', 'qty': 1, 'rate': purchase_prices['Pencil']},
        {'id': 3, 'item': 'Eraser', 'qty': 1, 'rate': purchase_prices['Eraser']},
        {'id': 4, 'item': 'Sharpener', 'qty': 1, 'rate': purchase_prices['Sharpener']},
        {'id': 5, 'item': 'Geometry Box', 'qty': 1, 'rate': purchase_prices['Geometry Box']},
    ]

    item = next((i for i in inventory_items if i['id'] == item_id), None)

    if not item:
        flash("Invalid item selected", category='error')
        return redirect(url_for('views.view_cart'))

    selected_items = session.get('selected_items', [])

    # Check if item already selected; if yes, just update quantity
    existing = next((i for i in selected_items if i['item'] == item['item']), None)
    if existing:
        existing['qty'] = existing.get('qty', 1) + 1  # Increment quantity
        existing['rate'] = item['rate']
    else:
        selected_items.append(item)

    session['selected_items'] = selected_items

    if action == 'purchase':
        return redirect(url_for('views.purchase'))
    elif action == 'sale':
        return redirect(url_for('views.sales'))
    else:
        return redirect(url_for('views.view_cart'))

@views.route('/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    session.pop('selected_items', None)
    flash('Cart has been cleared!', category='success')
    return redirect(url_for('views.view_cart'))

@views.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    selected_items = request.json.get('items', [])
    session['selected_items'] = selected_items
    return {'message': 'Cart updated successfully'}

@views.route('/clear-cart/<page>')
@login_required
def clear_cart_from_page(page):
    session.pop('selected_items', None)
    if page == 'purchase':
        return redirect(url_for('views.purchase'))
    elif page == 'sales':
        return redirect(url_for('views.sales'))
    return redirect(url_for('views.view_cart'))