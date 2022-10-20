from enum import Enum
from ipaddress import IPv4Address, IPv4Network, IPv6Network
from typing import Optional, Dict, Any

from email_validator import validate_email
from pydantic import BaseModel, conint, EmailStr, UUID4

"""Here are the definition of some datatypes, which will
get checked and validated against by pydantic.

They directly influence the schema of valid json-requests
(hence the name of this file).
"""


class PrefixState(str, Enum):
    temporary = "temporary"
    final = "final"


class Captcha(BaseModel):

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='string', format='captcha',
                            example="Charlottenburg")

    @classmethod
    def __get_validators__(cls):
        yield cls.capture_must_match

    @classmethod
    def capture_must_match(cls, v):
        if v != 'Berlin':
            raise ValueError("Was ist die Hauptstadt von Berlin?")

        return v


class Hostname(BaseModel):

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='string', format='host',
                            example='freifunk-router')

    @classmethod
    def __get_validators__(cls):
        yield cls.name_must_comply_rfc952

    # RFC 952: up to 24 characters drawn from the alphabet (A-Z), digits (0-9), minus sign (-), and period (.).
    # Note that periods are only allowed when they serve to delimit components of "domain style names".
    # For our purposes, max 63 characters fit better
    @classmethod
    def name_must_comply_rfc952(cls, name_to_check):
        # Todo: string lib benutzen
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


class EmailStrict(BaseModel):

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='string', format='email',
                            example='test@example.org')

    @classmethod
    def __get_validators__(cls):
        yield cls.email_with_dns_check

    @classmethod
    def email_with_dns_check(cls, email):
        try:
            validation = validate_email(email, check_deliverability=True)
            v = validation.email
        except:
            raise ValueError(
                "No valid email address. Please give your right contact, so we can send you the IP-Addresses.")

        return validation


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
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='integer', format='constituency', example=42)

    @classmethod
    def __get_validators__(cls):
        yield cls.constituency_must_be_in_berlin

    # 0 shows, that no IPv6-Prefix is needed.
    @classmethod
    def constituency_must_be_in_berlin(cls, v):
        # assert(isinstance(v, int))
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


class SessionDBRepresentation(BaseModel):
    session: UUID4
    host: Hostname
    email: EmailStr
    constituency: Constituency
    mesh4: list[IPv4Address]
    prefix4: IPv4Network
    prefix6: IPv6Network
    confirmed: bool

    class Config:
        orm_mode = True


# Request for running router, which wants to get connected IPv6?
# We may somehow connect the addresses, so we know, that they belong to the same router...
# in that turn, we may also update hostnames in old database...


class SimplePrefixRequest(BaseModel):
    host: Hostname
    email: list[EmailStr]
    size4: conint(ge=27, le=28)
    constituency: Constituency
    captcha: Captcha


class ExpertPrefixRequest(BaseModel):
    host: Hostname
    email: EmailStr
    size4: ExpertPrefixSizeIPv4
    constituency: Constituency
    captcha: Captcha

# old definition of Request
# class SimplePrefixResponse(BaseModel):
#     session: UUID4
#     host: Hostname
#     email: EmailStr
#     mesh4: list[IPv4Address]
#     # ToDo: mesh6-field needed? No: we begin counting mesh-addresses from the back of the prefix
#     prefix4: IPv4Network
#     prefix6: IPv6Network
#     constituency: Constituency
#     constituencyName: ConstituencyName
#     state: PrefixState


class SimplePrefixResponse(BaseModel):
    session: UUID4
    host: Hostname
    email: [EmailStr]
    constituency: Constituency

# old definition
# class ExpertPrefixResponse(BaseModel):
#     session: UUID4
#     host: Hostname
#     email: EmailStr
#     prefix4: Optional[IPv4Network]
#     prefix6: Optional[IPv6Network]
#     constituency: Optional[Constituency]
#     constituencyName: Optional[ConstituencyName]
#     state: PrefixState

# ToDo: ConfirmPrefix is a get-request now
#class ConfirmPrefixRequest(BaseModel):
#    session: UUID4
#    host: Hostname
#    mesh4: list[IPv4Address]
#    prefix4: IPv4Network
#    prefix6: IPv6Network

class ConfirmPrefixRequest(BaseModel):
    session: UUID4
    token: UUID4


class ConfirmPrefixResponse(BaseModel):
    session: UUID4
    host: Hostname
    mesh4: list[IPv4Address]
    prefix4: IPv4Network
    prefix6: IPv6Network
    # ToDo: Make URL
    deleteLink: str
    msgLink: str

class GetPrefixesByMailRequest(BaseModel):
    pass

class GetPrefixesBySessionRequest(BaseModel):
    pass