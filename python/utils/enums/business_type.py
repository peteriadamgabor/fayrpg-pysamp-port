from enum import Enum


class BusinessTypeEnum(int, Enum):
    BANK                 = 1
    CARDEALERSHIP        = 2
    RETAILCARDEALERSHIP  = 3
    STORE                = 4
    RESTAURANT           = 5
    FASTFOODRESTAURANT   = 6
    CLOTHSHOP            = 7
