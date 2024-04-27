/**
 * A module exporting functions to access the bank database.
 */
"use strict";

module.exports = {
    getPlants,
    getPlantsPre
};

const mysql  = require("promise-mysql");
const config = require("../config/db/config.json");
const { merge } = require("../route/route");
let db;

(async function() {
    db = await mysql.createConnection(config);

    process.on("exit", () => {
        db.end();
    });
})();

async function getPlants(color, minHeight, maxHeight, category, month) {
    let sql = `CALL get_plants(?, ?, ?, ?, ?)`;
    try {
        const res = await db.query(sql, [minHeight, maxHeight, color, category, month]);
        return res[0]
    } catch (error) {
        console.error("Error executing query:", error);
        throw error;
    }
}

async function getPlantsPre(colors = [], height = [], categories = [], months = []) {
    try {

        const promises = [];
        categories.forEach(category => {
            colors.forEach(color => {
                months.forEach(month => {
                    promises.push(getPlants(color, height[0], height[1], category, month));
                })
            });
        });

        const resDirty = await Promise.all(promises);
        const uniqueMap = new Map();

        // Add objects from the responses to the map
        resDirty.forEach(res => {
            res.forEach(obj => {
                uniqueMap.set(obj.name, obj);
            });
        });
        const mergedResponse = Array.from(uniqueMap.values());

        // Sort mergedResponse by category
        mergedResponse.sort((a, b) => {
            if (a.category < b.category) return -1;
            if (a.category > b.category) return 1;
            return 0;
        });
        return mergedResponse;
    } catch (error) {
        console.error("Error in getPlantsPre:", error);
        throw error;
    }
}
