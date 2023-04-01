""" Structures for databases. """
from typing import List, TypedDict


class EstateDb(TypedDict):
    """
    Structure that should be connected in DB and come to proxy as single
    structure. Then PostgresAPI and NoSQLAPI will convert it to their
    structures.
    """

    price: int
    title: str
    place: str
    url: str
    has_video: bool
    features: List[str]
    medias: List[str]
    region: int


class EstateFrontendResponse(TypedDict):
    """Structure that's returned back for the frontend view."""

    id: int
    title: str
    place: str
    url: str
    features: List[str]
    medias: List[str]
    region: int
    price: int
