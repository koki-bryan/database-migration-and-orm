# SQLAlchemy — The Super Basic Version

> Tone: imagine I'm explaining this to a 10-year-old. We're going for "it works" not "it's perfect."

---

## What even is SQLAlchemy?

Imagine your **database** is a giant box of LEGO drawers. Each drawer holds one kind of thing —
one drawer for "professors", one for "subjects".

The problem: the database only speaks a weird robot language called **SQL**
(`SELECT * FROM professors;`). You speak **Python**.

**SQLAlchemy is the translator.** You talk to it in Python, and it whispers SQL to the database for
you. You never have to speak robot.

So instead of writing scary SQL, you write Python classes and SQLAlchemy turns your classes into
tables, and your Python objects into rows.

---

## The 3 things you ALWAYS need

Think of setting up a lemonade stand. Before you sell anything, you need 3 things:

### 1. The Engine 🚗
The **engine** is the car that drives to the database and back. It knows the *address* of your
database (that long `postgresql+psycopg://...` string).

You make it once. It's the thing that actually connects.

```python
from sqlalchemy import create_engine

# the address string says: who you are (user:password), where it lives (localhost:5432),
# and which box to open (the database name at the end)
engine = create_engine("postgresql+psycopg://postgres:mypassword@localhost:5432/learn_be")
```

> ⚠️ Beginner trap: if the address has no database name at the end (just stops at `:5432`), the car
> drives to the parking lot but never enters a building. Always put the DB name at the end.

### 2. The Session 💬
The **session** is a *conversation* with the database.

Think of it like a shopping cart 🛒. You put things in ("I want to add this professor"), you change
things, and nothing is REAL until you say **"commit"** (checkout). If you never commit, it's like
walking out of the store and leaving your cart behind — nothing got saved.

```python
from sqlalchemy.orm import sessionmaker

# this is a "session factory" — a machine that hands you fresh shopping carts
SessionLocal = sessionmaker(bind=engine)

# get one cart to use
session = SessionLocal()
```

### 3. The Base 🧬
The **Base** is the "parent" that all your table-classes copy from. It's like the template for a
school worksheet — every worksheet (every table) starts from the same blank template so they all
look official.

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Every table class you make will say "I am a child of Base," and that's how SQLAlchemy knows "oh,
this Python class is actually a database table."

---

## Making a table (a "Model")

A **Model** is just a Python class that describes ONE drawer (one table).

Let's make a `Professor` table. We want each professor to have an `id` (a number tag) and a `name`.

```python
from sqlalchemy.orm import Mapped, mapped_column

class Professor(Base):
    __tablename__ = "professors"   # the real name of the drawer in the database

    id: Mapped[int] = mapped_column(primary_key=True)   # the unique number tag
    name: Mapped[str] = mapped_column()                 # a word/text
```

Breaking it down like you're 10:
- `class Professor(Base)` → "Hey SQLAlchemy, here's a new kind of thing, and it's a real table."
- `__tablename__` → the name written on the drawer.
- `id` is the **primary key** → every professor gets a unique number sticker, like a jersey number.
  No two professors share one.
- `name` → a box to write their name in.

---

## Actually creating the table in the database

You *described* the table in Python, but the database doesn't have it yet. You described a drawer on
paper — now you have to actually build the drawer.

The most basic (and honestly lazy) way:

```python
Base.metadata.create_all(engine)
```

This tells SQLAlchemy: "Look at every class that copied from Base, and go build those drawers in the
real database."

> ⚠️ Honest note: this is the *beginner* way. It's great for learning. But it has a weakness — it
> only CREATES tables that don't exist. If you later change a table (add a column), `create_all`
> **won't update it**. That's the exact problem Alembic solves (see the other file). For now,
> `create_all` is totally fine to learn with.

---

## Putting data IN (Create)

```python
session = SessionLocal()

new_prof = Professor(name="Dr. Smith")   # make a Python object (not saved yet!)
session.add(new_prof)                     # put it in the shopping cart
session.commit()                          # CHECKOUT — now it's really saved
```

Remember the cart analogy: `add` = put in cart, `commit` = pay and make it real. Forget `commit` and
nothing happens.

---

## Getting data OUT (Read)

```python
# get ALL professors
all_profs = session.query(Professor).all()

# get ONE professor by their number tag
one_prof = session.query(Professor).filter(Professor.id == 1).first()

print(one_prof.name)   # "Dr. Smith"
```

Think of `query` as asking the librarian: "Can you bring me all the professors?" `.all()` means
"bring everything," `.first()` means "just bring me the first one you find."

> Note: `session.query(...)` is the classic, older style. There's a newer `select()` style too, but
> `query` is the easiest to understand when starting, so we're using it on purpose.

---

## Changing data (Update)

```python
prof = session.query(Professor).filter(Professor.id == 1).first()
prof.name = "Dr. Johnson"   # just change the Python object's box
session.commit()            # checkout again to save the change
```

You grab the thing, scribble a new value on it, and commit. That's it.

---

## Deleting data (Delete)

```python
prof = session.query(Professor).filter(Professor.id == 1).first()
session.delete(prof)   # put it in the "throw away" pile
session.commit()       # checkout — now it's really gone
```

---

## Closing the conversation

When you're done talking, hang up the phone:

```python
session.close()
```

If you forget, it's not the end of the world while learning, but it's polite and avoids leaving
connections open.

---

## The whole thing in one tiny script

Here's the most basic possible "it works" program, start to finish:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

# 1. engine (the car)
engine = create_engine("postgresql+psycopg://postgres:mypassword@localhost:5432/learn_be")

# 2. base (the template)
class Base(DeclarativeBase):
    pass

# 3. a model (one table)
class Professor(Base):
    __tablename__ = "professors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

# 4. build the table in the real database
Base.metadata.create_all(engine)

# 5. session factory (the cart machine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 6. add someone
session.add(Professor(name="Dr. Smith"))
session.commit()

# 7. read them back
for p in session.query(Professor).all():
    print(p.id, p.name)

session.close()
```

If you run that and see `1 Dr. Smith` printed, **you just used SQLAlchemy end to end.** 🎉

---

## The one-sentence summary

> SQLAlchemy lets you treat database tables like Python classes and database rows like Python
> objects, and the **session** is the shopping cart where changes aren't real until you `commit`.

---

## What to try next

- Make a second model (`Subject`) the same way.
- Add more columns (like `age` or `email`).
- Then read the **Alembic** guide to learn the grown-up way of building/changing tables (instead of
  `create_all`).
