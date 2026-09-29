#include <iostream>
using namespace std;

class X {
private:
    int a = 5;
    friend class Y;
};

class Y {
public:
    void show(X obj) {
        cout << obj.a << endl;
    }
};

class Box {
private:
    int length = 10;
    friend void show(Box);
};

void show(Box a) {
    cout << a.length << endl;
}

int main() {
    X objX;
    Y objY;
    objY.show(objX);

    Box b;
    show(b);

    return 0;
}
