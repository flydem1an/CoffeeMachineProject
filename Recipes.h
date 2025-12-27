#pragma once
#include "Beverage.h"

class Espresso : public Beverage {
public:
    Espresso() : Beverage("Espresso", 30, 30, 10, 0, 0) {} 
    string prepare() const override { return "Brewing under high pressure..."; }
};

class Americano : public Beverage {
public:
    Americano() : Beverage("Americano", 35, 120, 10, 0, 0) {} 
    string prepare() const override { return "Brewing espresso and adding hot water..."; }
};

class Cappuccino : public Beverage {
public:
    Cappuccino() : Beverage("Cappuccino", 45, 100, 10, 100, 0) {} 
    string prepare() const override { return "Steaming milk foam and mixing..."; }
};

class Latte : public Beverage {
public:
    Latte() : Beverage("Latte", 50, 150, 10, 150, 0) {} 
    string prepare() const override { return "Pouring gentle milk layers..."; }
};

class Raf : public Beverage {
public:
    Raf() : Beverage("Raf Coffee", 55, 30, 10, 200, 5) {} 
    string prepare() const override { return "Whipping espresso with cream and vanilla..."; }
};

class CustomBeverage : public Beverage {
public:
    CustomBeverage(string n, int w, int c, int m, int s) 
        : Beverage(n, 60, w, c, m, s) {}

    string prepare() const override {
        return "Brewing custom recipe '" + name + "'..."; 
    }
};