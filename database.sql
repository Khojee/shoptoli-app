-- User table to handle login credentials
CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

-- Customer table with more specific customer info, linked to a user
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES "user"(user_id),
    phone VARCHAR(50)
);

-- Address table, a customer can have multiple addresses
CREATE TABLE address (
    address_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customer(customer_id),
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL
);

-- Product table
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL
	image_file VARCHAR(50) NOT NULL DEFAULT 'default_product.png'
);

-- Order table
CREATE TABLE "order" (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customer(customer_id),
    address_id INT NOT NULL REFERENCES address(address_id),
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Changed from DATE
    total_amount DECIMAL(10, 2) NOT NULL
);

-- OrderItem table (junction table for many-to-many between Order and Product)
CREATE TABLE order_item (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES "order"(order_id),
    product_id INT NOT NULL REFERENCES product(product_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);