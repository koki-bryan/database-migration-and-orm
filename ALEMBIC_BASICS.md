# Alembic — The Super Basic Version

> Tone: still explaining to a 10-year-old. Read the **SQLAlchemy** guide first — Alembic is its
> best friend and won't make sense alone.

---

## The problem Alembic fixes

In the SQLAlchemy guide, we built tables with `Base.metadata.create_all(engine)`. That works... the
first time.

But imagine this: you built a LEGO castle 🏰. Now you want to add a tower. With `create_all`,
SQLAlchemy looks at your castle and says "Oh, a castle already exists, I'll do nothing," and your
tower never gets built. 😤

Also, what if you want to **undo** a change? Or you have a friend who needs to build the _exact same_
castle on their computer? `create_all` can't help with any of that.

**Alembic is like a save-game system for your database.** 🎮

- Every time you change your tables, Alembic writes down a "save point" (called a **migration**).
- You can jump forward to the newest save (`upgrade`).
- You can jump backward to an older save (`downgrade`).
- Your friend can replay all your save points and end up with the identical database.

Think of migrations like a **diary** 📔 of every change your database ever had, in order.

---

## The mental picture

```
save 1: "created professors table"
   ↓
save 2: "added email column to professors"
   ↓
save 3: "created subjects table"
   ↓
  HEAD  ← you are here (the newest save)
```

Each arrow is one migration file. "HEAD" just means "the latest save point."

---

## Step 1: Wake Alembic up

In your project folder, run this ONE time:

```bash
alembic init alembic
```

This creates two things:

- A file called `alembic.ini` → the **settings** file.
- A folder called `alembic/` → where all your diary pages (migrations) will live. Inside it there's
  an important file: `alembic/env.py`.

Think of this like installing the save-game system before you can save.

---

## Step 2: Tell Alembic two secrets

Alembic is new here. It doesn't know two things, and you have to tell it:

### Secret A: "Where is the database?"

Open `alembic.ini`, find the line:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

Change it to YOUR real database address:

```ini
sqlalchemy.url = postgresql+psycopg://postgres:mypassword@localhost:5432/learn_be
```

> This is the quick-and-dirty beginner way (password sitting in a file). Not secure, totally fine for
> learning. Later you'd load it from `.env` instead.

### Secret B: "What do my tables look like?"

Alembic needs to see your SQLAlchemy models to compare them against the database. Open
`alembic/env.py` and find the line:

```python
target_metadata = None
```

Change it so it points to your `Base`'s metadata. You import your Base and your models, then:

```python
# near the top of env.py
from app.database import Base
from app.models import professor, subject   # import models so Alembic can "see" them

target_metadata = Base.metadata
```

> ⚠️ The #1 beginner mistake: forgetting to import your models here. If Alembic can't _see_ a model,
> it acts like that table doesn't exist and won't create it. Importing them is like turning on the
> lights so Alembic can look around.

---

## Step 3: Take your first "snapshot" (autogenerate)

Now the magic. Alembic can look at your Python models, look at your real database, spot the
difference, and **write the migration file for you**:

```bash
alembic revision --autogenerate -m "create professors table"
```

- `revision` = "make a new diary page"
- `--autogenerate` = "figure out the changes automatically by comparing models vs database"
- `-m "..."` = a little note so future-you remembers what this page was about

This creates a new file inside `alembic/versions/`. **Open it and read it!** It will have two
functions:

```python
def upgrade():
    # the instructions to GO FORWARD (e.g. create the table)
    ...

def downgrade():
    # the instructions to UNDO it (e.g. drop the table)
    ...
```

> Think of `upgrade` as "do the change" and `downgrade` as "ctrl+Z the change."
>
> ⚠️ Always read this file before running it. Autogenerate is smart but not perfect — sometimes it
> guesses wrong, especially with renames.

---

## Step 4: Actually apply it

The migration file was just _written_. The database hasn't changed yet (the diary page is written
but the event hasn't happened). To make it real:

```bash
alembic upgrade head
```

`upgrade head` means "run every save point up to the newest one." Now go look at your database —
the `professors` table is really there. 🎉

---

## Step 5: The loop you'll repeat forever

This is the whole rhythm of using Alembic. Memorize this dance:

```
1. Change your SQLAlchemy model (add a column, add a table, etc.)
2. alembic revision --autogenerate -m "what I did"
3. READ the generated file
4. alembic upgrade head
```

That's it. Every single schema change follows these 4 steps for the rest of your life. 🔁

### Example: adding an email column

1. In your `Professor` model, add a new line: `email: Mapped[str] = mapped_column()`
2. `alembic revision --autogenerate -m "add email to professors"`
3. Read the file — it should say "add column email."
4. `alembic upgrade head` — done, the column now exists.

---

## Undoing things (the save-game superpower)

Made a mistake? Go back one save point:

```bash
alembic downgrade -1
```

`-1` means "go back one step." This runs the `downgrade()` function of the latest migration.

Want to go back to the very beginning (empty database)?

```bash
alembic downgrade base
```

Want to return to newest again?

```bash
alembic upgrade head
```

Forward and backward through time, like a video game. That's the whole point of Alembic.

---

## Handy "where am I?" commands

```bash
alembic current    # which save point is the database on right now?
alembic history    # show me the whole diary, all save points in order
```

Use these when you get confused about what state things are in (you will, everyone does).

---

## Why NOT just use create_all?

| `create_all` (SQLAlchemy)      | Alembic                               |
| ------------------------------ | ------------------------------------- |
| Builds tables that don't exist | Builds AND changes AND removes tables |
| Can't change existing tables   | Can add/drop columns, rename, etc.    |
| No undo                        | Full undo (`downgrade`)               |
| No history                     | Keeps a diary of every change         |
| Fine for tiny learning scripts | What real projects actually use       |

> Golden rule: **pick ONE.** If you're using Alembic, stop calling `create_all`. Having both fighting
> over who controls the tables causes confusing bugs. In a real project, Alembic wins.

---

## The one-sentence summary

> Alembic is a save-game system for your database: every table change becomes a numbered save point
> you can jump forward (`upgrade`) or backward (`downgrade`) through, so your schema has a history
> and can be rebuilt anywhere.

---

## The absolute minimum cheat sheet

```bash
alembic init alembic                              # once, to set up
# (edit alembic.ini url + env.py target_metadata)
alembic revision --autogenerate -m "my change"    # write a save point
alembic upgrade head                              # apply it
alembic downgrade -1                              # undo it
alembic current                                   # where am I?
alembic history                                   # show all saves
```

If you can run those and watch tables appear and disappear in Postgres, **you understand Alembic.**
