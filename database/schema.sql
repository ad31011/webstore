-- ===== ROLET DHE PËRDORUESIT =====
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL          -- admin, advanced, simple
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===== TABELAT NDIHMËSE (LOOKUP) =====
CREATE TABLE genders    (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL);
CREATE TABLE categories (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL);
CREATE TABLE brands     (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL);
CREATE TABLE sizes      (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL);
CREATE TABLE colors     (id SERIAL PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL);

-- ===== PRODUKTET =====
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    initial_quantity INT NOT NULL DEFAULT 0 CHECK (initial_quantity >= 0),
    gender_id   INT REFERENCES genders(id),
    category_id INT REFERENCES categories(id),
    brand_id    INT REFERENCES brands(id),
    color_id    INT REFERENCES colors(id),
    size_id     INT REFERENCES sizes(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===== ZBRITJET =====
CREATE TABLE discounts (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    percentage NUMERIC(5,2) NOT NULL CHECK (percentage > 0 AND percentage <= 100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    CHECK (end_date >= start_date)
);

-- ===== KLIENTËT =====
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(30),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===== POROSITË =====
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL REFERENCES clients(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','confirmed','shipped','delivered','cancelled')),
    total_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL          -- çmimi në momentin e blerjes
);

CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_orders_status ON orders(status);

-- ===== RAPORTET (VIEWS) =====
CREATE VIEW daily_earnings AS
SELECT DATE(o.created_at) AS day,
       COUNT(DISTINCT o.id) AS orders_count,
       SUM(oi.quantity) AS items_sold,
       SUM(oi.quantity * oi.unit_price) AS earnings
FROM orders o JOIN order_items oi ON oi.order_id = o.id
WHERE o.status IN ('confirmed','shipped','delivered')
GROUP BY DATE(o.created_at);

CREATE VIEW monthly_earnings AS
SELECT TO_CHAR(DATE_TRUNC('month', o.created_at), 'YYYY-MM') AS month,
       COUNT(DISTINCT o.id) AS orders_count,
       SUM(oi.quantity) AS items_sold,
       SUM(oi.quantity * oi.unit_price) AS earnings
FROM orders o JOIN order_items oi ON oi.order_id = o.id
WHERE o.status IN ('confirmed','shipped','delivered')
GROUP BY 1;

CREATE VIEW top_selling_products AS
SELECT p.id AS product_id, p.name,
       SUM(oi.quantity) AS total_sold,
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN products p ON p.id = oi.product_id
WHERE o.status IN ('confirmed','shipped','delivered')
GROUP BY p.id, p.name;

-- ===== TË DHËNA FILLESTARE =====
INSERT INTO roles (name) VALUES ('admin'), ('advanced'), ('simple');
INSERT INTO genders (name) VALUES ('Men'), ('Women'), ('Children');
INSERT INTO categories (name) VALUES ('Shirts'), ('Pants'), ('Jackets'), ('T-Shirts');
INSERT INTO brands (name) VALUES ('Nike'), ('Adidas'), ('Zara'), ('Tommy Hilfiger');
INSERT INTO sizes (name) VALUES ('S'), ('M'), ('L'), ('XL');
INSERT INTO colors (name) VALUES ('Red'), ('Black'), ('White'), ('Blue');

INSERT INTO products (name, description, price, initial_quantity, gender_id, category_id, brand_id, color_id, size_id) VALUES
('Nike T-Shirt', 'Bluzë pambuku', 25.00, 100, 1, 4, 1, 3, 3),
('Adidas Jacket', 'Xhaketë sportive', 120.00, 30, 1, 3, 2, 2, 3),
('Zara Pants', 'Pantallona elegante', 45.00, 50, 2, 2, 3, 4, 2),
('Tommy Hilfiger Shirt', 'Këmishë e kuqe', 60.00, 40, 2, 1, 4, 1, 2),
('Kids Nike Jacket', 'Xhaketë për fëmijë', 35.00, 0, 3, 3, 1, 4, 1);

INSERT INTO discounts (product_id, percentage, start_date, end_date)
VALUES (4, 20, CURRENT_DATE, CURRENT_DATE + 30);

INSERT INTO clients (first_name, last_name, email, phone, address) VALUES
('Arta', 'Krasniqi', 'arta@mail.com', '044111222', 'Prishtinë'),
('Blerim', 'Hoxha', 'blerim@mail.com', '070333444', 'Tetovë');

INSERT INTO orders (client_id, status, total_amount, created_at) VALUES
(1, 'confirmed', 715.00, NOW()),
(2, 'delivered', 120.00, NOW() - INTERVAL '2 days'),
(1, 'pending',   60.00,  NOW());

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 25, 25.00), (1, 3, 2, 45.00),
(2, 2, 1, 120.00),
(3, 4, 1, 60.00);