"""Create Len Silverston boat parts warehouse schema

This migration creates an enterprise-grade dimensional model following
Len Silverston's methodology for boat parts warehouse management.

Unlike the flat table disasters created by consulting firms, this schema
properly separates:
- Party relationships (customers, suppliers, manufacturers)
- Product hierarchies with proper categorization
- Inventory tracking with location management
- Order management with proper state tracking
- Time-based dimensional modeling

Revision ID: 001
Revises: 
Create Date: 2025-01-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the complete boat parts warehouse schema."""
    
    # =========================================================================
    # PARTY MANAGEMENT - Silverston's Universal Data Model for Parties
    # =========================================================================
    
    # Party types lookup
    op.create_table('party_type',
        sa.Column('party_type_id', sa.Integer(), nullable=False),
        sa.Column('party_type_name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('party_type_id'),
        sa.UniqueConstraint('party_type_name')
    )
    
    # Base party table - universal party model
    op.create_table('party',
        sa.Column('party_id', sa.Integer(), nullable=False),
        sa.Column('party_type_id', sa.Integer(), nullable=False),
        sa.Column('party_name', sa.String(255), nullable=False),
        sa.Column('external_id', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('party_id'),
        sa.ForeignKeyConstraint(['party_type_id'], ['party_type.party_type_id']),
        sa.Index('idx_party_type', 'party_type_id'),
        sa.Index('idx_party_external_id', 'external_id')
    )
    
    # Person details (subtype of party)
    op.create_table('person',
        sa.Column('party_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('middle_name', sa.String(100)),
        sa.Column('title', sa.String(50)),
        sa.Column('birth_date', sa.Date()),
        sa.Column('gender', sa.String(10)),
        sa.PrimaryKeyConstraint('party_id'),
        sa.ForeignKeyConstraint(['party_id'], ['party.party_id'], ondelete='CASCADE')
    )
    
    # Organization details (subtype of party)
    op.create_table('organization',
        sa.Column('party_id', sa.Integer(), nullable=False),
        sa.Column('organization_name', sa.String(255), nullable=False),
        sa.Column('tax_id', sa.String(50)),
        sa.Column('duns_number', sa.String(20)),
        sa.Column('industry_code', sa.String(20)),
        sa.Column('founded_date', sa.Date()),
        sa.Column('employee_count', sa.Integer()),
        sa.PrimaryKeyConstraint('party_id'),
        sa.ForeignKeyConstraint(['party_id'], ['party.party_id'], ondelete='CASCADE')
    )
    
    # Party relationships (customer, supplier, etc.)
    op.create_table('party_relationship_type',
        sa.Column('relationship_type_id', sa.Integer(), nullable=False),
        sa.Column('relationship_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.PrimaryKeyConstraint('relationship_type_id'),
        sa.UniqueConstraint('relationship_name')
    )
    
    op.create_table('party_relationship',
        sa.Column('party_relationship_id', sa.Integer(), nullable=False),
        sa.Column('from_party_id', sa.Integer(), nullable=False),
        sa.Column('to_party_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type_id', sa.Integer(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('through_date', sa.Date()),
        sa.Column('comment', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('party_relationship_id'),
        sa.ForeignKeyConstraint(['from_party_id'], ['party.party_id']),
        sa.ForeignKeyConstraint(['to_party_id'], ['party.party_id']),
        sa.ForeignKeyConstraint(['relationship_type_id'], ['party_relationship_type.relationship_type_id']),
        sa.Index('idx_party_rel_from', 'from_party_id'),
        sa.Index('idx_party_rel_to', 'to_party_id'),
        sa.Index('idx_party_rel_type', 'relationship_type_id')
    )
    
    # =========================================================================
    # PRODUCT CATALOG - Hierarchical Product Management
    # =========================================================================
    
    # Product categories (hierarchical)
    op.create_table('product_category',
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('parent_category_id', sa.Integer()),
        sa.Column('category_name', sa.String(255), nullable=False),
        sa.Column('category_code', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('category_id'),
        sa.ForeignKeyConstraint(['parent_category_id'], ['product_category.category_id']),
        sa.UniqueConstraint('category_code'),
        sa.Index('idx_category_parent', 'parent_category_id'),
        sa.Index('idx_category_code', 'category_code')
    )
    
    # Product types
    op.create_table('product_type',
        sa.Column('product_type_id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.PrimaryKeyConstraint('product_type_id'),
        sa.UniqueConstraint('type_name')
    )
    
    # Products - master data
    op.create_table('product',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_type_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer()),
        sa.Column('manufacturer_party_id', sa.Integer()),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('product_code', sa.String(100)),
        sa.Column('manufacturer_part_number', sa.String(100)),
        sa.Column('upc_code', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('specifications', postgresql.JSONB()),
        sa.Column('weight_lbs', sa.Numeric(10, 3)),
        sa.Column('length_inches', sa.Numeric(8, 2)),
        sa.Column('width_inches', sa.Numeric(8, 2)),
        sa.Column('height_inches', sa.Numeric(8, 2)),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('introduction_date', sa.Date()),
        sa.Column('discontinuation_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('product_id'),
        sa.ForeignKeyConstraint(['product_type_id'], ['product_type.product_type_id']),
        sa.ForeignKeyConstraint(['category_id'], ['product_category.category_id']),
        sa.ForeignKeyConstraint(['manufacturer_party_id'], ['party.party_id']),
        sa.UniqueConstraint('product_code'),
        sa.Index('idx_product_type', 'product_type_id'),
        sa.Index('idx_product_category', 'category_id'),
        sa.Index('idx_product_manufacturer', 'manufacturer_party_id'),
        sa.Index('idx_product_mpn', 'manufacturer_part_number')
    )
    
    # Product compatibility (boats that parts fit)
    op.create_table('boat_model',
        sa.Column('boat_model_id', sa.Integer(), nullable=False),
        sa.Column('manufacturer_party_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(255), nullable=False),
        sa.Column('model_year', sa.Integer()),
        sa.Column('hull_type', sa.String(50)),
        sa.Column('length_feet', sa.Numeric(5, 1)),
        sa.Column('beam_feet', sa.Numeric(5, 1)),
        sa.Column('draft_feet', sa.Numeric(4, 2)),
        sa.Column('displacement_lbs', sa.Integer()),
        sa.Column('fuel_capacity_gallons', sa.Integer()),
        sa.Column('water_capacity_gallons', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('boat_model_id'),
        sa.ForeignKeyConstraint(['manufacturer_party_id'], ['party.party_id']),
        sa.Index('idx_boat_manufacturer', 'manufacturer_party_id'),
        sa.Index('idx_boat_model_year', 'model_year')
    )
    
    op.create_table('product_compatibility',
        sa.Column('compatibility_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('boat_model_id', sa.Integer(), nullable=False),
        sa.Column('compatibility_type', sa.String(50), nullable=False),  # 'fits', 'recommended', 'optional'
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('compatibility_id'),
        sa.ForeignKeyConstraint(['product_id'], ['product.product_id']),
        sa.ForeignKeyConstraint(['boat_model_id'], ['boat_model.boat_model_id']),
        sa.UniqueConstraint('product_id', 'boat_model_id'),
        sa.Index('idx_compat_product', 'product_id'),
        sa.Index('idx_compat_boat', 'boat_model_id')
    )
    
    # =========================================================================
    # FACILITY AND LOCATION MANAGEMENT
    # =========================================================================
    
    # Geographic locations
    op.create_table('geographic_boundary',
        sa.Column('geo_id', sa.Integer(), nullable=False),
        sa.Column('parent_geo_id', sa.Integer()),
        sa.Column('geo_type', sa.String(50), nullable=False),  # country, state, city, etc.
        sa.Column('geo_name', sa.String(255), nullable=False),
        sa.Column('geo_code', sa.String(20)),
        sa.Column('abbreviation', sa.String(10)),
        sa.PrimaryKeyConstraint('geo_id'),
        sa.ForeignKeyConstraint(['parent_geo_id'], ['geographic_boundary.geo_id']),
        sa.Index('idx_geo_parent', 'parent_geo_id'),
        sa.Index('idx_geo_type', 'geo_type')
    )
    
    # Postal addresses
    op.create_table('postal_address',
        sa.Column('postal_address_id', sa.Integer(), nullable=False),
        sa.Column('address_line_1', sa.String(255)),
        sa.Column('address_line_2', sa.String(255)),
        sa.Column('city', sa.String(100)),
        sa.Column('state_province', sa.String(100)),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('country_geo_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('postal_address_id'),
        sa.ForeignKeyConstraint(['country_geo_id'], ['geographic_boundary.geo_id']),
        sa.Index('idx_postal_state', 'state_province'),
        sa.Index('idx_postal_zip', 'postal_code')
    )
    
    # Facilities (warehouses, stores, etc.)
    op.create_table('facility_type',
        sa.Column('facility_type_id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.PrimaryKeyConstraint('facility_type_id'),
        sa.UniqueConstraint('type_name')
    )
    
    op.create_table('facility',
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('facility_type_id', sa.Integer(), nullable=False),
        sa.Column('owner_party_id', sa.Integer()),
        sa.Column('postal_address_id', sa.Integer()),
        sa.Column('facility_name', sa.String(255), nullable=False),
        sa.Column('facility_code', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('square_footage', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('opened_date', sa.Date()),
        sa.Column('closed_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('facility_id'),
        sa.ForeignKeyConstraint(['facility_type_id'], ['facility_type.facility_type_id']),
        sa.ForeignKeyConstraint(['owner_party_id'], ['party.party_id']),
        sa.ForeignKeyConstraint(['postal_address_id'], ['postal_address.postal_address_id']),
        sa.UniqueConstraint('facility_code'),
        sa.Index('idx_facility_type', 'facility_type_id'),
        sa.Index('idx_facility_owner', 'owner_party_id')
    )
    
    # Location within facility (aisle, bin, shelf)
    op.create_table('facility_location',
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('parent_location_id', sa.Integer()),
        sa.Column('location_name', sa.String(100), nullable=False),
        sa.Column('location_type', sa.String(50)),  # aisle, row, shelf, bin
        sa.Column('location_code', sa.String(50)),
        sa.Column('capacity_cubic_feet', sa.Numeric(10, 2)),
        sa.Column('max_weight_lbs', sa.Numeric(10, 2)),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('location_id'),
        sa.ForeignKeyConstraint(['facility_id'], ['facility.facility_id']),
        sa.ForeignKeyConstraint(['parent_location_id'], ['facility_location.location_id']),
        sa.UniqueConstraint('facility_id', 'location_code'),
        sa.Index('idx_location_facility', 'facility_id'),
        sa.Index('idx_location_parent', 'parent_location_id')
    )
    
    # =========================================================================
    # INVENTORY MANAGEMENT
    # =========================================================================
    
    # Inventory item (specific instance of a product at a location)
    op.create_table('inventory_item',
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('facility_id', sa.Integer(), nullable=False),
        sa.Column('location_id', sa.Integer()),
        sa.Column('lot_number', sa.String(100)),
        sa.Column('serial_number', sa.String(100)),
        sa.Column('condition_code', sa.String(20), default='NEW'),  # NEW, USED, REFURBISHED, DAMAGED
        sa.Column('quantity_on_hand', sa.Numeric(12, 3), default=0),
        sa.Column('quantity_available', sa.Numeric(12, 3), default=0),
        sa.Column('quantity_reserved', sa.Numeric(12, 3), default=0),
        sa.Column('unit_cost', sa.Numeric(10, 2)),
        sa.Column('received_date', sa.DateTime(timezone=True)),
        sa.Column('expiration_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('inventory_item_id'),
        sa.ForeignKeyConstraint(['product_id'], ['product.product_id']),
        sa.ForeignKeyConstraint(['facility_id'], ['facility.facility_id']),
        sa.ForeignKeyConstraint(['location_id'], ['facility_location.location_id']),
        sa.Index('idx_inventory_product', 'product_id'),
        sa.Index('idx_inventory_facility', 'facility_id'),
        sa.Index('idx_inventory_location', 'location_id'),
        sa.Index('idx_inventory_lot', 'lot_number'),
        sa.Index('idx_inventory_serial', 'serial_number')
    )
    
    # Inventory transactions (movements, adjustments)
    op.create_table('inventory_transaction_type',
        sa.Column('transaction_type_id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('affects_quantity', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('transaction_type_id'),
        sa.UniqueConstraint('type_name')
    )
    
    op.create_table('inventory_transaction',
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type_id', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(100)),  # Order ID, Transfer ID, etc.
        sa.Column('quantity_change', sa.Numeric(12, 3), nullable=False),
        sa.Column('quantity_after', sa.Numeric(12, 3), nullable=False),
        sa.Column('unit_cost', sa.Numeric(10, 2)),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('comments', sa.Text()),
        sa.Column('created_by_party_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('transaction_id'),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_item.inventory_item_id']),
        sa.ForeignKeyConstraint(['transaction_type_id'], ['inventory_transaction_type.transaction_type_id']),
        sa.ForeignKeyConstraint(['created_by_party_id'], ['party.party_id']),
        sa.Index('idx_inv_trans_item', 'inventory_item_id'),
        sa.Index('idx_inv_trans_type', 'transaction_type_id'),
        sa.Index('idx_inv_trans_date', 'transaction_date'),
        sa.Index('idx_inv_trans_ref', 'reference_id')
    )
    
    # =========================================================================
    # ORDER MANAGEMENT
    # =========================================================================
    
    # Order types and statuses
    op.create_table('order_type',
        sa.Column('order_type_id', sa.Integer(), nullable=False),
        sa.Column('type_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.PrimaryKeyConstraint('order_type_id'),
        sa.UniqueConstraint('type_name')
    )
    
    op.create_table('order_status',
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('status_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_terminal', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('status_id'),
        sa.UniqueConstraint('status_name')
    )
    
    # Order header
    op.create_table('order_header',
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('order_type_id', sa.Integer(), nullable=False),
        sa.Column('customer_party_id', sa.Integer(), nullable=False),
        sa.Column('sales_rep_party_id', sa.Integer()),
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(100)),
        sa.Column('po_number', sa.String(100)),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('requested_ship_date', sa.Date()),
        sa.Column('promised_ship_date', sa.Date()),
        sa.Column('actual_ship_date', sa.Date()),
        sa.Column('billing_address_id', sa.Integer()),
        sa.Column('shipping_address_id', sa.Integer()),
        sa.Column('subtotal_amount', sa.Numeric(12, 2), default=0),
        sa.Column('tax_amount', sa.Numeric(12, 2), default=0),
        sa.Column('shipping_amount', sa.Numeric(12, 2), default=0),
        sa.Column('total_amount', sa.Numeric(12, 2), default=0),
        sa.Column('currency_code', sa.String(3), default='USD'),
        sa.Column('comments', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('order_id'),
        sa.ForeignKeyConstraint(['order_type_id'], ['order_type.order_type_id']),
        sa.ForeignKeyConstraint(['customer_party_id'], ['party.party_id']),
        sa.ForeignKeyConstraint(['sales_rep_party_id'], ['party.party_id']),
        sa.ForeignKeyConstraint(['status_id'], ['order_status.status_id']),
        sa.ForeignKeyConstraint(['billing_address_id'], ['postal_address.postal_address_id']),
        sa.ForeignKeyConstraint(['shipping_address_id'], ['postal_address.postal_address_id']),
        sa.UniqueConstraint('order_number'),
        sa.Index('idx_order_customer', 'customer_party_id'),
        sa.Index('idx_order_date', 'order_date'),
        sa.Index('idx_order_status', 'status_id'),
        sa.Index('idx_order_number', 'order_number')
    )
    
    # Order line items
    op.create_table('order_item',
        sa.Column('order_item_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('quantity_ordered', sa.Numeric(12, 3), nullable=False),
        sa.Column('quantity_shipped', sa.Numeric(12, 3), default=0),
        sa.Column('quantity_cancelled', sa.Numeric(12, 3), default=0),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit_cost', sa.Numeric(10, 2)),
        sa.Column('line_total', sa.Numeric(12, 2)),
        sa.Column('requested_ship_date', sa.Date()),
        sa.Column('promised_ship_date', sa.Date()),
        sa.Column('comments', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('order_item_id'),
        sa.ForeignKeyConstraint(['order_id'], ['order_header.order_id']),
        sa.ForeignKeyConstraint(['product_id'], ['product.product_id']),
        sa.UniqueConstraint('order_id', 'line_number'),
        sa.Index('idx_order_item_order', 'order_id'),
        sa.Index('idx_order_item_product', 'product_id')
    )


def downgrade() -> None:
    """Drop all warehouse schema tables."""
    
    # Drop in reverse order to handle foreign key constraints
    op.drop_table('order_item')
    op.drop_table('order_header')
    op.drop_table('order_status')
    op.drop_table('order_type')
    
    op.drop_table('inventory_transaction')
    op.drop_table('inventory_transaction_type')
    op.drop_table('inventory_item')
    
    op.drop_table('facility_location')
    op.drop_table('facility')
    op.drop_table('facility_type')
    op.drop_table('postal_address')
    op.drop_table('geographic_boundary')
    
    op.drop_table('product_compatibility')
    op.drop_table('boat_model')
    op.drop_table('product')
    op.drop_table('product_type')
    op.drop_table('product_category')
    
    op.drop_table('party_relationship')
    op.drop_table('party_relationship_type')
    op.drop_table('organization')
    op.drop_table('person')
    op.drop_table('party')
    op.drop_table('party_type')