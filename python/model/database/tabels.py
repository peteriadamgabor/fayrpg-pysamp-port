from sqlalchemy import Column, Integer, ForeignKey, Table

from .base import Base

fraction_skins = Table(
    'fraction_skins',
    Base.metadata,
    Column('fraction_id', Integer, ForeignKey('fractions.id'), primary_key=True),
    Column('skin_id', Integer, ForeignKey('skins.id'), primary_key=True)
)

vehicle_model_fuels = Table(
    'vehicle_model_fuels',
    Base.metadata,
    Column('vehicle_model_id', Integer, ForeignKey('vehicle_models.id'), primary_key=True),
    Column('fuel_type_id', Integer, ForeignKey('fuel_types.id'), primary_key=True)
)

shop_skins = Table(
    'shop_skins',
    Base.metadata,
    Column('business_id', Integer, ForeignKey('business.id'), primary_key=True),
    Column('skin_id', Integer, ForeignKey('skins.id'), primary_key=True)
)

account_players = Table(
    'account_players',
    Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id'), primary_key=True),
    Column('player_id', Integer, ForeignKey('players.id'), primary_key=True)
)
