# Temporary in-memory persistence layer before connecting PostgreSQL
fake_db: dict[int, dict] = {}
id_counter: int = 1


def get_next_id() -> int:
    global id_counter
    current = id_counter
    id_counter += 1
    return current