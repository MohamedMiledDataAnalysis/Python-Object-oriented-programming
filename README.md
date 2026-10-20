# Object-oriented programming in Python: a bank as a worked example

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)

One Python script that reviews the basics of object-oriented programming
(OOP) through a single real example: a small bank with current and
savings accounts.

```bash
python oop_bank.py
```

No package to install: the script uses only the Python standard library.
It prints 13 numbered sections. Each number matches a comment block in
the code and a section of this README.

---

## Contents

- [Why object-oriented programming?](#why-object-oriented-programming)
- [The example: four classes](#the-example-four-classes)
- [The 13 concepts](#the-13-concepts)
  1. [Class and object](#1-class-and-object)
  2. [`__init__` and attributes](#2-__init__-and-attributes)
  3. [Methods](#3-methods)
  4. [Class attributes](#4-class-attributes)
  5. [Encapsulation and `@property`](#5-encapsulation-and-property)
  6. [Custom exceptions](#6-custom-exceptions)
  7. [Special methods](#7-special-methods)
  8. [Abstraction](#8-abstraction)
  9. [Inheritance and `super()`](#9-inheritance-and-super)
  10. [Method overriding](#10-method-overriding)
  11. [Composition](#11-composition)
  12. [Polymorphism](#12-polymorphism)
  13. [`@classmethod` and `@staticmethod`](#13-classmethod-and-staticmethod)
- [Summary table](#summary-table)
- [Comparison with R](#comparison-with-r)

---

## Why object-oriented programming?

Without objects, an account would be loose data plus separate functions:

```python
balance = 1000
balance = deposit(balance, 250)
balance = -999_999          # nothing prevents this
```

Any line of code can change the balance, and no rule is enforced.

OOP groups the **data** (the balance) with the **functions** that act on
it (deposit, withdraw) in one unit: an object. The data then changes only
through those functions, which apply the rules:

```python
account.deposit(250)        # checked: the amount must be positive
account.balance = -999_999  # refused: AttributeError
```

---

## The example: four classes

```
                 Account               abstract: the common base
                 (owner, balance, deposit, withdraw, transfer_to)
                    │
          ┌─────────┴──────────┐
          │                    │
   CurrentAccount        SavingsAccount
   overdraft             no overdraft
   monthly fee           monthly interest


   Bank ─── holds ───> Account, Account, Account...
```

| Class | Role |
|---|---|
| `Account` | what every account has and does; cannot be used on its own |
| `CurrentAccount` | an everyday account: agreed overdraft, £3 monthly fee |
| `SavingsAccount` | no overdraft, monthly interest |
| `Bank` | holds the accounts and runs the month-end processing |
| `InsufficientFunds` | the error raised when a withdrawal breaks the limit |

---

## The 13 concepts

### 1. Class and object

A **class** is a template. An **object** (or instance) is one thing built
from it.

```python
alice = CurrentAccount("Alice", 1_000)
bob = SavingsAccount("Bob", 5_000, annual_rate=0.05)
```

`CurrentAccount` is the class; `alice` is an object of that class. A class
is written once; any number of objects can be created from it, each with
its own data.

### 2. `__init__` and attributes

`__init__` runs automatically each time an object is created. It sets up
the object's data.

```python
def __init__(self, owner: str, opening_balance: float = 0.0):
    self.owner = owner
    self._balance = opening_balance
```

- `self` is the object being created. Python passes it automatically:
  you write `CurrentAccount("Alice", 1_000)`, not
  `CurrentAccount(self, "Alice", 1_000)`.
- `self.owner = owner` stores a value **inside** the object. This is an
  **instance attribute**: each account has its own owner.

```python
alice.owner      # 'Alice'
bob.owner        # 'Bob'
```

### 3. Methods

A **method** is a function defined inside a class. It receives the object
as `self`, so it can read and change that object's attributes.

```python
def deposit(self, amount: float) -> None:
    if amount <= 0:
        raise ValueError("A deposit must be positive")
    self._balance += amount
```

```python
alice.deposit(250)      # Python runs deposit(alice, 250)
```

`transfer_to()` shows two objects working together: one account calls
the methods of another.

```python
def transfer_to(self, other, amount):
    self.withdraw(amount)     # raises an error before any money moves
    other.deposit(amount)
```

### 4. Class attributes

An attribute defined in the class, outside any method, belongs to the
**class**: all objects share the same value.

```python
class Account(ABC):
    bank_code = "MM-BANK"
    _next_number = 1001
```

| | Instance attribute | Class attribute |
|---|---|---|
| Defined | in `__init__`, with `self.` | in the class body |
| Values | one per object | one for the whole class |
| Example | `alice.owner` | `Account.bank_code` |

`_next_number` gives each account a unique number: each new account takes
the current value, then increases the class counter by 1.

### 5. Encapsulation and `@property`

**Encapsulation** means hiding an object's internal data and allowing
changes only through its methods.

```python
self._balance = opening_balance
```

The leading underscore in `_balance` is a convention meaning "internal:
do not use from outside". Python does not block access, but the
convention is respected.

To let users **read** the balance without being able to **set** it, the
class defines a property:

```python
@property
def balance(self) -> float:
    return round(self._balance, 2)
```

`@property` turns the method into an attribute you read without
parentheses:

```python
alice.balance             # 1150: calls the method
alice.balance = 1_000_000
# AttributeError: property 'balance' of 'CurrentAccount' object has no setter
```

The balance can now change only through `deposit()` and `withdraw()`, so
the rules always apply.

`history` works the same way, and returns a **copy** of the list: a
caller who modifies the copy cannot alter the real history.

### 6. Custom exceptions

A class that inherits from `Exception` is a new kind of error:

```python
class InsufficientFunds(Exception):
    """Raised when a withdrawal would take an account below its limit."""
```

The caller can then react to this problem specifically:

```python
try:
    bob.withdraw(10_000)
except InsufficientFunds as error:
    print("InsufficientFunds:", error)
```

A specific error type is more useful than a generic `ValueError`: the
code can treat "not enough money" differently from "invalid amount".

### 7. Special methods

Methods whose names start and end with two underscores (`__str__`,
"dunder" methods) are called by Python automatically for built-in
operations.

| Method | Called by | In the bank |
|---|---|---|
| `__init__` | `CurrentAccount(...)` | sets up the account |
| `__str__` | `print(acc)`, `str(acc)` | `CurrentAccount 1001 (Alice): -350.00` |
| `__repr__` | the console, lists | `CurrentAccount(owner='Alice', balance=-350)` |
| `__eq__` | `acc1 == acc2` | same account number |
| `__lt__` | `acc1 < acc2`, `sorted()` | lower balance |
| `__hash__` | sets, dictionary keys | the account number |
| `__len__` | `len(bank)` | number of accounts |
| `__iter__` | `for acc in bank:` | loops over the accounts |

- `__str__` is for users: readable.
- `__repr__` is for developers: precise. Python shows it inside lists,
  which is why `sorted(bank)` displays the `__repr__` form.
- Defining `__eq__` removes Python's default `__hash__`, so the class
  defines one again; otherwise accounts could not go into a set.

### 8. Abstraction

`Account` describes what every account has, but no real account is just
an "account": it is a current account or a savings account.

```python
from abc import ABC, abstractmethod

class Account(ABC):

    @abstractmethod
    def overdraft_limit(self) -> float:
        """How far below zero the balance may go."""

    @abstractmethod
    def month_end(self) -> None:
        """What happens to this account at the end of each month."""
```

- `ABC` (Abstract Base Class) marks `Account` as abstract.
- `@abstractmethod` declares a method with no code: every child class
  **must** define it.
- An abstract class cannot be created:

```
Account('Nobody')
TypeError: Can't instantiate abstract class Account without an
implementation for abstract methods 'month_end', 'overdraft_limit'
```

If a new account type forgets to define `month_end()`, Python refuses
to create it. The mistake appears immediately, not at the first month end.

### 9. Inheritance and `super()`

```python
class CurrentAccount(Account):
```

`CurrentAccount` **inherits** from `Account`: it receives every attribute
and method of `Account`, and adds or changes only what is specific to it.
`deposit()`, `withdraw()`, `balance` and `transfer_to()` are written once,
in `Account`, and work for every account type.

```python
def __init__(self, owner, opening_balance=0.0, overdraft=500.0):
    super().__init__(owner, opening_balance)
    self.overdraft = overdraft
```

- `super()` refers to the parent class.
- `super().__init__(...)` runs `Account.__init__`, which sets the owner,
  balance, history and number.
- The child then adds its own attribute, `overdraft`.
- Without the `super()` call, the attributes set by the parent would not
  exist, and `deposit()` would fail.

```python
isinstance(bob, SavingsAccount)   # True
isinstance(bob, Account)          # True: a SavingsAccount IS an Account
```

### 10. Method overriding

A child class **overrides** a method by defining it again. Python then
uses the child's version.

```python
class CurrentAccount(Account):
    def overdraft_limit(self) -> float:
        return self.overdraft            # e.g. 500

class SavingsAccount(Account):
    def overdraft_limit(self) -> float:
        return 0.0                       # never below zero
```

`withdraw()` is written once, in `Account`, and calls
`self.overdraft_limit()`. Each account type gets the right limit without
`withdraw()` knowing which type it is.

Overriding can also **extend** the parent's version with `super()`:

```python
class SavingsAccount(Account):
    def __str__(self) -> str:
        return f"{super().__str__()} at {self.annual_rate:.2%}"
```

`SavingsAccount 1002 (Bob): 5,000.00 at 5.00%`: the parent's text, plus
the interest rate.

### 11. Composition

A `Bank` is not an account: it **has** accounts. It holds `Account`
objects in a dictionary and works with them.

```python
class Bank:
    def __init__(self, name: str):
        self.name = name
        self._accounts: dict[int, Account] = {}

    def open(self, account: Account) -> Account:
        self._accounts[account.number] = account
        return account
```

The rule for choosing between inheritance and composition:

| Relationship | Use | Example |
|---|---|---|
| "is a" | inheritance | a `SavingsAccount` **is an** `Account` |
| "has a" | composition | a `Bank` **has** accounts |

### 12. Polymorphism

**Polymorphism** means: the same call does different things depending on
the object's class.

```python
def month_end(self) -> None:          # in Bank
    for acc in self._accounts.values():
        acc.month_end()
```

- For a `CurrentAccount`, `month_end()` charges the £3 fee.
- For a `SavingsAccount`, it adds the monthly interest.

Output of the demonstration (shortened):

```
CurrentAccount 1001 (Alice): -353.00         <- fee: 3.0
SavingsAccount 1002 (Bob): 4,016.67 at 5.00% <- interest: 16.67
CurrentAccount 1003 (Carol): 1,297.00        <- fee: 3.0
```

The `Bank` does not test the account type. To add a new type, such as a
business account, you write the new class; `Bank` does not change.

Without polymorphism, `Bank` would need a test for each type, edited
every time a type is added:

```python
if isinstance(acc, CurrentAccount):
    ...charge the fee...
elif isinstance(acc, SavingsAccount):
    ...add the interest...
```

### 13. `@classmethod` and `@staticmethod`

Normal methods receive the object (`self`). Two decorators change that:

| Decorator | Receives | Typical use |
|---|---|---|
| none | the object, `self` | most methods |
| `@classmethod` | the class, `cls` | another way to create objects |
| `@staticmethod` | nothing | a helper function that belongs to the class's topic |

```python
@classmethod
def from_records(cls, name: str, records: list[dict]) -> "Bank":
    bank = cls(name)
    ...
    return bank
```

`Bank.from_records(...)` builds a bank from records, such as rows read
from a CSV file. `cls(name)` is the same as `Bank(name)`, but also works
for a class that inherits from `Bank`.

```python
@staticmethod
def is_valid_sort_code(code: str) -> bool:
    parts = code.split("-")
    return len(parts) == 3 and all(
        p.isdigit() and len(p) == 2 for p in parts)
```

`Bank.is_valid_sort_code("12-34-56")` returns `True`. It needs neither a
bank nor the `Bank` class; it sits in the class because it belongs to the
banking topic.

---

## Summary table

| # | Concept | One-line definition | In the code |
|---|---|---|---|
| 1 | Class / object | template / one thing built from it | `CurrentAccount` / `alice` |
| 2 | `__init__` | runs when an object is created | sets owner, balance, number |
| 3 | Method | function that acts on the object | `deposit()`, `withdraw()` |
| 4 | Class attribute | shared by all objects | `bank_code`, `_next_number` |
| 5 | Encapsulation | data changes only through methods | `_balance` + `@property balance` |
| 6 | Custom exception | a new error type | `InsufficientFunds` |
| 7 | Special methods | called by Python operations | `__str__`, `__eq__`, `__lt__` |
| 8 | Abstraction | a base that cannot be used alone | `Account(ABC)`, `@abstractmethod` |
| 9 | Inheritance | a child reuses its parent | `CurrentAccount(Account)`, `super()` |
| 10 | Overriding | a child redefines a method | `overdraft_limit()`, `__str__` |
| 11 | Composition | an object holds other objects | `Bank` holds accounts |
| 12 | Polymorphism | same call, behaviour by class | `acc.month_end()` |
| 13 | Class / static methods | methods without `self` | `from_records()`, `is_valid_sort_code()` |

---

## Comparison with R

R has three object systems. R6 is the closest to Python classes.

| Python | R6 | S3 |
|---|---|---|
| `class Account:` | `Account <- R6Class("Account", ...)` | a list with `class(x) <- "account"` |
| `__init__` | `initialize = function(...)` | a constructor function |
| `self.owner` | `self$owner` | `x$owner` |
| method `deposit(self, ...)` | `public = list(deposit = function(...))` | generic `deposit.account <- function(x, ...)` |
| `_balance` (convention) | `private = list(balance = ...)` (enforced) | none |
| `@property` | `active = list(balance = function() ...)` | none |
| `class Savings(Account)` | `R6Class(..., inherit = Account)` | `class(x) <- c("savings", "account")` |
| `super().__init__()` | `super$initialize()` | `NextMethod()` |
| `__str__` | `print = function(...)` | `print.account <- function(x, ...)` |
| polymorphism | method lookup on the object | generic dispatch: `month_end(x)` |

One practical difference: R6 enforces private fields, while Python's
leading underscore is only a convention. Python relies on developers
respecting it.

---

## Project structure

```
oop-bank/
├── oop_bank.py     the script: classes, then the demonstration in main()
├── LICENSE
└── README.md
```

## Licence

MIT
