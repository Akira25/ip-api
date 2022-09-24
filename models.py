from pydantic import BaseModel, conint, EmailStr, ValidationError, validator, UUID4, root_validator
from ipaddress import IPv4Address, IPv4Network, IPv6Network
from fastapi import HTTPException
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum


class PrefixState(str, Enum):
    temporary = "temporary"
    final = "final"


class Captcha(BaseModel):
    @classmethod
    def __get_validators__(cls):
        yield cls.capture_must_match

    @classmethod
    def capture_must_match(cls, v):

        if v != 'Berlin':
            raise ValueError("Was is' die Hauptstadt vong Berlin?")

        return v


class Hostname(BaseModel):

    @classmethod
    def __get_validators__(cls):
        yield cls.name_must_comply_rfc952

    # RFC 952: up to 24 characters drawn from the alphabet (A-Z), digits (0-9), minus sign (-), and period (.).
    # Note that periods are only allowed when they serve to delimit components of "domain style names".
    # For our purposes, max 63 characters fit better
    @classmethod
    def name_must_comply_rfc952(cls, name_to_check):

        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

        for char in name_to_check:
            if char not in allowed_chars:
                raise ValueError(
                    "Hostname must comply to rfc952. It's only allowed to contain characters (A-z), digits (0-9) and a minus sign (-).")

        if len(name_to_check) < 3 or len(name_to_check) > 63:
            raise ValueError(
                "Hostnames must be at least 1 characters and at most 63 characters long.")

        if not name_to_check[0].isalpha():
            raise ValueError("Hostnames must start with a character.")

        if name_to_check[-1] == '-':
            raise ValueError("Hostnames must not end with a minus sign.")

        return name_to_check


class ConstituencyName(str, Enum):
    c75 = "Wahlkreis 75, Mitte",
    c76 = "Wahlkreis 76, Pankow",
    c77 = "Wahlkreis 77, Reinickendorf",
    c78 = "Wahlkreis 78, Spandau - Charlottenburg Nord",
    c79 = "Wahlkreis 79, Steglitz - Zehlendorf",
    c80 = "Wahlkreis 80, Charlottenburg - Wilmersdorf",
    c81 = "Wahlkreis 81, Tempelhof - Schoeneberg",
    c82 = "Wahlkreis 82, Neukölln",
    c83 = "Wahlkreis 83, Friedrichshain - Kreuzberg - Prenzlauer Berg Ost",
    c84 = "Wahlkreis 84, Treptow - Köpenick",
    c85 = "Wahlkreis 85, Marzahn - Hellersdorf",
    c86 = "Wahlkreis 86, Lichtenberg"


class Constituency(BaseModel):

    @classmethod
    def __get_validators__(cls):
        yield cls.constituency_must_be_in_berlin

    # 0 shows, that no IPv6-Prefix is needed.
    @classmethod
    def constituency_must_be_in_berlin(cls, v):
        #assert(isinstance(v, int))
        if v not in list(range(75, 87)) and v != 0:
            raise ValueError(
                "Cannot assign IPv6-Prefix: No valid constituency in Berlin.")

        return v


class ExpertPrefixSizeIPv4(int):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):

        if v != 0 and (v < 23 or v > 32):
            raise ValueError(
                f"Can not assign /{v}-Prefix. Only /23 to /32 allowed, or 0 to get no IPv4-Address.")

        return v


# Request for running router, which wants to get connected IPv6?
# We may somehow connect the addresses, so we know, that they belong to the same router...
# in that turn, we may also update hostnames in old database...

class SimplePrefixRequest(BaseModel):
    host:  Hostname
    email: EmailStr
    size4: conint(ge=27, le=28)
    constituency: Constituency
    captcha: Captcha


class ExpertPrefixRequest(BaseModel):
    host:  Hostname
    email: EmailStr
    size4: ExpertPrefixSizeIPv4
    #constituency: Constituency
    captcha: Captcha


class SimplePrefixResponse(BaseModel):
    session: UUID4
    host:  Hostname
    email: EmailStr
    mesh4: list[IPv4Address]
    # ToDo: mesh6-field needed?
    prefix4: IPv4Network
    prefix6: IPv6Network
    #constituency: Constituency
    constituencyName: ConstituencyName
    state: PrefixState


class ExpertPrefixResponse(BaseModel):
    session: UUID4
    host:  Hostname
    email: EmailStr
    prefix4: Optional[IPv4Network]
    prefix6: Optional[IPv6Network]
    constituency: Optional[Constituency]
    constituencyName: Optional[ConstituencyName]
    state: PrefixState


class FinalizePrefixRequest(BaseModel):
    session: UUID4
    host:  Hostname
    prefix4: Optional[IPv4Network]
    prefix6: Optional[IPv6Network]


class FinalizePrefixResponse(BaseModel):
    session: UUID4
    host:  Hostname
    prefix4: Optional[IPv4Network]
    prefix6: Optional[IPv6Network]
    state: PrefixState
