import os
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

products = []


@app.route('/product', methods=['POST'])
def add_product():
    data = request.get_json()

    new_id = len(products) + 1

    product = {
        'id': new_id,
        'name': data['name'],
        'description': data['description'],
        'icon_path': None
    }

    products.append(product)

    return jsonify(product), 201


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    for product in products:
        if product['id'] == product_id:
            return jsonify(product)

    return jsonify({'error': f'Product with ID {product_id} not found'}), 404


@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()

    for i, product in enumerate(products):
        if product['id'] == product_id:
            if 'name' in data:
                product['name'] = data['name']
            if 'description' in data:
                product['description'] = data['description']

            return jsonify(product), 200

    return jsonify({'error': f'Product with ID {product_id} not found'}), 404


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    for i, product in enumerate(products):
        if product['id'] == product_id:
            deleted_product = products.pop(i)
            return jsonify(deleted_product), 200

    return jsonify({'error': f'Product with ID {product_id} not found'}), 404


@app.route('/products', methods=['GET'])
def get_all_products():
    return jsonify(products), 200


# загрузка иконки
@app.route('/product/<int:product_id>/image', methods=['POST'])
def upload_icon(product_id):
    for product in products:
        if product['id'] == product_id:
            file = request.files['icon']
            filename = f"{product_id}.jpg"
            icon_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(icon_path)

            product['icon_path'] = icon_path

            return jsonify(product), 200

    return jsonify({'error': f'Product with ID {product_id} not found'}), 404


# получение иконки
@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_icon(product_id):
    for product in products:
        if product['id'] == product_id:
            if product['icon_path']:
                return send_file(product['icon_path'], mimetype='image/jpeg')
            else:
                return jsonify({'error': 'Icon not found'}), 404

    return jsonify({'error': f'Product with ID {product_id} not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)