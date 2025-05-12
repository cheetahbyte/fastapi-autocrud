# fastapi-autocrud

**fastapi-autocrud** is a minimal and opinionated FastAPI extension that automatically generates CRUD endpoints for your Pydantic models, using pluggable storage backends such as in-memory or Tortoise ORM.

This project was originally developed as a **purpose-built solution for [keinbudget](https://github.com/cheetahbyte/keinbudget)** — a personal finance manager — and fits its architectural needs.

## ✨ Features

- 🔁 Automatically generates:
  - `GET /` – list all entries
  - `POST /` – create entry
  - `GET /{id}` – get entry by ID
  - `PUT /{id}` – update entry
  - `DELETE /{id}` – delete entry
- 🧱 Storage backend support (e.g. Tortoise ORM, in-memory)
- 🔒 Inject dependencies like `Depends(get_current_user)` directly into both endpoints and storage logic
- 🧩 Type-safe Pydantic model derivation for `Create` and `Update` schemas

## 🚧 Warning

This project was created specifically for the internal needs of **keinbudget**. It is not intended for general-purpose use at this time.

> ⚠️ **Use at your own risk.**  
> API stability, edge case support, and extensibility are not guaranteed yet.  
> I may decide to expand or generalize this project later — but no promises.