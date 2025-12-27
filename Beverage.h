#pragma once
#include <string>
#include <iostream>

using namespace std;

class Beverage {
protected:
    string name;
    int price;
    int waterNeeded; 
    int coffeeNeeded;
    int milkNeeded;
    int sugarNeeded;

public:
    Beverage(string n, int p, int w, int c, int m, int s) 
        : name(n), price(p), waterNeeded(w), coffeeNeeded(c), milkNeeded(m), sugarNeeded(s) {}

    virtual ~Beverage() {}

    virtual string prepare() const = 0; 

    string getName() const { return name; }
    int getPrice() const { return price; }
    int getWater() const { return waterNeeded; }
    int getCoffee() const { return coffeeNeeded; }
    int getMilk() const { return milkNeeded; }
    int getSugar() const { return sugarNeeded; }
};