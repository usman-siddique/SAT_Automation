# Buy Now test structure

Buy Now coverage follows the business hierarchy:

```text
buy_flow/
|-- user/
|   |-- used_car/
|   |   |-- test_paygent.py
|   |   `-- test_bank_transfer.py
|   `-- new_car/
|       |-- test_paygent.py
|       `-- test_bank_transfer.py
`-- dealer/
    |-- used_car/
    `-- new_car/
```

Each payment method is an independent pytest test module so failures and
automatic reruns remain isolated. Dealer packages are prepared for future
coverage but intentionally contain no tests yet.

## Implemented User flows

| Vehicle | Payment | Distinguishing make | Final checks |
|---|---|---|---|
| Used Car | Paygent | Volkswagen | Successful order and total-price behavior |
| Used Car | Bank Transfer | Daihatsu | Payment Pending, invoice/proof behavior, and Ask handling |
| New Car | Paygent | Nissan | Partial Payment, matching car price, Shipping Ask, Total Ask |
| New Car | Bank Transfer | Honda | Pending, matching car price, Shipping Ask, Total Ask, proof action, and bank details |

Both New Car flows validate the selected variant and its features from the
details page through checkout. The car price is carried to payment and the
final order summary. Environment domains come from the runtime `BASE_URL`;
test navigation never hardcodes Sprint or Development.

The shared site navigation detects transient homepage HTTP 500 responses and
retries up to three times. It also returns profile/dashboard redirects to the
public homepage before selecting New Cars from the navigation menu.
