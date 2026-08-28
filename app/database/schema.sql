SET ROLE backend_owner;

CREATE TYPE shipment_status AS ENUM (
    'placed', 'pending', 'shipped', 'in_transit', 'delivered'
);

CREATE TABLE shipments (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    content VARCHAR(30) NOT NULL CHECK (length(trim(content)) > 0),
    weight DECIMAL(4, 2) NOT NULL CHECK (weight > 0 AND weight <= 25),
    status shipment_status NOT NULL DEFAULT 'placed',
    destination INTEGER NOT NULL
);

-- Filstros de GET /shipments
CREATE INDEX shipments_destination_idx ON shipments (destination);
CREATE INDEX shipments_status_idx ON shipments (status);

INSERT INTO shipments (content, weight, status, destination) VALUES
    ('glassware', 0.6, 'placed', 11009),
    ('electronics', 1.2, 'shipped', 24902),
    ('documents', 0.3, 'delivered', 30516),
    ('machinery parts', 5.4, 'in_transit', 11009),
    ('textiles', 2.1, 'placed', 24902),
    ('ceramics', 0.8, 'pending', 30516),
    ('furniture', 12.0, 'delivered', 11009),
    ('office supplies', 0.1, 'shipped', 24902);

RESET ROLE;
