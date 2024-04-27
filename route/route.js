/**
 * Route for bank.
 */
"use strict";

const express = require("express");
const router  = express.Router();
const funcs    = require("../src/functions.js");

router.get("/index", async (req, res) => {
    let data = {
        title: "Welcome | The Bank"
    };
    data.res = await funcs.getPlantsPre(["Röd", "Vit", "Brun", "Lila", "Rosa", "Aprikos", "Orange", "Gul", "Cerise", "Purpur", "Blålia", "Lime", "Blå"], [0, 500], ["Barrväxter", "Blomsterlök", "Bärbuskar", "Fruktträd", "Häckväxter", "Höstväxter", "Klängsväxter", "Kryddväxter", "Medelhavsväxter", "Perenner", "Prydnadsbuskar", "Prydnadsträd", "Rosor", "Sommarplantor", "Vårblommor"], ["Januari", "Februari", "Mars", "April", "Maj", "Juni", "Juli", "Augusti", "September", "Oktober", "November", "December"]);
    res.render("index", data);
});

router.get("/index/sorted/:colors/:minHeight/:maxHeight/:categories/:months", async (req, res) => {
    let data = {
        title: "Welcome | The Bank"
    };

    let colors = req.params.colors.split(",");
    let height = [parseInt(req.params.minHeight), parseInt(req.params.maxHeight)];
    let categories = req.params.categories.split(",");
    let months = req.params.months.split(",");

    data.selectedColors = colors;
    data.selectedHeight = height;
    data.selectedCategories = categories;
    data.selectedMonths = months;
    data.res = await funcs.getPlantsPre(colors, height, categories, months);
    console.log("Data from get loaded")
    res.render("sorted", data);
});

module.exports = router;