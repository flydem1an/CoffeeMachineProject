#include <iostream>
#include <iomanip>
#include <ctime>
#include "httplib.h"
#include "CoffeeMachine.h"
#include "Recipes.h" 

using namespace std;
using namespace httplib;

string getCurrentTime() {
    auto t = time(nullptr);
    auto tm = *localtime(&t);
    ostringstream oss;
    oss << put_time(&tm, "%H:%M:%S");
    return oss.str();
}

int main() {
    Server svr;
    CoffeeMachine machine;

    cout << "==================================================" << endl;
    cout << "   SMART COFFEE SERVER" << endl;
    cout << "   Started at: " << getCurrentTime() << endl;
    cout << "   Listening on port: 8080" << endl;
    cout << "==================================================" << endl;

    svr.Get("/status", [&](const Request& req, Response& res) {
        res.set_content(machine.getStatusJson().dump(), "application/json");
    });

    svr.Post("/refill", [&](const Request& req, Response& res) {
        machine.refill();
        cout << "[" << getCurrentTime() << "] [SERVICE] Tanks refilled by admin." << endl;
        res.set_content("{\"status\":\"success\", \"message\": \"Refilled\"}", "application/json");
    });

    svr.Post("/clean", [&](const Request& req, Response& res) {
        machine.serviceClean();
        cout << "[" << getCurrentTime() << "] [SERVICE] Maintenance cycle completed." << endl;
        res.set_content("{\"status\":\"success\", \"message\": \"Cleaned\"}", "application/json");
    });

    svr.Post("/make", [&](const Request& req, Response& res) {
        try {
            auto body = json::parse(req.body);
            string type = body["type"];
            int sugar = body.value("sugar", 0);

            Beverage* drink = nullptr;

            string displayName = type;
            if(type == "custom") displayName = body.value("name", "Custom Mix");
            
            cout << "[" << getCurrentTime() << "] [ORDER] New request: " << displayName 
                 << " (Sugar: " << sugar << ")" << endl;

            if (type == "espresso") drink = new Espresso();
            else if (type == "americano") drink = new Americano();
            else if (type == "cappuccino") drink = new Cappuccino();
            else if (type == "latte") drink = new Latte();
            else if (type == "raf") drink = new Raf();
            else if (type == "custom") {
                string name = body.value("name", "Custom Mix");
                int w = body.value("water", 100);
                int c = body.value("coffee", 10);
                int m = body.value("milk", 0);
                drink = new CustomBeverage(name, w, c, m, sugar);
            }
            
            if (drink) {
                string result = machine.makeDrink(drink, sugar);
                
                json response;
                if (result.find("ERROR") != string::npos) {
                    response["status"] = "error";
                    response["message"] = result;
                    cout << "   -> [FAIL] " << result << endl;
                } else {
                    response["status"] = "success";
                    response["message"] = result;
                    cout << "   -> [OK] " << result << endl;
                    cout << "   -> [FINANCE] Revenue updated." << endl;
                }
                
                delete drink;
                res.set_content(response.dump(), "application/json");
            } else {
                cout << "   -> [ERROR] Unknown drink type!" << endl;
                res.status = 400;
                res.set_content("{\"status\":\"error\", \"message\": \"Unknown drink\"}", "application/json");
            }

        } catch (...) {
            cout << "   -> [CRITICAL] JSON Parsing Error!" << endl;
            res.status = 400;
            res.set_content("{\"status\":\"error\", \"message\": \"Invalid JSON\"}", "application/json");
        }
    });

    svr.listen("0.0.0.0", 8080);
    return 0;
}