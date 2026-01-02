
UPDATE orders
SET status = 'PLACED'
WHERE status = 'CANCELLED'

UPDATE order_items
SET status = 'PENDING'
WHERE status = 'CANCELLED'

DROP TABLE orders
DROP TABLE order_items
