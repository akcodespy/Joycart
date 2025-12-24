UPDATE orders
SET shipping_address = '{
  "name": "user1",
  "phone": "9999999999",
  "address_line1": "user1road",
  "address_line2": "",
  "city": "user1city",
  "state": "user1state",
  "pincode": "999999"
}'
WHERE id = 1;

