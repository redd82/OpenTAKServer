from dataclasses import dataclass

from opentakserver.models.user import User


@dataclass
class TakatUser(User):
    
    def serialize(self):
        # Get the base serialization from the parent User class
        base_data = super().serialize()
        
        # Add TakatUser-specific fields
        base_data.update({
            'id': self.id,
            'data_packages_hash': [dp.hash for dp in self.data_packages],
            'data_packages': [dp.filename for dp in self.data_packages]
        })
        
        return base_data

