#include <iostream>
using namespace std;

int main() {
    int a = 10, b = 99;
    cout << "Initial values: a = " << a << ", b = " << b << endl;
    
    // Standard variable swap
    int temp = a;
    a = b;
    b = temp;
    
    cout << "Swapped values: a = " << a << ", b = " << b << endl;
    return 0;
}