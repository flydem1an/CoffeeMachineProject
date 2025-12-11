#include <iostream>
#include "httplib.h"
#include "CoffeeMachine.h"
#include "Recipe.h"

using namespace std;
using namespace httplib;

int main() {
    Server svr;
    CoffeeMachine machine;

    cout << "--- Coffee Server started on port 8080 ---" << endl;


    svr.Get("/status", [&](const Request& req, Response& res) {
        json status = machine.getStatusJson();
        res.set_content(status.dump(), "application/json");
        cout << "[LOG] Status requested" << endl;
    });

    svr.Post("/clean", [&](const Request& req, Response& res) {
        machine.serviceClean();
        res.set_content("{\"message\": \"Machine cleaned\"}", "application/json");
        cout << "[LOG] Machine cleaned" << endl;
    });

    svr.Post("/refill", [&](const Request& req, Response& res) {
        machine.refill();
        res.set_content("{\"message\": \"Refilled\"}", "application/json");
        cout << "[LOG] Machine refilled" << endl;
    });

    svr.Post("/make", [&](const Request& req, Response& res) {
        try {
            auto body = json::parse(req.body);
            string type = body["type"];
            int sugar = body["sugar"];

            Recipe* recipe = nullptr;
            if (type == "espresso") recipe = new Recipe("Espresso", 50, 10, 0);
            else if (type == "cappuccino") recipe = new Recipe("Cappuccino", 50, 10, 100);
            else if (type == "latte") recipe = new Recipe("Latte", 50, 10, 150);
            else {
                res.status = 400;
                res.set_content("{\"error\": \"Unknown coffee type\"}", "application/json");
                return;
            }

            string resultMsg = machine.makeCoffee(*recipe, sugar);
            delete recipe;

            json response;
            if (resultMsg.find("ERROR") != string::npos) {
                response["status"] = "error";
                response["message"] = resultMsg;
            } else {
                response["status"] = "success";
                response["message"] = resultMsg;
            }
            
            res.set_content(response.dump(), "application/json");
            cout << "[LOG] Made coffee: " << type << endl;

        } catch (...) {
            res.status = 400;
            res.set_content("{\"error\": \"Invalid JSON\"}", "application/json");
        }
    });

    svr.listen("0.0.0.0", 8080);

    return 0;
}