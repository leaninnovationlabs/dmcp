"""Insert sample boat parts data

This migration adds realistic sample data for testing DBMCP with the warehouse schema.
Includes basic boat parts, manufacturers, and inventory data.

Revision ID: 002
Revises: 001
Create Date: 2025-01-04 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Numeric, Boolean, Date, DateTime, Text
from datetime import date, datetime

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Insert sample data for testing."""
    
    # Define table structures for inserts
    party_type = table('party_type',
        column('party_type_id', Integer),
        column('party_type_name', String),
        column('description', Text)
    )
    
    party = table('party',
        column('party_id', Integer),
        column('party_type_id', Integer),
        column('party_name', String),
        column('external_id', String),
        column('is_active', Boolean)
    )
    
    organization = table('organization',
        column('party_id', Integer),
        column('organization_name', String),
        column('tax_id', String),
        column('industry_code', String)
    )
    
    product_category = table('product_category',
        column('category_id', Integer),
        column('parent_category_id', Integer),
        column('category_name', String),
        column('category_code', String),
        column('description', Text),
        column('is_active', Boolean)
    )
    
    product_type = table('product_type',
        column('product_type_id', Integer),
        column('type_name', String),
        column('description', Text)
    )
    
    product = table('product',
        column('product_id', Integer),
        column('product_type_id', Integer),
        column('category_id', Integer),
        column('manufacturer_party_id', Integer),
        column('product_name', String),
        column('product_code', String),
        column('manufacturer_part_number', String),
        column('description', Text),
        column('weight_lbs', Numeric),
        column('is_active', Boolean)
    )
    
    facility_type = table('facility_type',
        column('facility_type_id', Integer),
        column('type_name', String),
        column('description', Text)
    )
    
    facility = table('facility',
        column('facility_id', Integer),
        column('facility_type_id', Integer),
        column('facility_name', String),
        column('facility_code', String),
        column('description', Text),
        column('square_footage', Integer),
        column('is_active', Boolean)
    )
    
    inventory_item = table('inventory_item',
        column('inventory_item_id', Integer),
        column('product_id', Integer),
        column('facility_id', Integer),
        column('condition_code', String),
        column('quantity_on_hand', Numeric),
        column('quantity_available', Numeric),
        column('unit_cost', Numeric)
    )
    
    # Insert party types
    op.bulk_insert(party_type, [
        {'party_type_id': 1, 'party_type_name': 'Manufacturer', 'description': 'Boat parts manufacturer'},
        {'party_type_id': 2, 'party_type_name': 'Customer', 'description': 'End customer'},
        {'party_type_id': 3, 'party_type_name': 'Supplier', 'description': 'Parts supplier'},
    ])
    
    # Insert manufacturers (parties)
    op.bulk_insert(party, [
        {'party_id': 1, 'party_type_id': 1, 'party_name': 'Mercury Marine', 'external_id': 'MERCURY', 'is_active': True},
        {'party_id': 2, 'party_type_id': 1, 'party_name': 'Yamaha Marine', 'external_id': 'YAMAHA', 'is_active': True},
        {'party_id': 3, 'party_type_id': 1, 'party_name': 'Brunswick Corporation', 'external_id': 'BRUNSWICK', 'is_active': True},
        {'party_id': 4, 'party_type_id': 1, 'party_name': 'Johnson Outdoors Marine', 'external_id': 'JOHNSON', 'is_active': True},
        {'party_id': 5, 'party_type_id': 1, 'party_name': 'SeaStar Solutions', 'external_id': 'SEASTAR', 'is_active': True},
    ])
    
    # Insert organization details
    op.bulk_insert(organization, [
        {'party_id': 1, 'organization_name': 'Mercury Marine', 'tax_id': '39-0123456', 'industry_code': 'MARINE'},
        {'party_id': 2, 'organization_name': 'Yamaha Marine', 'tax_id': '54-0234567', 'industry_code': 'MARINE'},
        {'party_id': 3, 'organization_name': 'Brunswick Corporation', 'tax_id': '36-0345678', 'industry_code': 'MARINE'},
        {'party_id': 4, 'organization_name': 'Johnson Outdoors Marine', 'tax_id': '39-0456789', 'industry_code': 'MARINE'},
        {'party_id': 5, 'organization_name': 'SeaStar Solutions', 'tax_id': '54-0567890', 'industry_code': 'MARINE'},
    ])
    
    # Insert product categories (hierarchical)
    op.bulk_insert(product_category, [
        {'category_id': 1, 'parent_category_id': None, 'category_name': 'Engine Parts', 'category_code': 'ENGINE', 'description': 'Boat engine components', 'is_active': True},
        {'category_id': 2, 'parent_category_id': 1, 'category_name': 'Propellers', 'category_code': 'PROP', 'description': 'Boat propellers and accessories', 'is_active': True},
        {'category_id': 3, 'parent_category_id': 1, 'category_name': 'Filters', 'category_code': 'FILTER', 'description': 'Engine filters and maintenance', 'is_active': True},
        {'category_id': 4, 'parent_category_id': None, 'category_name': 'Electrical', 'category_code': 'ELEC', 'description': 'Electrical components', 'is_active': True},
        {'category_id': 5, 'parent_category_id': 4, 'category_name': 'Ignition', 'category_code': 'IGNITION', 'description': 'Ignition system components', 'is_active': True},
        {'category_id': 6, 'parent_category_id': None, 'category_name': 'Hull & Deck', 'category_code': 'HULL', 'description': 'Hull and deck hardware', 'is_active': True},
    ])
    
    # Insert product types
    op.bulk_insert(product_type, [
        {'product_type_id': 1, 'type_name': 'Part', 'description': 'Physical boat part'},
        {'product_type_id': 2, 'type_name': 'Kit', 'description': 'Assembly kit with multiple parts'},
        {'product_type_id': 3, 'type_name': 'Tool', 'description': 'Maintenance and repair tool'},
    ])
    
    # Insert products
    op.bulk_insert(product, [
        # Propellers
        {'product_id': 1, 'product_type_id': 1, 'category_id': 2, 'manufacturer_party_id': 1, 'product_name': 'Mercury 3-Blade Aluminum Propeller 14x19', 'product_code': 'MERC-PROP-14x19', 'manufacturer_part_number': '48-832832A45', 'description': '14" diameter, 19" pitch aluminum propeller', 'weight_lbs': 8.5, 'is_active': True},
        {'product_id': 2, 'product_type_id': 1, 'category_id': 2, 'manufacturer_party_id': 2, 'product_name': 'Yamaha Saltwater Series II 3-Blade SS Prop 15x17', 'product_code': 'YAM-PROP-15x17', 'manufacturer_part_number': '6E5-45947-00-EL', 'description': '15" diameter, 17" pitch stainless steel propeller', 'weight_lbs': 12.3, 'is_active': True},
        
        # Filters
        {'product_id': 3, 'product_type_id': 1, 'category_id': 3, 'manufacturer_party_id': 1, 'product_name': 'Mercury Fuel Filter Element', 'product_code': 'MERC-FUEL-FILTER', 'manufacturer_part_number': '35-60494A2', 'description': 'Fuel filter element for Mercury engines', 'weight_lbs': 0.3, 'is_active': True},
        {'product_id': 4, 'product_type_id': 1, 'category_id': 3, 'manufacturer_party_id': 2, 'product_name': 'Yamaha Oil Filter', 'product_code': 'YAM-OIL-FILTER', 'manufacturer_part_number': '5GH-13440-50-00', 'description': 'Engine oil filter for Yamaha 4-stroke engines', 'weight_lbs': 0.5, 'is_active': True},
        
        # Ignition
        {'product_id': 5, 'product_type_id': 1, 'category_id': 5, 'manufacturer_party_id': 1, 'product_name': 'Mercury Spark Plug Set (6-pack)', 'product_code': 'MERC-SPARK-6PK', 'manufacturer_part_number': '33-864218T01', 'description': 'Set of 6 spark plugs for V6 engines', 'weight_lbs': 1.2, 'is_active': True},
        {'product_id': 6, 'product_type_id': 1, 'category_id': 5, 'manufacturer_party_id': 3, 'product_name': 'Brunswick Ignition Coil', 'product_code': 'BRUNS-COIL-01', 'manufacturer_part_number': '18-5184-1', 'description': 'Ignition coil for Mercury/Mariner engines', 'weight_lbs': 2.1, 'is_active': True},
        
        # Hull Hardware
        {'product_id': 7, 'product_type_id': 1, 'category_id': 6, 'manufacturer_party_id': 5, 'product_name': 'SeaStar Hydraulic Steering Helm', 'product_code': 'SEASTAR-HELM-H5000', 'manufacturer_part_number': 'HH5271', 'description': 'Single cable hydraulic steering helm', 'weight_lbs': 15.8, 'is_active': True},
        {'product_id': 8, 'product_type_id': 2, 'category_id': 6, 'manufacturer_party_id': 4, 'product_name': 'Johnson Bilge Pump Kit', 'product_code': 'JOHNSON-BILGE-500', 'manufacturer_part_number': '500GPH-KIT', 'description': 'Complete 500 GPH bilge pump installation kit', 'weight_lbs': 3.7, 'is_active': True},
    ])
    
    # Insert facility types
    op.bulk_insert(facility_type, [
        {'facility_type_id': 1, 'type_name': 'Warehouse', 'description': 'Storage and distribution warehouse'},
        {'facility_type_id': 2, 'type_name': 'Retail Store', 'description': 'Retail storefront'},
    ])
    
    # Insert facilities
    op.bulk_insert(facility, [
        {'facility_id': 1, 'facility_type_id': 1, 'facility_name': 'Main Distribution Center', 'facility_code': 'DC-MAIN', 'description': 'Primary warehouse facility', 'square_footage': 50000, 'is_active': True},
        {'facility_id': 2, 'facility_type_id': 2, 'facility_name': 'Marine Supply Store #1', 'facility_code': 'STORE-001', 'description': 'Retail location downtown', 'square_footage': 2500, 'is_active': True},
    ])
    
    # Insert inventory
    op.bulk_insert(inventory_item, [
        {'inventory_item_id': 1, 'product_id': 1, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 25, 'quantity_available': 20, 'unit_cost': 89.99},
        {'inventory_item_id': 2, 'product_id': 2, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 15, 'quantity_available': 12, 'unit_cost': 349.99},
        {'inventory_item_id': 3, 'product_id': 3, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 100, 'quantity_available': 95, 'unit_cost': 12.50},
        {'inventory_item_id': 4, 'product_id': 4, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 75, 'quantity_available': 70, 'unit_cost': 18.75},
        {'inventory_item_id': 5, 'product_id': 5, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 40, 'quantity_available': 35, 'unit_cost': 45.00},
        {'inventory_item_id': 6, 'product_id': 6, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 20, 'quantity_available': 18, 'unit_cost': 125.00},
        {'inventory_item_id': 7, 'product_id': 7, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 5, 'quantity_available': 4, 'unit_cost': 285.00},
        {'inventory_item_id': 8, 'product_id': 8, 'facility_id': 1, 'condition_code': 'NEW', 'quantity_on_hand': 12, 'quantity_available': 10, 'unit_cost': 95.50},
        
        # Store inventory (smaller quantities)
        {'inventory_item_id': 9, 'product_id': 3, 'facility_id': 2, 'condition_code': 'NEW', 'quantity_on_hand': 10, 'quantity_available': 10, 'unit_cost': 12.50},
        {'inventory_item_id': 10, 'product_id': 4, 'facility_id': 2, 'condition_code': 'NEW', 'quantity_on_hand': 8, 'quantity_available': 8, 'unit_cost': 18.75},
        {'inventory_item_id': 11, 'product_id': 5, 'facility_id': 2, 'condition_code': 'NEW', 'quantity_on_hand': 5, 'quantity_available': 5, 'unit_cost': 45.00},
    ])


def downgrade() -> None:
    """Remove sample data."""
    
    # Delete in reverse order to handle foreign key constraints
    op.execute("DELETE FROM inventory_item")
    op.execute("DELETE FROM facility")
    op.execute("DELETE FROM facility_type")
    op.execute("DELETE FROM product")
    op.execute("DELETE FROM product_type")
    op.execute("DELETE FROM product_category")
    op.execute("DELETE FROM organization")
    op.execute("DELETE FROM party")
    op.execute("DELETE FROM party_type")