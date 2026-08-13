# Buy Now test structure

Buy Now coverage follows the business hierarchy:

```text
buy_flow/
|-- user/
|   |-- used_car/
|   |   |-- test_paygent.py
|   |   `-- test_bank_transfer.py
|   `-- new_car/
|       `-- test_paygent.py
`-- dealer/
    |-- used_car/
    `-- new_car/
```

Each payment method is an independent pytest test module so failures and
automatic reruns remain isolated. Dealer packages are prepared for future
coverage but intentionally contain no tests yet.
