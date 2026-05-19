CREATE DATABASE IF NOT EXISTS product_database;
USE product_database;

CREATE TABLE IF NOT EXISTS product (
    tenant_id INT NOT NULL,
    product_id BIGINT AUTO_INCREMENT UNIQUE,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    base_price DECIMAL(12,2) NOT NULL,
    tax_percent DECIMAL(5,2) DEFAULT 0.0,
    PRIMARY KEY (tenant_id, product_id)
);

CREATE TABLE IF NOT EXISTS category (
    tenant_id INT NOT NULL,
    category_id INT AUTO_INCREMENT UNIQUE,
    name VARCHAR(100) NOT NULL,
    parent_category_id INT NULL,
    PRIMARY KEY (tenant_id, category_id)
);

USE product_database;


-- ============================================
-- CATEGORIES
-- ============================================

-- Tenant 1: (20 categories)
INSERT IGNORE INTO category (tenant_id, name, parent_category_id) VALUES
(1, 'Electronica', NULL),
(1, 'Computadores', 1),
(1, 'Laptops', 2),
(1, 'Desktops', 2),
(1, 'Tablets', 2),
(1, 'Accesorios Computadores', 2),
(1, 'Audio', 1),
(1, 'Audifonos', 7),
(1, 'Parlantes', 7),
(1, 'Telefonia', 1),
(1, 'Smartphones', 10),
(1, 'Accesorios Telefonia', 10),
(1, 'Hogar', NULL),
(1, 'Electrodomesticos', 13),
(1, 'Cocina', 13),
(1, 'Limpieza', 13),
(1, 'Deportes', NULL),
(1, 'Ropa Deportiva', 17),
(1, 'Calzado Deportivo', 17),
(1, 'Equipamiento', 17);

-- Tenant 2: (22 categories)
INSERT IGNORE INTO category (tenant_id, name, parent_category_id) VALUES
(2, 'Electronica', NULL),
(2, 'Computadoras', 1),
(2, 'Laptops', 2),
(2, 'Monitores', 2),
(2, 'Componentes PC', 2),
(2, 'Audio', 1),
(2, 'Audifonos', 6),
(2, 'Parlantes', 6),
(2, 'Telefonia', 1),
(2, 'Smartphones', 9),
(2, 'Accesorios', 9),
(2, 'Oficina', NULL),
(2, 'Mobiliario', 12),
(2, 'Papeleria', 12),
(2, 'Equipamiento Oficina', 12),
(2, 'Hogar', NULL),
(2, 'Electrodomesticos', 16),
(2, 'Cocina', 16),
(2, 'Limpieza', 16),
(2, 'Industrial', NULL),
(2, 'Maquinaria', 20),
(2, 'Herramientas', 20);

-- Tenant 3: Chile (18 categories)
INSERT IGNORE INTO category (tenant_id, name, parent_category_id) VALUES
(3, 'Tecnologia', NULL),
(3, 'Computacion', 1),
(3, 'Notebooks', 2),
(3, 'PC Escritorio', 2),
(3, 'Tablets', 2),
(3, 'Audio', 1),
(3, 'Audifonos', 6),
(3, 'Parlantes', 6),
(3, 'Moviles', 1),
(3, 'Celulares', 9),
(3, 'Accesorios Moviles', 9),
(3, 'Hogar', NULL),
(3, 'Electrodomesticos', 12),
(3, 'Menaje', 12),
(3, 'Deportes', NULL),
(3, 'Outdoor', 15),
(3, 'Fitness', 15),
(3, 'Camping', 15);

-- ============================================
-- PRODUCTS
-- ============================================

