-- adding sample data

--Add 10 popular programming books
INSERT INTO books (isbn, title, author, price, stock) VALUES
('978-0132350884', 'Clean Code', 'Robert C. Martin', 35.99, 15),
('978-0201633610', 'Design Patterns', 'Erich Gamma', 45.50, 8),
('978-0134685991', 'Effective Java', 'Joshua Bloch', 42.99, 12),
('978-0321125217', 'Domain-Driven Design', 'Eric Evans', 38.75, 5),
('978-0135957059', 'The Pragmatic Programmer', 'Andrew Hunt', 39.99, 3),
('978-1491950357', 'Building Microservices', 'Sam Newman', 34.99, 10),
('978-1617293290', 'Spring in Action', 'Craig Walls', 44.99, 7),
('978-0134093413', 'Clean Architecture', 'Robert C. Martin', 37.99, 9),
('978-1119067900', 'Python Crash Course', 'Eric Matthes', 29.99, 20),
('978-0596007126', 'Head First Design Patterns', 'Eric Freeman', 47.99, 6);

-- Add 6 library customers
INSERT INTO customers (name, email, phone) VALUES
('Alice Johnson', 'alice@email.com', '555-0101'),
('Bob Smith', 'bob@email.com', '555-0102'),
('Carol Davis', 'carol@email.com', '555-0103'),
('David Wilson', 'david@email.com', '555-0104'),
('Eva Brown', 'eva@email.com', '555-0105'),
('Frank Miller', 'frank@email.com', '555-0106');

-- Create 4 sample orders
INSERT INTO orders (customer_id, status, total_amount) VALUES
(1, 'completed', 71.98),  
(2, 'completed', 45.50),   
(3, 'pending', 119.97),    
(4, 'completed', 85.49);   

-- Add books to each order
INSERT INTO order_items (order_id, isbn, quantity, unit_price) VALUES
(1, '978-0132350884', 2, 35.99),           
(2, '978-0201633610', 1, 45.50),          
(3, '978-0135957059', 3, 39.99),           
(4, '978-0134685991', 1, 42.99),           
(4, '978-0596007126', 1, 47.99);           