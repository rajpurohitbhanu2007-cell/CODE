#include <iostream>
using namespace std;

int main() {
    int *p;
    p = new int;
    *p = 50;
    cout << "Value: " << *p << endl;
    delete p;
    p = nullptr;
    return 0;
}
