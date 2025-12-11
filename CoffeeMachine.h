#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <nlohmann/json.hpp>
#include "Recipe.h"

using json = nlohmann::json;
using namespace std;

class CoffeeMachine {
private:
    int waterAmount;
    int coffeeAmount;
    int milkAmount;
    int sugarAmount;
    
    int cupsMade; 
    const int MAX_CUPS = 5;

    const string DATA_FILE = "coffee_data.json";

public:
    CoffeeMachine() {
        if (!loadState()) {
            waterAmount = 2000;
            coffeeAmount = 500;
            milkAmount = 1000;
            sugarAmount = 500;
            cupsMade = 0;
            saveState();
        }
    }

    
    void saveState() {
        json j;
        j["water"] = waterAmount;
        j["coffee"] = coffeeAmount;
        j["milk"] = milkAmount;
        j["sugar"] = sugarAmount;
        j["cups"] = cupsMade;

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
            
            waterAmount = j["water"];
            coffeeAmount = j["coffee"];
            milkAmount = j["milk"];
            sugarAmount = j["sugar"];
            cupsMade = j["cups"];
            file.close();
            return true;
        }
        return false;
    }


    string getStatus() {
        return "Water: " + to_string(waterAmount) + "ml | Coffee: " + to_string(coffeeAmount) + 
               "g | Milk: " + to_string(milkAmount) + "ml | Sugar: " + to_string(sugarAmount) + 
               "g | Cups: " + to_string(cupsMade) + "/" + to_string(MAX_CUPS);
    }

    bool isBlocked() const {
        return cupsMade >= MAX_CUPS;
    }

    void serviceClean() {
        cupsMade = 0;
        saveState();
        cout << "[System] Machine cleaned and ready!" << endl;
    }

    void refill() {
        waterAmount = 2000;
        coffeeAmount = 500;
        milkAmount = 1000;
        sugarAmount = 500;
        saveState();
        cout << "[System] All resources refilled!" << endl;
    }

    string makeCoffee(const Recipe& recipe, int sugarLevel) {
        if (isBlocked()) {
            return "ERROR: Machine is dirty! Please clean it.";
        }

        int actualSugar = sugarLevel * 5;

        if (waterAmount < recipe.getWater()) return "ERROR: Not enough water";
        if (coffeeAmount < recipe.getCoffee()) return "ERROR: Not enough coffee";
        if (milkAmount < recipe.getMilk()) return "ERROR: Not enough milk";
        if (sugarAmount < actualSugar) return "ERROR: Not enough sugar";

        waterAmount -= recipe.getWater();
        coffeeAmount -= recipe.getCoffee();
        milkAmount -= recipe.getMilk();
        sugarAmount -= actualSugar;
        cupsMade++;

        saveState();

        return "SUCCESS: Your " + recipe.getName() + " is ready!";
    }

    json getStatusJson() {
        return {
            {"water", waterAmount},
            {"coffee", coffeeAmount},
            {"milk", milkAmount},
            {"sugar", sugarAmount},
            {"cups", cupsMade},
            {"max_cups", MAX_CUPS},
            {"is_blocked", isBlocked()}
        };
    }

};