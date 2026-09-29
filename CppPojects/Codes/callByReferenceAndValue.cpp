#include <iostream>
using namespace std;

void display(int a){
    a = a+5;
    cout<<"Inside Function: "<<a<<endl;
}
void displayA(int &a){
    a = a+4;
    cout<<"Inside Function: "<<a<<endl;
}

int main() {
    display(5);
    int x = 5;
    displayA(x);
    return 0;
}