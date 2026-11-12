# Buy Now test structure

Buy Now coverage follows the business hierarchy:

```text
buy_flow/
|-- user/
|   `-- used_car/
|       |-- test_paygent.py
|       |-- test_bank_transfer.py
|       `-- test_paypal.py
`-- dealer/
    `-- used_car/
```

Each payment method is an independent pytest test module so failures and
automatic reruns remain isolated. Dealer packages are prepared for future
coverage but intentionally contain no tests yet.

## Implemented User flows

| Vehicle | Payment | Distinguishing make | Final checks |
|---|---|---|---|
| Used Car | Paygent | Volkswagen | Successful order and total-price behavior |
| Used Car | Bank Transfer | Daihatsu | Payment Pending, invoice/proof behavior, and Ask handling |
| Used Car | PayPal | Suzuki | JPY conversion, sandbox approval, confirmation, and tracking |

New Cars are inquiry-only and intentionally excluded from Buy Now automation.
Environment domains come from the runtime `BASE_URL`; test navigation does not
hardcode an environment domain.

The shared site navigation detects transient homepage HTTP 500 responses and
retries up to three times. It also returns profile/dashboard redirects to the
public homepage before continuing navigation.

## Role sessions

User tests keep the existing `page` fixture and share only the User browser
context. Future Dealer tests must request `dealer_page`, which uses a completely
separate cookie and local-storage context. Public tests use `page_no_login`, a
fresh anonymous context for every test. This makes full-suite execution order
independent and prevents one role's login from replacing another role's session.
