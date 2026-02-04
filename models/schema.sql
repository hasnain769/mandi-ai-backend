-- Multi-tenant separation
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL, -- The link between Twilio and Web
    business_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    item_name TEXT NOT NULL,
    quantity DECIMAL DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'kg',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('SALE', 'PURCHASE', 'ADJUSTMENT')),
    item_name TEXT NOT NULL,
    quantity DECIMAL NOT NULL,
    unit VARCHAR(20),
    rate DECIMAL, -- Price per unit
    total_amount DECIMAL,
    buyer_name TEXT, -- Optional, mostly for SALES
    is_credit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
