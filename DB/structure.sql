-- Crear las tablas
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();  -- Establece la nueva fecha y hora
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_customers_before_update
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Disparador para la tabla orders
CREATE TRIGGER update_orders_before_update
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();


-- Insertar datos en la tabla customers
INSERT INTO customers (name) VALUES
('Alice'),
('Bob'),
('Charlie'),
('David'),
('Eva');

-- Insertar datos en la tabla orders
INSERT INTO orders (customer_id) VALUES
((SELECT id FROM customers WHERE name = 'Alice')),
((SELECT id FROM customers WHERE name = 'Bob')),
((SELECT id FROM customers WHERE name = 'Charlie')),
((SELECT id FROM customers WHERE name = 'David')),
((SELECT id FROM customers WHERE name = 'Eva'));



select * from customers;
select * from orders;

select * from customers where id > 0;