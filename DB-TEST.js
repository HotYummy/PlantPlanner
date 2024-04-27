"use strict";

const mysql = require("promise-mysql");
const config = {
    "host":     "DESKTOP-N9CNRBA.local",
    "user":     "dbadm",
    "password": "BAsse123//",
    "database": "blomsterlandet",
    "multipleStatements": true
};

async function establishDBConnection() {
    const db = await mysql.createConnection(config);
    console.log("Database connection established successfully.");
    return db;
}

async function getPlants(db, colors = [], height = []) {
    let sql = `CALL get_plants(?, ?, ?)`;
    try {
        const res = await db.query(sql, [0, 500, "Röd"]);
        console.table(res[0]);
        return res[0];
    } catch (error) {
        console.error("Error executing query:", error);
        throw error;
    }
}

module.exports = {
    establishDBConnection,
    getPlants
};
