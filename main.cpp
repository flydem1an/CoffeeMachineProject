#include <iostream>
#include "httplib.h"
#include "CoffeeMachine.h"
#include "Recipes.h" 

using namespace std;
using namespace httplib;

int main() {
    Server svr;
    CoffeeMachine machine;

    cout << "--- Smart Coffee Server (OOP Edition) started on 8080 ---" << endl;

    svr.Get("/status", [&](const Request& req, Response& res) {
        res.set_content(machine.getStatusJson().dump(), "application/json");
    });

    svr.Post("/refill", [&](const Request& req, Response& res) {
        machine.refill();
        res.set_content("{\"status\":\"success\", \"message\": \"Refilled\"}", "application/json");
    });

    svr.Post("/clean", [&](const Request& req, Response& res) {
        machine.serviceClean();
        res.set_content("{\"status\":\"success\", \"message\": \"Cleaned\"}", "application/json");
    });

    svr.Post("/make", [&](const Request& req, Response& res) {
        try {
            auto body = json::parse(req.body);
            string type = body["type"];
            int sugar = body.value("sugar", 0);

            Beverage* drink = nullptr;

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
                } else {
                    response["status"] = "success";
                    response["message"] = result;
                }
                
                delete drink;
                res.set_content(response.dump(), "application/json");
            } else {
                res.status = 400;
                res.set_content("{\"status\":\"error\", \"message\": \"Unknown drink\"}", "application/json");
            }

        } catch (...) {
            res.status = 400;
            res.set_content("{\"status\":\"error\", \"message\": \"Invalid JSON\"}", "application/json");
        }
    });

    svr.listen("0.0.0.0", 8080);
    return 0;
}