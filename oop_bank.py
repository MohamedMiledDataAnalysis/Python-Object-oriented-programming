"""
oop_bank.py
-----------
The basics of object-oriented programming (OOP) in Python, reviewed
through one real example: a small bank with current and savings accounts.

Run it:  python oop_bank.py
Each part of the demonstration prints what the concept does.

Concepts covered, in order:
     1. Class and object
     2. __init__ and attributes
     3. Methods
     4. Class attributes (shared by all objects)
     5. Encapsulation: protected attributes and @property
     6. Custom exceptions
     7. Special methods: __str__, __repr__, __eq__, __lt__
     8. Abstraction: abstract base class
     9. Inheritance and super()
    10. Method overriding
    11. Composition: an object made of other objects
    12. Polymorphism
    13. @classmethod and @staticmethod

The idea behind OOP: group DATA (an account's balance) together with the
FUNCTIONS that act on it (deposit, withdraw), so the data can only change
through rules you control.
"""

from abc import ABC, abstractmethod
from datetime import date


# =============================================================================
# 6. CUSTOM EXCEPTIONS
# A class can define a new kind of error. Inheriting from Exception makes it
# usable with `raise` and `except`. A specific error type lets the caller
# react to THIS problem only: `except InsufficientFunds:`.
# =============================================================================
class InsufficientFunds(Exception):
    """Raised when a withdrawal would take an account below its limit."""


