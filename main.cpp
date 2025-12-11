#include <iostream>
#include "CoffeeMachine.h"
#include "Recipe.h"

using namespace std;

int main() {
    cout << "--- Starting Coffee Machine System ---" << endl;

    CoffeeMachine myMachine;
    
    cout << "Current Status: " << myMachine.getStatus() << endl;

    Recipe espresso("Espresso", 50, 10, 0);       
    Recipe cappuccino("Cappuccino", 50, 10, 100); 

    cout << "\nOrder: Espresso (2 sugar)..." << endl;
    string result = myMachine.makeCoffee(espresso, 2);
    cout << "Machine says: " << result << endl;

    cout << "Status after: " << myMachine.getStatus() << endl;

    return 0;
}