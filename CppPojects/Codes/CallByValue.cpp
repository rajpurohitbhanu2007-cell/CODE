#include <iostream>
using namespace std;

void display(int a){
    a = a+5;
    cout<<"Inside Function: "<<a<<endl;
}

int main() {
    display(5);
    return 0;
}
    