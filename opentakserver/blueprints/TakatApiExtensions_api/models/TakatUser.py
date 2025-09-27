from dataclasses import dataclass

from opentakserver.models.user import User


@dataclass
class TakatUser(User):
    
    def serialize(self):
        # Get the base serialization from the parent User class
        base_data = super().serialize()
        
        # Add TakatUser-specific fields
        data_packages_info = [(dp.hash, dp.filename) for dp in self.data_packages]
        base_data.update({
            'id': self.id,
            'data_packages_hash': [dp_info[0] for dp_info in data_packages_info],
            'data_packages': [dp_info[1] for dp_info in data_packages_info]
        })
        
        return base_data

