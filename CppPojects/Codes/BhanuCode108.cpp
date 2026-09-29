#include <iostream>
using namespace std;
class A{
    int a = 10;
    friend void display();
};
void display(){
    cout<<A.a;
}
int main() {

    cout << "Program";
    display();
    return 0;
}
