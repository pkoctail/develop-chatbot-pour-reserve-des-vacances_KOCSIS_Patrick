# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        dst_city: str = None,
        or_city: str = None,
        str_date: str = None,
        end_date: str = None,
        budget: str = None,
        
    ):
        
        self.dst_city: str = dst_city
        self.or_city: str = or_city
        self.str_date: str = str_date
        self.end_date: str = end_date
        self.budget = budget
        
