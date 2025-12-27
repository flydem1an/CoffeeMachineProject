#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <nlohmann/json.hpp>
#include "Recipes.h" 

using json = nlohmann::json;
using namespace std;

class CoffeeMachine {
private:
    int water, coffee, milk, sugar;
    int cupsMade;
    double totalRevenue;
    const int MAX_CUPS = 20;
    const string DATA_FILE = "coffee_data.json";

public:
    CoffeeMachine() {
        if (!loadState()) {
            refill();
            cupsMade = 0;
            totalRevenue = 0.0;
            saveState();
        }
    }

    void saveState() {
        json j;
        j["water"] = water;
        j["coffee"] = coffee;
        j["milk"] = milk;
        j["sugar"] = sugar;
        j["cups"] = cupsMade;
        j["revenue"] = totalRevenue;

        ofstream file(DATA_FILE);
        if (file.is_open()) {
            file << j.dump(4);
            file.close();
        }
    }

    bool loadState() {
        ifstream file(DATA_FILE);
        if (file.is_open()) {
            json j;
            file >> j;
            water = j.value("water", 2000);
            coffee = j.value("coffee", 500);
            milk = j.value("milk", 1000);
            sugar = j.value("sugar", 500);
            cupsMade = j.value("cups", 0);
            totalRevenue = j.value("revenue", 0.0);
            return true;
        }
        return false;
    }

    json getStatusJson() {
        return {
            {"water", water},
            {"coffee", coffee},
            {"milk", milk},
            {"sugar", sugar},
            {"cups", cupsMade},
            {"max_cups", MAX_CUPS},
            {"is_blocked", cupsMade >= MAX_CUPS},
            {"revenue", totalRevenue}
        };
    }

    void refill() {
        water = 2000; coffee = 500; milk = 1000; sugar = 500;
        saveState();
    }

    void serviceClean() {
        cupsMade = 0;
        saveState();
    }

    string makeDrink(Beverage* drink, int sugarSpoons) {
        if (cupsMade >= MAX_CUPS) return "ERROR: Machine needs cleaning!";

        int totalSugarNeeded = (sugarSpoons * 5) + drink->getSugar();

        if (water < drink->getWater()) return "ERROR: Not enough water";
        if (coffee < drink->getCoffee()) return "ERROR: Not enough coffee";
        if (milk < drink->getMilk()) return "ERROR: Not enough milk";
        if (sugar < totalSugarNeeded) return "ERROR: Not enough sugar";

        water -= drink->getWater();
        coffee -= drink->getCoffee();
        milk -= drink->getMilk();
        sugar -= totalSugarNeeded;
        
        cupsMade++;
        totalRevenue += drink->getPrice();

        saveState();
        
        return "SUCCESS: " + drink->prepare(); 
    }
};