-- MySQL 8+ schema for cleaned online retail line items.
CREATE DATABASE IF NOT EXISTS ecommerce_analytics;
USE ecommerce_analytics;

DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    InvoiceNo VARCHAR(20) NOT NULL,
    StockCode VARCHAR(30),
    Description VARCHAR(255),
    Quantity INT NOT NULL,
    InvoiceDate DATETIME NOT NULL,
    UnitPrice DECIMAL(12, 4) NOT NULL,
    CustomerID VARCHAR(20) NOT NULL,
    Country VARCHAR(100),
    Revenue DECIMAL(14, 4) NOT NULL,
    OrderMonth CHAR(7),
    OrderDate CHAR(10),
    INDEX idx_customer (CustomerID),
    INDEX idx_invoice (InvoiceNo),
    INDEX idx_invoice_date (InvoiceDate),
    INDEX idx_country (Country)
);
