#include <iostream>
using namespace std;

class Demo {
private: 
    int a; 
public:
    int b;
protected:
    int c;

public:
    void set() {
        a = 10; 
        b = 20; 
        c = 80;
    }
    void show() {
        cout << a << " " << b << " " << c << endl;
    }
};

class Child : public Demo {
public:
    void access() {
        b = 20; 
        c = 30;
    }
};

int main() {
    Demo d;
    d.set();
    d.show();
    
    d.b = 10;    
    
    cout << d.b;
    return 0;
}