-- Tenant 1: (80 products)
INSERT IGNORE INTO product (tenant_id, name, category, base_price, tax_percent) VALUES
-- Computers
(1, 'MacBook Pro 14 M3', 'Laptops', 2400.00, 19.00),
(1, 'MacBook Air 13 M2', 'Laptops', 1300.00, 19.00),
(1, 'Dell XPS 15', 'Laptops', 2100.00, 19.00),
(1, 'Lenovo ThinkPad X1', 'Laptops', 1850.00, 19.00),
(1, 'HP Spectre x360', 'Laptops', 1500.00, 19.00),
(1, 'ASUS ROG Zephyrus', 'Laptops', 1900.00, 19.00),
(1, 'Acer Swift 3', 'Laptops', 850.00, 19.00),
(1, 'MSI Stealth 16', 'Laptops', 2200.00, 19.00),
(1, 'PC Gaming i7', 'Desktops', 1200.00, 19.00),
(1, 'PC Oficina i5', 'Desktops', 650.00, 19.00),
(1, 'Mac Mini M2', 'Desktops', 700.00, 19.00),
(1, 'iPad Pro 12.9', 'Tablets', 1100.00, 19.00),
(1, 'iPad Air', 'Tablets', 600.00, 19.00),
(1, 'Samsung Galaxy Tab S9', 'Tablets', 850.00, 19.00),
(1, 'Lenovo Tab P12', 'Tablets', 450.00, 19.00),
-- Computer Accessories
(1, 'Mouse Logitech MX Master 3', 'Accesorios Computadores', 80.00, 19.00),
(1, 'Teclado Mecanico Keychron K2', 'Accesorios Computadores', 120.00, 19.00),
(1, 'Monitor LG 27 4K', 'Accesorios Computadores', 450.00, 19.00),
(1, 'Monitor Dell 24', 'Accesorios Computadores', 280.00, 19.00),
(1, 'SSD Samsung 1TB', 'Accesorios Computadores', 120.00, 19.00),
(1, 'RAM Kingston 16GB', 'Accesorios Computadores', 80.00, 19.00),
(1, 'Webcam Logitech C920', 'Accesorios Computadores', 90.00, 19.00),
(1, 'Base Refrigerante', 'Accesorios Computadores', 35.00, 19.00),
(1, 'Laptop Stand', 'Accesorios Computadores', 45.00, 19.00),
(1, 'Hub USB-C', 'Accesorios Computadores', 50.00, 19.00),
-- Audio
(1, 'Audifonos Sony WH-1000XM5', 'Audifonos', 350.00, 19.00),
(1, 'Audifonos Apple AirPods Pro 2', 'Audifonos', 230.00, 19.00),
(1, 'Audifonos JBL Tune 510BT', 'Audifonos', 60.00, 19.00),
(1, 'Audifonos Bose QC45', 'Audifonos', 320.00, 19.00),
(1, 'Audifonos Razer BlackShark', 'Audifonos', 120.00, 19.00),
(1, 'Audifonos HyperX Cloud', 'Audifonos', 90.00, 19.00),
(1, 'Parlante JBL Charge 5', 'Parlantes', 180.00, 19.00),
(1, 'Parlante Bose SoundLink', 'Parlantes', 300.00, 19.00),
(1, 'Parlante Sony SRS-XB13', 'Parlantes', 60.00, 19.00),
(1, 'Parlante Marshall Emberton', 'Parlantes', 150.00, 19.00),
(1, 'Parlante Harman Kardon', 'Parlantes', 250.00, 19.00),
-- Telephony
(1, 'iPhone 15 Pro', 'Smartphones', 1200.00, 19.00),
(1, 'iPhone 15', 'Smartphones', 900.00, 19.00),
(1, 'Samsung Galaxy S24 Ultra', 'Smartphones', 1300.00, 19.00),
(1, 'Samsung Galaxy S24+', 'Smartphones', 1100.00, 19.00),
(1, 'Google Pixel 8 Pro', 'Smartphones', 1000.00, 19.00),
(1, 'Xiaomi 13 Pro', 'Smartphones', 800.00, 19.00),
(1, 'Motorola Edge 40', 'Smartphones', 550.00, 19.00),
(1, 'Cargador USB-C 65W', 'Accesorios Telefonia', 35.00, 19.00),
(1, 'Funda iPhone Silicon', 'Accesorios Telefonia', 25.00, 19.00),
(1, 'Protector Pantalla Vidrio', 'Accesorios Telefonia', 15.00, 19.00),
(1, 'Power Bank 20000mAh', 'Accesorios Telefonia', 45.00, 19.00),
(1, 'Soporte Ventilacion', 'Accesorios Telefonia', 20.00, 19.00),
-- Appliances
(1, 'Licuadora Oster', 'Electrodomesticos', 90.00, 19.00),
(1, 'Batidora KitchenAid', 'Electrodomesticos', 350.00, 19.00),
(1, 'Cafetera Nespresso', 'Electrodomesticos', 120.00, 19.00),
(1, 'Freidora de Aire Ninja', 'Electrodomesticos', 200.00, 19.00),
(1, 'Aspiradora Robot Roomba', 'Electrodomesticos', 450.00, 19.00),
(1, 'Microondas Samsung', 'Electrodomesticos', 180.00, 19.00),
(1, 'Nevera No Frost', 'Electrodomesticos', 1200.00, 19.00),
(1, 'Lavadora Samsung', 'Electrodomesticos', 650.00, 19.00),
(1, 'Hervidor Electrico', 'Cocina', 45.00, 19.00),
(1, 'Set de Ollas Tefal', 'Cocina', 80.00, 19.00),
(1, 'Juego de Cuchillos', 'Cocina', 60.00, 19.00),
(1, 'Sarten Antiadherente', 'Cocina', 35.00, 19.00),
(1, 'Aspiradora Manual', 'Limpieza', 55.00, 19.00),
(1, 'Trapero Giratorio', 'Limpieza', 40.00, 19.00),
-- Sports
(1, 'Camiseta Deportiva Nike', 'Ropa Deportiva', 45.00, 19.00),
(1, 'Pantaloneta Adidas', 'Ropa Deportiva', 40.00, 19.00),
(1, 'Chaqueta Running', 'Ropa Deportiva', 80.00, 19.00),
(1, 'Zapatillas Running Nike', 'Calzado Deportivo', 120.00, 19.00),
(1, 'Zapatillas Adidas Ultraboost', 'Calzado Deportivo', 180.00, 19.00),
(1, 'Zapatillas Puma', 'Calzado Deportivo', 100.00, 19.00),
(1, 'Pesas 2.5kg', 'Equipamiento', 25.00, 19.00),
(1, 'Esterilla Yoga', 'Equipamiento', 30.00, 19.00),
(1, 'Balon de Futbol', 'Equipamiento', 35.00, 19.00),
(1, 'Raqueta Tenis', 'Equipamiento', 60.00, 19.00),
(1, 'Kit de Pesas', 'Equipamiento', 120.00, 19.00),
(1, 'Cuerda para Saltar', 'Equipamiento', 15.00, 19.00);

