#include <iostream>
#include <string>
#include "CoffeeMachine.h"
#include "Recipe.h"

using namespace std;

void showUsage() {
    cout << "Usage: ./coffee_app [command] [sugar_amount]" << endl;
    cout << "Commands: status, espresso, cappuccino, latte, refill, clean" << endl;
}

int main(int argc, char* argv[]) {

    if (argc < 2) {
        showUsage();
        return 1;
    }

    string command = argv[1];
    CoffeeMachine machine;

    if (command == "status") {
        cout << machine.getStatus() << endl;
    }
    else if (command == "refill") {
        machine.refill();
    }
    else if (command == "clean") {
        machine.serviceClean();
    }
    else if (command == "espresso" || command == "cappuccino" || command == "latte") {
        int sugar = 0;
        if (argc >= 3) {
            sugar = stoi(argv[2]);
        }

        Recipe* recipe = nullptr;
        if (command == "espresso") recipe = new Recipe("Espresso", 50, 10, 0);
        else if (command == "cappuccino") recipe = new Recipe("Cappuccino", 50, 10, 100);
        else if (command == "latte") recipe = new Recipe("Latte", 50, 10, 150);

        if (recipe) {
            cout << machine.makeCoffee(*recipe, sugar) << endl;
            delete recipe;
        }
    } 
    else {
        cout << "Unknown command" << endl;
    }

    return 0;
}