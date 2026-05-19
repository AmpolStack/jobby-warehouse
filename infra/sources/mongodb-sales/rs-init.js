const rsConfig = {
    _id: "rs0",
    members: [{ _id: 0, host: "sales-database:27017" }]
};
let initiated = false;
try {
    const status = rs.status();
    if (status.ok === 1) {
        print("Replica set already initiated, skipping rs.initiate().");
        initiated = true;
    }
} catch (e) {
}

if (!initiated) {
    const result = rs.initiate(rsConfig);
    if (result.ok !== 1) {
        print("ERROR initiating replica set: " + JSON.stringify(result));
        quit(1);
    }
    print("Replica set initiated successfully.");
}

print("Waiting for node to become PRIMARY...");
let retries = 30;
while (retries-- > 0) {
    const state = rs.status().myState;
    if (state === 1) {
        print("Node is PRIMARY. Waiting for stabilization...");
        sleep(2000);
        print("Continuing with initialization.");
        break;
    }
    sleep(1000);
}
if (retries <= 0) {
    print("ERROR: Node did not reach PRIMARY state in time.");
    quit(1);
}

const adminDb = db.getSiblingDB('admin');
adminDb.auth('root', 'root');

if (!adminDb.getUser('debezium_user')) {
    adminDb.createUser({
        user: "debezium_user",
        pwd: "debezium_pass",
        roles: [
            { role: "read", db: "admin" },
            { role: "readAnyDatabase", db: "admin" },
            { role: "clusterMonitor", db: "admin" }
        ],
        mechanisms: ["SCRAM-SHA-256"]
    });
    print("User debezium_user created.");
} else {
    print("User debezium_user already exists, skipping creation.");
}

const salesDb = db.getSiblingDB('sales_database');