-- Tenant 2: (75 products)
INSERT IGNORE INTO product (tenant_id, name, category, base_price, tax_percent) VALUES
-- Laptops
(2, 'MacBook Pro 16 M3', 'Laptops', 2800.00, 18.00),
(2, 'Microsoft Surface Laptop 5', 'Laptops', 1450.00, 18.00),
(2, 'Lenovo Legion 5', 'Laptops', 1600.00, 18.00),
(2, 'HP Victus 16', 'Laptops', 1100.00, 18.00),
(2, 'ASUS TUF Gaming', 'Laptops', 1300.00, 18.00),
-- Monitors
(2, 'Monitor ASUS ProArt 32', 'Monitores', 800.00, 18.00),
(2, 'Monitor Dell UltraSharp 27', 'Monitores', 550.00, 18.00),
(2, 'Monitor LG UltraGear 27', 'Monitores', 450.00, 18.00),
(2, 'Monitor Samsung Odyssey', 'Monitores', 600.00, 18.00),
(2, 'Monitor Acer 24', 'Monitores', 250.00, 18.00),
-- Components
(2, 'Tarjeta RTX 4060', 'Componentes PC', 450.00, 18.00),
(2, 'Procesador Intel i7', 'Componentes PC', 380.00, 18.00),
(2, 'Placa Madre ASUS', 'Componentes PC', 220.00, 18.00),
(2, 'Fuente 750W', 'Componentes PC', 120.00, 18.00),
-- Audio
(2, 'Audifonos Logitech G435', 'Audifonos', 70.00, 18.00),
(2, 'Audifonos Redragon', 'Audifonos', 45.00, 18.00),
(2, 'Audifonos Trust', 'Audifonos', 35.00, 18.00),
(2, 'Parlante JBL Go 3', 'Parlantes', 50.00, 18.00),
(2, 'Parlante Sony XB100', 'Parlantes', 70.00, 18.00),
-- Smartphones
(2, 'iPhone 14', 'Smartphones', 800.00, 18.00),
(2, 'Samsung A54', 'Smartphones', 400.00, 18.00),
(2, 'Xiaomi Redmi Note 12', 'Smartphones', 250.00, 18.00),
(2, 'Motorola G84', 'Smartphones', 350.00, 18.00),
(2, 'Google Pixel 7', 'Smartphones', 550.00, 18.00),
(2, 'iPhone 13', 'Smartphones', 650.00, 18.00),
(2, 'Samsung S23 FE', 'Smartphones', 600.00, 18.00),
-- Accessories
(2, 'Cargador Inalambrico', 'Accesorios', 30.00, 18.00),
(2, 'Funda Silicona', 'Accesorios', 15.00, 18.00),
(2, 'Vidrio Templado', 'Accesorios', 10.00, 18.00),
(2, 'Adaptador USB', 'Accesorios', 8.00, 18.00),
-- Furniture
(2, 'Silla Ergo.', 'Mobiliario', 350.00, 18.00),
(2, 'Escritorio Ajustable', 'Mobiliario', 280.00, 18.00),
(2, 'Silla Ejecutiva', 'Mobiliario', 250.00, 18.00),
(2, 'Estante Metalico', 'Mobiliario', 120.00, 18.00),
-- Stationery
(2, 'Resma Papel Oficio', 'Papeleria', 12.00, 18.00),
(2, 'Marcadores Permanentes', 'Papeleria', 8.00, 18.00),
(2, 'Cuaderno Profesional', 'Papeleria', 15.00, 18.00),
(2, 'Boligrafos Gel', 'Papeleria', 5.00, 18.00),
-- Office Equipment
(2, 'Proyector Epson', 'Equipamiento Oficina', 450.00, 18.00),
(2, 'Enmicadora', 'Equipamiento Oficina', 80.00, 18.00),
(2, 'Destructora Papel', 'Equipamiento Oficina', 120.00, 18.00),
-- Appliances
(2, 'Licuadora Oster', 'Electrodomesticos', 80.00, 18.00),
(2, 'Microondas Mabe', 'Electrodomesticos', 150.00, 18.00),
(2, 'Refrigeradora Indurama', 'Electrodomesticos', 800.00, 18.00),
(2, 'Lavadora LG', 'Electrodomesticos', 550.00, 18.00),
-- Kitchen
(2, 'Cocina Electrica', 'Cocina', 180.00, 18.00),
(2, 'Hervidor Electrico', 'Cocina', 40.00, 18.00),
(2, 'Set de Ollas', 'Cocina', 95.00, 18.00),
(2, 'Sarten Profesional', 'Cocina', 45.00, 18.00),
-- Cleaning
(2, 'Detergente Liquido', 'Limpieza', 15.00, 18.00),
(2, 'Escoba Multisuperficie', 'Limpieza', 20.00, 18.00),
(2, 'Aspiradora Portatil', 'Limpieza', 70.00, 18.00),
-- Industrial Machinery
(2, 'Excavadora Caterpillar', 'Maquinaria', 45000.00, 0.00),
(2, 'Retroexcavadora JCB', 'Maquinaria', 38000.00, 0.00),
(2, 'Montacargas Toyota', 'Maquinaria', 25000.00, 0.00),
(2, 'Compactador Dynapac', 'Maquinaria', 32000.00, 0.00),
-- Tools
(2, 'Taladro Percutor', 'Herramientas', 120.00, 18.00),
(2, 'Esmeril Angular', 'Herramientas', 80.00, 18.00),
(2, 'Sierra Circular', 'Herramientas', 150.00, 18.00),
(2, 'Caja de Herramientas', 'Herramientas', 200.00, 18.00),
(2, 'Compresor de Aire', 'Herramientas', 350.00, 18.00);

