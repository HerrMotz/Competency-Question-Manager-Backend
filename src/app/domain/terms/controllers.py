from litestar import Controller, delete, get, put


class TermController(Controller):
    path = "/terms"

    @get("/")
    def get_all(self) -> ...:
        """Gets all `Terms` with in the system."""
        ...

    @get("/")
    def get_all_project(self) -> ...:
        """Gets all `Passage`s and `Term`s within a `Project`."""
        ...

    @get("/")
    def get_all_question(self) -> ...:
        """Gets all `Passage`s and `Term`s associated with a `Question`."""
        ...

    @put("/")
    def add(self) -> ...:
        """Adds one or more `Passage`s and `Term`s to a `Question` or updates existing `Passage`s."""
        ...

    @delete("/")
    def delete(self) -> ...:
        """Removes one or more `Passage`s and `Term`s from a `Question`."""
        ...