if (salesDb.orders.countDocuments() === 0) {
    salesDb.createCollection('orders');
    salesDb.createCollection('orderLines');

    salesDb.orders.createIndex({ "tenant_id": 1, "orderDate": -1 });
    salesDb.orders.createIndex({ "tenant_id": 1, "customerId": 1 });
    salesDb.orders.createIndex({ "tenant_id": 1, "employeeId": 1 });
    salesDb.orders.createIndex({ "tenant_id": 1, "branchId": 1 });
    salesDb.orders.createIndex({ "tenant_id": 1, "status": 1 });
    salesDb.orders.createIndex({ "tenant_id": 1, "paymentMethodId": 1 });
    salesDb.orders.createIndex({ "orderId": 1 }, { unique: true });
    salesDb.orders.createIndex({ "createdAt": -1 });

    salesDb.orderLines.createIndex({ "tenant_id": 1, "orderId": 1 });
    salesDb.orderLines.createIndex({ "tenant_id": 1, "orderId": 1, "productId": 1 });
    salesDb.orderLines.createIndex({ "tenant_id": 1, "eventType": 1, "timestamp": -1 });
    salesDb.orderLines.createIndex({ "lineId": 1, "seq": 1 });
    salesDb.orderLines.createIndex({ "timestamp": -1 });

    const PAYMENT_METHODS = [1, 2, 3, 4, 5];

    const PRODUCTS_BY_TENANT = {
        1: [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010],
        2: [7001, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7010],
        3: [8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]
    };

    const CUSTOMERS_BY_TENANT = {
        1: [10001, 10002, 10003, 10004, 10005],
        2: [20001, 20002, 20003, 20004, 20005],
        3: [30001, 30002, 30003, 30004, 30005]
    };

    const EMPLOYEES_BY_TENANT = {
        1: [2001, 2002, 2003, 2004, 2005],
        2: [4001, 4002, 4003, 4004, 4005],
        3: [5001, 5002, 5003, 5004, 5005]
    };

    const BRANCHES_BY_TENANT = {
        1: [301, 302, 303, 304, 305],
        2: [601, 602, 603, 604, 605],
        3: [801, 802, 803, 804, 805]
    };

    const PRODUCT_INFO = {
        default: { unitPrice: 100.00, taxRate: 0.19, cost: 60.00 }
    };

    const randomDate = (startDate, endDate) => {
        return new Date(startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime()));
    };

    const randomItem = (arr) => {
        return arr[Math.floor(Math.random() * arr.length)];
    };

    const randomInt = (min, max) => {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    };

    const getProductInfo = (productId) => {
        return PRODUCT_INFO[productId] || PRODUCT_INFO.default;
    };

    const generateOrderId = (tenantId, orderNum) => {
        return `ORD-${tenantId}${String(orderNum).padStart(5, '0')}`;
    };

    const generateLineId = (orderId, productId, seq) => {
        return `LINE-${orderId.substring(4)}-${productId}-${seq}`;
    };

    const startDate = new Date("2025-01-01T00:00:00Z");
    const endDate = new Date("2026-12-31T23:59:59Z");

    let orders = [];
    let orderLines = [];

    const TENANTS = [1, 2, 3];

    for (let tenant of TENANTS) {
        const products = PRODUCTS_BY_TENANT[tenant];
        const customers = CUSTOMERS_BY_TENANT[tenant];
        const employees = EMPLOYEES_BY_TENANT[tenant];
        const branches = BRANCHES_BY_TENANT[tenant];

        let ordersPerTenant = 1500;
        if (tenant === 1) ordersPerTenant = 1600;
        if (tenant === 3) ordersPerTenant = 1400;

        print(`Generating ${ordersPerTenant} orders for tenant ${tenant}`);

        for (let i = 0; i < ordersPerTenant; i++) {
            const orderNum = i + 1;
            const orderId = generateOrderId(tenant, orderNum);
            const orderDate = randomDate(startDate, endDate);
            const customerId = randomItem(customers);
            const employeeId = randomItem(employees);
            const branchId = randomItem(branches);
            const paymentMethodId = randomItem(PAYMENT_METHODS);

            const numProducts = randomInt(1, 4);
            let totalAmount = 0;
            let lineItems = [];

            for (let idx = 0; idx < numProducts; idx++) {
                const productId = randomItem(products);
                const productInfo = getProductInfo(productId);
                const quantity = randomInt(1, 3);
                const unitPrice = productInfo.unitPrice;
                const discount = Math.random() > 0.8 ? parseFloat((unitPrice * quantity * 0.1).toFixed(2)) : 0;
                const subtotal = quantity * unitPrice - discount;
                const tax = subtotal * productInfo.taxRate;
                const totalLine = subtotal + tax;
                totalAmount += totalLine;

                const lineId = generateLineId(orderId, productId, idx + 1);
                const timestampCreated = new Date(orderDate.getTime() + (idx + 1) * 1000);
                const timestampPaid = new Date(timestampCreated.getTime() + 30000 + Math.random() * 30000);

                lineItems.push({
                    lineId: lineId, orderId: orderId, tenant_id: tenant, productId: productId,
                    quantity: quantity, unitPrice: unitPrice, discount: discount,
                    cost: productInfo.cost, taxRate: productInfo.taxRate,
                    eventType: "created", timestamp: timestampCreated, seq: 1
                });

                lineItems.push({
                    lineId: lineId, orderId: orderId, tenant_id: tenant, productId: productId,
                    quantity: quantity, unitPrice: unitPrice, discount: discount,
                    cost: productInfo.cost, taxRate: productInfo.taxRate,
                    eventType: "paid", timestamp: timestampPaid, seq: 2
                });
            }

            let status = "completed";
            if (Math.random() > 0.85) status = "pending";

            orders.push({
                orderId: orderId, tenant_id: tenant, customerId: customerId,
                employeeId: employeeId, paymentMethodId: paymentMethodId, branchId: branchId,
                orderDate: orderDate, totalAmount: parseFloat(totalAmount.toFixed(2)),
                status: status, createdAt: orderDate, updatedAt: orderDate
            });

            orderLines.push(...lineItems);
        }
    }

    print(`Inserting ${orders.length} orders...`);
    salesDb.orders.insertMany(orders);

    print(`Inserting ${orderLines.length} order lines...`);
    const batchSize = 500;
    for (let i = 0; i < orderLines.length; i += batchSize) {
        const batch = orderLines.slice(i, i + batchSize);
        salesDb.orderLines.insertMany(batch);
        print(`  Inserted batch ${Math.floor(i / batchSize) + 1} of ${Math.ceil(orderLines.length / batchSize)}`);
    }

    print(`SUCCESS: Generated ${orders.length} orders and ${orderLines.length} order lines`);
    print("=========================================");

    print("sales_database initialized successfully.");
    print("Collections: orders, orderLines");
} else {
    print("sales_database already contains data, skipping initial insertion.");
}