# =============================================================================
# 8. ABSTRACTION: an abstract base class
# Account describes what EVERY account has and can do, without being a real
# account itself. ABC + @abstractmethod mean: Account() cannot be created,
# and every child class MUST define the abstract methods.
# =============================================================================
class Account(ABC):
    """Common base for all accounts. Not usable on its own."""

    # 4. CLASS ATTRIBUTES: defined in the class, outside any method.
    # Shared by ALL accounts; one value for the whole class.
    bank_code = "MM-BANK"
    _next_number = 1001          # used to give each account a unique number

    # 1-2. CLASS AND OBJECT, __init__ AND ATTRIBUTES
    # A class is a template; an object is one thing built from it.
    # __init__ runs automatically each time an object is created:
    #     acc = CurrentAccount("Alice", 500)   -> calls __init__
    # `self` is the object being created. `self.owner = owner` stores a value
    # INSIDE this object: an instance attribute, different for each account.
    def __init__(self, owner: str, opening_balance: float = 0.0):
        if opening_balance < 0:
            raise ValueError("The opening balance cannot be negative")
        self.owner = owner                      # public attribute
        self._balance = opening_balance         # protected: see 5. below
        self._history: list[tuple] = []         # (date, type, amount)
        # Each new account takes the next number, then increases the class counter.
        self.number = Account._next_number
        Account._next_number += 1

    # 5. ENCAPSULATION
    # The leading underscore in `_balance` means "internal: do not change it
    # from outside". Python does not block access, but the convention is
    # respected. The balance changes only through deposit() and withdraw(),
    # which apply the rules.
    #
    # @property turns a method into a read-only attribute:
    #     acc.balance        -> works (calls this method)
    #     acc.balance = 1e6  -> AttributeError: no way to set it directly
    @property
    def balance(self) -> float:
        return round(self._balance, 2)

    # 3. METHODS: functions defined in the class. They receive the object as
    # `self`, so they can read and change ITS attributes.
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("A deposit must be positive")
        self._balance += amount
        self._history.append((date.today(), "deposit", amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("A withdrawal must be positive")
        # The limit depends on the type of account: each child class defines it.
        if self._balance - amount < -self.overdraft_limit():
            raise InsufficientFunds(
                f"{self.owner}: withdrawing {amount:,.2f} would exceed the limit "
                f"(balance {self.balance:,.2f}, overdraft {self.overdraft_limit():,.2f})"
            )
        self._balance -= amount
        self._history.append((date.today(), "withdrawal", amount))

    def transfer_to(self, other: "Account", amount: float) -> None:
        """Objects can work together: one account calls methods of another."""
        self.withdraw(amount)       # raises InsufficientFunds before any money moves
        other.deposit(amount)

    @property
    def history(self) -> list[tuple]:
        return list(self._history)  # a copy: the caller cannot alter the real history

    # Abstract methods: no code here; every child class MUST provide them.
    @abstractmethod
    def overdraft_limit(self) -> float:
        """How far below zero the balance may go."""

    @abstractmethod
    def month_end(self) -> None:
        """What happens to this account at the end of each month."""

    # 7. SPECIAL METHODS ("dunder" methods: double underscore on each side)
    # Python calls them automatically for built-in operations.

    def __str__(self) -> str:
        # Called by print(acc) and str(acc): a readable text for users.
        return f"{type(self).__name__} {self.number} ({self.owner}): {self.balance:,.2f}"

    def __repr__(self) -> str:
        # Called in the console and inside lists: a precise text for developers.
        return f"{type(self).__name__}(owner={self.owner!r}, balance={self.balance})"

    def __eq__(self, other) -> bool:
        # Called by acc1 == acc2. Two accounts are the same if they have the same number.
        return isinstance(other, Account) and self.number == other.number

    def __lt__(self, other: "Account") -> bool:
        # Called by acc1 < acc2, and therefore by sorted(): accounts sort by balance.
        return self.balance < other.balance

    def __hash__(self) -> int:
        # Defining __eq__ removes the default hash; restore one so accounts can go in sets.
        return hash(self.number)


# =============================================================================
# 9. INHERITANCE
# `class CurrentAccount(Account)` means: CurrentAccount IS an Account. It gets
# every attribute and method of Account (deposit, withdraw, balance, __str__...)
# and adds or changes only what is specific to it.
# =============================================================================
class CurrentAccount(Account):
    """An everyday account with an agreed overdraft and a monthly fee."""

    monthly_fee = 3.00

    def __init__(self, owner: str, opening_balance: float = 0.0, overdraft: float = 500.0):
        # super() is the parent class. super().__init__(...) runs Account's
        # __init__, which sets owner, _balance, number... Then this class adds
        # its own attribute. Without this call, those attributes would not exist.
        super().__init__(owner, opening_balance)
        self.overdraft = overdraft

    # 10. METHOD OVERRIDING: defining a method the parent also defines (or,
    # here, declares as abstract). Python uses the child's version.
    def overdraft_limit(self) -> float:
        return self.overdraft

    def month_end(self) -> None:
        self._balance -= self.monthly_fee
        self._history.append((date.today(), "fee", self.monthly_fee))


class SavingsAccount(Account):
    """A savings account: no overdraft, monthly interest."""

    def __init__(self, owner: str, opening_balance: float = 0.0, annual_rate: float = 0.04):
        super().__init__(owner, opening_balance)
        self.annual_rate = annual_rate

    def overdraft_limit(self) -> float:
        return 0.0                  # a savings account can never go below zero

    def month_end(self) -> None:
        interest = self._balance * self.annual_rate / 12
        self._balance += interest
        self._history.append((date.today(), "interest", round(interest, 2)))

    # Overriding a CONCRETE method, and extending it with super():
    # same text as Account.__str__, plus the interest rate.
    def __str__(self) -> str:
        return f"{super().__str__()} at {self.annual_rate:.2%}"


# =============================================================================
# 11. COMPOSITION
# A Bank is not an account: it HAS accounts. It holds Account objects in a
# dictionary and works with them. Rule of thumb:
#     "IS a"  -> inheritance  (a SavingsAccount IS an Account)
#     "HAS a" -> composition  (a Bank HAS accounts)
# =============================================================================
class Bank:
    def __init__(self, name: str):
        self.name = name
        self._accounts: dict[int, Account] = {}

    def open(self, account: Account) -> Account:
        self._accounts[account.number] = account
        return account

    def get(self, number: int) -> Account:
        return self._accounts[number]

    def total_deposits(self) -> float:
        return round(sum(acc.balance for acc in self._accounts.values()), 2)

    def month_end(self) -> None:
        # 12. POLYMORPHISM: the same call, acc.month_end(), does different things
        # depending on the account's class: a fee for a CurrentAccount, interest
        # for a SavingsAccount. The Bank does not need to know which is which.
        for acc in self._accounts.values():
            acc.month_end()

    def __len__(self) -> int:
        # Special method: makes len(bank) work.
        return len(self._accounts)

    def __iter__(self):
        # Special method: makes `for acc in bank:` work.
        return iter(self._accounts.values())

    # 13. @classmethod: receives the CLASS (cls) instead of an object (self).
    # Typical use: an alternative way to create objects.
    @classmethod
    def from_records(cls, name: str, records: list[dict]) -> "Bank":
        """Build a bank from records such as rows read from a CSV file."""
        bank = cls(name)
        kinds = {"current": CurrentAccount, "savings": SavingsAccount}
        for r in records:
            bank.open(kinds[r["type"]](r["owner"], r["balance"]))
        return bank

    # 13. @staticmethod: receives neither the object nor the class. A plain
    # function placed in the class because it belongs to its topic.
    @staticmethod
    def is_valid_sort_code(code: str) -> bool:
        """UK sort codes look like 12-34-56."""
        parts = code.split("-")
        return len(parts) == 3 and all(p.isdigit() and len(p) == 2 for p in parts)


# =============================================================================
# DEMONSTRATION
# =============================================================================
def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def main() -> None:
    section("1-2. Class and object, __init__ and attributes")
    alice = CurrentAccount("Alice", 1_000)        # creating an object calls __init__
    bob = SavingsAccount("Bob", 5_000, annual_rate=0.05)
    print("alice.owner  =", alice.owner)          # instance attribute
    print("alice.number =", alice.number, "| bob.number =", bob.number)
    print("Two objects from two classes, each with its own data.")

    section("3. Methods")
    alice.deposit(250)
    alice.withdraw(100)
    print("After deposit(250) and withdraw(100):", alice.balance)

    section("4. Class attributes: shared by all objects")
    print("alice.bank_code =", alice.bank_code, "| bob.bank_code =", bob.bank_code)
    print("Account.bank_code =", Account.bank_code, "(read from the class itself)")

    section("5. Encapsulation: @property")
    print("alice.balance =", alice.balance, "(read through the property)")
    try:
        alice.balance = 1_000_000
    except AttributeError as error:
        print("alice.balance = 1_000_000 ->", type(error).__name__, ":", error)

    section("6. Custom exception")
    try:
        bob.withdraw(10_000)
    except InsufficientFunds as error:
        print("InsufficientFunds:", error)
    alice.withdraw(1_500)                         # allowed: alice has a 500 overdraft
    print("Alice withdrew 1,500 into her overdraft:", alice.balance)

    section("7. Special methods")
    print("print(alice)      ->", alice)          # __str__
    print("repr(alice)       ->", repr(alice))    # __repr__
    print("alice == alice    ->", alice == alice) # __eq__
    print("alice == bob      ->", alice == bob)
    print("alice < bob       ->", alice < bob)    # __lt__ (by balance)

    section("8. Abstraction: Account cannot be created")
    try:
        Account("Nobody")
    except TypeError as error:
        print("Account('Nobody') ->", error)

    section("9-10. Inheritance and overriding")
    print("isinstance(bob, SavingsAccount) ->", isinstance(bob, SavingsAccount))
    print("isinstance(bob, Account)        ->", isinstance(bob, Account))
    print("bob has deposit() from Account  ->", hasattr(bob, "deposit"))
    print("overdraft_limit(): alice", alice.overdraft_limit(), "| bob", bob.overdraft_limit())
    print("SavingsAccount extends __str__  ->", bob)

    section("11. Composition: a Bank HAS accounts")
    bank = Bank("MM Bank")
    for acc in (alice, bob):
        bank.open(acc)
    carol = bank.open(CurrentAccount("Carol", 300, overdraft=0))
    print(f"{bank.name}: {len(bank)} accounts, total {bank.total_deposits():,.2f}")
    bob.transfer_to(carol, 1_000)                 # objects working together
    print("After Bob transfers 1,000 to Carol:", bank.get(carol.number))

    section("12. Polymorphism: one call, different behaviour")
    print("Before month end:", [acc.balance for acc in bank])
    bank.month_end()                              # fee for current, interest for savings
    for acc in bank:
        print(f"  {acc}  <- last entry: {acc.history[-1][1:]}")
    print("Sorted by balance (uses __lt__):", sorted(bank))

    section("13. @classmethod and @staticmethod")
    records = [{"type": "current", "owner": "Dan", "balance": 120},
               {"type": "savings", "owner": "Eve", "balance": 8_000}]
    branch = Bank.from_records("MM Bank - Leeds", records)
    print("Bank.from_records(...) ->", list(branch))
    print("Bank.is_valid_sort_code('12-34-56') ->", Bank.is_valid_sort_code("12-34-56"))
    print("Bank.is_valid_sort_code('1234-56')  ->", Bank.is_valid_sort_code("1234-56"))


if __name__ == "__main__":
    main()
