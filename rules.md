# Application Domain Rules

This document is the source of truth for your TDD loop. Fill in each section **before** you write any code — every rule you write here becomes at least one test.

There are no wrong answers, but there are inconsistent ones. Once you decide a rule, your code has to match it.

---

## 1. Currency Symbol

*What currency does your application use, and how is money formatted when it's displayed?*

> _Your answer:
Currency symbol: $
Money is displayed with 2 decimal places (e.g., $25.50).
---

## 2. Standard Categories

*Which expense categories are allowed? Limit yourself to 3–5. What happens if someone uses a category that isn't on your list?*

> _Your answer:_
Allowed categories:
Food
Transport
Utilities
Entertainment
Other
If a user provides a category that is not on this list, the application raises a ValueError and does not record the expense.
---

## 3. Overspending Behaviour (Total Balance)

*What happens when an expense is larger than the total balance? Does your app allow the balance to go negative, or does it block the transaction? If it blocks, what does the caller get back?*

> _Your answer:_
If an expense is greater than the available account balance, the transaction is blocked and the application raises an InsufficientFundsError. The account balance remains unchanged.
---

## 4. Budget Limits (Category Budgets)

*What happens when an expense exceeds a category's budget limit, but the balance could still cover it? Is it blocked, or is it recorded with a warning?*

> _Your answer:_
If an expense exceeds the budget limit for its category, the transaction is still recorded as long as there is enough money in the account. The application returns or stores a budget warning indicating that the category budget has been exceeded.
---

## TDD Blueprint

Now turn each rule above into the test you will write **before** the implementation exists. Name the behaviour you'd assert.

[ ] Rule 1 (Currency) → Test that money is displayed using $ with two decimal places (e.g., $100.00).
[ ] Rule 2 (Categories) → Test that valid categories are accepted and an invalid category raises a ValueError.
[ ] Rule 3 (Overspending) → Test that attempting to spend more than the account balance raises InsufficientFundsError and leaves the balance unchanged.
[ ] Rule 4 (Budget Limits) → Test that an expense exceeding the category budget is recorded successfully and generates a budget warning.
