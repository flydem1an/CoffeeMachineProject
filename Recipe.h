#pragma once
#include <string>

class Recipe {
private:
    std::string name;
    int water;
    int coffee;
    int milk;
    int sugar;

public:
    Recipe(std::string n, int w, int c, int m, int s = 0) 
        : name(n), water(w), coffee(c), milk(m), sugar(s) {}

    std::string getName() const { return name; }
    int getWater() const { return water; }
    int getCoffee() const { return coffee; }
    int getMilk() const { return milk; }
    int getSugar() const { return sugar; }
};