-- Tenant 3: (70 products)
INSERT IGNORE INTO product (tenant_id, name, category, base_price, tax_percent) VALUES
-- Notebooks
(3, 'MacBook Air M1', 'Notebooks', 950.00, 19.00),
(3, 'Dell Latitude 5430', 'Notebooks', 1200.00, 19.00),
(3, 'Lenovo IdeaPad 3', 'Notebooks', 550.00, 19.00),
(3, 'HP Pavilion 15', 'Notebooks', 700.00, 19.00),
(3, 'Acer Aspire 5', 'Notebooks', 650.00, 19.00),
(3, 'ASUS Vivobook', 'Notebooks', 600.00, 19.00),
-- Desktop PCs
(3, 'PC All-in-One HP', 'PC Escritorio', 800.00, 19.00),
(3, 'PC Gamer Armada', 'PC Escritorio', 1100.00, 19.00),
(3, 'Mini PC Intel', 'PC Escritorio', 350.00, 19.00),
(3, 'PC Oficina', 'PC Escritorio', 500.00, 19.00),
-- Tablets
(3, 'iPad 10.9', 'Tablets', 500.00, 19.00),
(3, 'Samsung Tab A8', 'Tablets', 250.00, 19.00),
(3, 'Lenovo Tab M10', 'Tablets', 180.00, 19.00),
(3, 'Huawei MatePad', 'Tablets', 300.00, 19.00),
-- Audio
(3, 'Audifonos Sony WH-CH510', 'Audifonos', 80.00, 19.00),
(3, 'Audifonos Huawei FreeBuds', 'Audifonos', 100.00, 19.00),
(3, 'Audifonos Xiaomi', 'Audifonos', 40.00, 19.00),
(3, 'Parlante Bose', 'Parlantes', 200.00, 19.00),
(3, 'Parlante Sony', 'Parlantes', 90.00, 19.00),
(3, 'Parlante JBL', 'Parlantes', 120.00, 19.00),
-- Cell Phones
(3, 'iPhone 15', 'Celulares', 850.00, 19.00),
(3, 'Samsung S24', 'Celulares', 800.00, 19.00),
(3, 'Xiaomi 13', 'Celulares', 500.00, 19.00),
(3, 'Motorola G54', 'Celulares', 250.00, 19.00),
(3, 'Google Pixel 8', 'Celulares', 650.00, 19.00),
-- Mobile Accessories
(3, 'Cargador Rapido', 'Accesorios Moviles', 25.00, 19.00),
(3, 'Funda Transparente', 'Accesorios Moviles', 12.00, 19.00),
(3, 'Protector Pantalla', 'Accesorios Moviles', 10.00, 19.00),
(3, 'Power Bank', 'Accesorios Moviles', 35.00, 19.00),
-- Appliances
(3, 'Licuadora Philips', 'Electrodomesticos', 70.00, 19.00),
(3, 'Cafetera Dolce Gusto', 'Electrodomesticos', 100.00, 19.00),
(3, 'Freidora Air Fryer', 'Electrodomesticos', 150.00, 19.00),
(3, 'Aspiradora Karcher', 'Electrodomesticos', 200.00, 19.00),
(3, 'Microondas LG', 'Electrodomesticos', 140.00, 19.00),
-- Tableware
(3, 'Set de Ollas', 'Menaje', 70.00, 19.00),
(3, 'Juego de Platos', 'Menaje', 45.00, 19.00),
(3, 'Cubiertos', 'Menaje', 30.00, 19.00),
(3, 'Vajilla 12 piezas', 'Menaje', 60.00, 19.00),
-- Outdoor
(3, 'Carpa 4 personas', 'Outdoor', 120.00, 19.00),
(3, 'Linterna LED', 'Outdoor', 25.00, 19.00),
(3, 'Mochila Trekking', 'Outdoor', 80.00, 19.00),
-- Fitness
(3, 'Colchoneta Yoga', 'Fitness', 25.00, 19.00),
(3, 'Mancuernas 5kg', 'Fitness', 40.00, 19.00),
(3, 'Kit Elasticos', 'Fitness', 20.00, 19.00),
(3, 'Pelota Fitness', 'Fitness', 15.00, 19.00),
-- Camping
(3, 'Hoguera Portatil', 'Camping', 45.00, 19.00),
(3, 'Saco Dormir', 'Camping', 60.00, 19.00),
(3, 'Baston Trekking', 'Camping', 35.00, 19.00);